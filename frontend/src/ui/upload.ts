import type { Component, Netlist, Solution, OCRText } from "../types";
import type { GhostPart } from "./trace-issues";
import { t, format, digits } from "../i18n";
import { ImageStore } from "./image-store";
import { friendlyFilename } from "./filenames";

export type AnalysisResult = {
  netlist: Netlist;
  solution: Solution;
  provenance: "extracted" | "partial" | "demo_fallback";
  source_image: string;
  warnings: { code: string; ref: string | null; message_key: string }[];
  timings: { total?: number };
  regions?: { netlist: Netlist }[];
  diagnostics?: {
    texts: OCRText[];
    stages?: { stage: string; status: string }[];
    trace?: {
      budget_exceeded?: boolean;
      ghosts?: GhostPart[];
      terminals_floating?: number;
      terminals_snapped?: number;
    };
  };
  style_estimate?: {
    style: string;
    effective_style: string;
    confidence: number;
    override: boolean;
  };
};
const stages = [
  "received",
  "preprocess",
  "detect",
  "text",
  "wires",
  "validate",
  "resolve",
  "solve",
  "done",
];
const node = <K extends keyof HTMLElementTagNameMap>(
  tag: K,
  parent: HTMLElement,
  key?: string,
) => {
  const element = document.createElement(tag);
  parent.append(element);
  if (key) element.dataset.i18n = key;
  return element;
};

export class UploadWorkspace {
  private active = true;
  private file?: File;
  private url = "";
  private job = "";
  private generation = 0;
  private controller?: AbortController;
  private errorCode = "";
  private received = false;
  private index = -1;
  private elapsed = 0;
  private dimensions = "";
  private result?: AnalysisResult;
  private parts: Component[] = [];
  private image = new Image();
  private previewImages = new ImageStore();
  private partialImage = false;
  private releasePreview() {
    this.previewImages.clear();
    if (this.url) URL.revokeObjectURL(this.url);
    this.url = "";
    this.image.src = "";
    this.preview.removeAttribute("src");
    this.boxes.width = this.boxes.height = 1;
    this.partialImage = false;
  }
  private receipt: HTMLElement;
  private preview: HTMLImageElement;
  private boxes: HTMLCanvasElement;
  private stepper: HTMLOListElement;
  private clock: HTMLElement;
  private error: HTMLElement;
  private retry: HTMLButtonElement;
  private cancel: HTMLButtonElement;
  private page: HTMLInputElement;
  private summary: HTMLElement;
  private show: HTMLInputElement;
  private provenance: HTMLElement;
  constructor(
    parent: HTMLElement,
    private apply: (r: AnalysisResult, file: File) => void,
    private settings: () => Record<string, string>,
  ) {
    const card = node("section", parent);
    card.className = "upload-progress";
    const choose = node("button", card, "upload.choose");
    choose.onclick = () => document.getElementById("upload")!.click();
    this.receipt = node("p", card);
    this.receipt.dataset.testid = "upload-receipt";
    this.receipt.setAttribute("role", "status");
    const frame = node("div", card);
    frame.className = "upload-preview";
    this.preview = node("img", frame);
    this.preview.dataset.testid = "upload-preview";
    this.preview.hidden = true;
    this.boxes = node("canvas", frame);
    this.boxes.dataset.testid = "detected-preview";
    this.boxes.hidden = true;
    const toggle = node("label", card);
    toggle.className = "toggle";
    this.show = node("input", toggle);
    this.show.type = "checkbox";
    this.show.checked = true;
    this.show.dataset.testid = "show-detections";
    node("span", toggle, "upload.parts");
    this.show.onchange = () => this.draw();
    const pageLabel = node("label", card);
    node("span", pageLabel, "upload.page");
    this.page = node("input", pageLabel);
    this.page.type = "number";
    this.page.min = "1";
    this.page.value = "1";
    this.page.max = "1";
    this.page.dataset.testid = "pdf-page";
    pageLabel.hidden = true;
    this.page.onchange = () => {
      if (this.file) void this.start(this.file, Number(this.page.value) - 1);
    };
    this.stepper = node("ol", card);
    this.stepper.className = "stepper";
    this.stepper.dataset.testid = "analysis-stepper";
    this.stepper.hidden = true;
    stages.forEach((stage) => node("li", this.stepper, "stage." + stage));
    this.clock = node("p", card);
    this.clock.setAttribute("aria-live", "off");
    this.cancel = node("button", card, "upload.cancel");
    this.cancel.hidden = true;
    this.cancel.dataset.testid = "analysis-cancel";
    this.cancel.onclick = () => void this.stop();
    this.error = node("p", card);
    this.error.setAttribute("role", "alert");
    this.error.dataset.testid = "upload-error";
    this.retry = node("button", card, "upload.retry");
    this.retry.hidden = true;
    this.retry.onclick = () => {
      if (this.file) void this.start(this.file, Number(this.page.value) - 1);
    };
    this.summary = node("section", card);
    this.summary.dataset.testid = "result-summary";
    this.summary.className = "result-summary";
    this.provenance = document.createElement("div");
    this.provenance.id = "provenance";
    this.provenance.dataset.testid = "provenance-banner";
    this.provenance.className = "banner provenance example";
    this.provenance.setAttribute("role", "status");
    document.querySelector(".center")!.prepend(this.provenance);
    this.example();
    document.addEventListener("paste", (e) => {
      const file = Array.from(e.clipboardData?.files || []).find((f) =>
        f.type.startsWith("image/"),
      );
      if (file) void this.start(file);
    });
  }
  example() {
    document.dispatchEvent(new Event("workspace:example"));
    this.result = undefined;
    this.provenance.className = "banner provenance example";
    this.provenance.textContent = t("upload.example");
  }
  translate() {
    this.preview.alt = t("upload.preview");
    this.boxes.setAttribute("aria-label", t("upload.parts"));
    this.receipt.textContent =
      this.received && this.file
        ? `${t("upload.received")} · ${friendlyFilename(this.file.name)}${this.file.name.match(/\.[a-z0-9]{1,6}$/i)?.[0] || ""} · ${format(this.file.size / 1024, "KB")}${this.dimensions ? " · " + digits(this.dimensions) : ""}`
        : "";
    this.receipt.title = this.file?.name || "";
    this.error.textContent = this.errorCode ? t("error." + this.errorCode) : "";
    if (this.index >= 0)
      this.clock.textContent = t("upload.elapsed", {
        time: format(this.elapsed, "s"),
      });
    if (this.result) this.renderResult();
    else this.provenance.textContent = t("upload.example");
  }
  private async stop() {
    const previous = this.job;
    ++this.generation;
    this.controller?.abort();
    this.job = "";
    this.cancel.hidden = true;
    this.stepper.hidden = true;
    this.releasePreview();
    this.errorCode = "cancelled";
    this.retry.hidden = false;
    this.setBusy(false);
    this.translate();
    if (previous)
      void fetch("/api/analyze/" + previous, { method: "DELETE" }).catch(
        () => {},
      );
  }
  setActive(active: boolean) {
    this.active = active;
    if (!active && !this.cancel.hidden) void this.stop();
  }
  async start(file: File, page = 0) {
    if (!this.active) return;
    document.dispatchEvent(new Event("workspace:importing"));
    this.stopPrevious();
    const generation = ++this.generation;
    this.file = file;
    this.received = true;
    this.errorCode = "";
    this.retry.hidden = true;
    this.parts = [];
    this.dimensions = "";
    this.page.value = String(page + 1);
    this.index = 0;
    this.elapsed = 0;
    this.setBusy(true);
    this.releasePreview();
    this.url = URL.createObjectURL(file);
    this.preview.src = this.url;
    this.preview.hidden = file.type === "application/pdf";
    this.preview.onload = () => {
      if (this.preview.src === this.url)
        this.dimensions = `${this.preview.naturalWidth} × ${this.preview.naturalHeight}`;
      this.translate();
    };
    this.translate();
    if (file.size > 20 * 1024 * 1024) return this.fail("too_large");
    if (!/\.(png|jpe?g|webp|heic|heif|pdf)$/i.test(file.name))
      return this.fail("unsupported_type");
    this.stepper.hidden = false;
    this.cancel.hidden = false;
    this.setStage(0);
    const controller = new AbortController();
    this.controller = controller;
    const timeout = window.setTimeout(
      () => controller.abort("timeout"),
      120000,
    );
    try {
      const data = new FormData();
      data.append("image", file);
      data.append("page", String(page));
      Object.entries(this.settings()).forEach(([k, v]) => data.append(k, v));
      const response = await fetch("/api/analyze/start", {
        method: "POST",
        body: data,
        signal: controller.signal,
      });
      const started = await response.json();
      if (!response.ok) throw new Error(started.detail?.code || "server_error");
      if (generation !== this.generation) {
        void fetch("/api/analyze/" + started.job_id, {
          method: "DELETE",
        }).catch(() => {});
        return;
      }
      this.job = started.job_id;
      if (
        Array.isArray(started.stages) &&
        started.stages.length >= 2 &&
        started.stages.every((stage: unknown) => typeof stage === "string")
      ) {
        this.stepper.replaceChildren();
        started.stages.forEach((stage: string) =>
          node("li", this.stepper, "stage." + stage),
        );
      }
      this.page.max = String(started.page_count || 1);
      this.page.parentElement!.hidden = (started.page_count || 1) <= 1;
      if (!this.dimensions)
        this.dimensions = `${started.width} × ${started.height}`;
      this.translate();
      while (generation === this.generation) {
        const response = await fetch("/api/analyze/" + this.job, {
          signal: controller.signal,
          headers: { "X-Include-Image": String(!this.partialImage) },
        });
        const job = await response.json();
        if (generation !== this.generation) return;
        if (!response.ok) throw Error(job.detail?.code || "server_error");
        this.elapsed = job.elapsed_seconds;
        this.setStage(job.stage_index);
        if (job.stage === "queued")
          this.clock.textContent = t("upload.stage.queued");
        if (job.partial?.source_image && !this.partialImage) {
          const url = this.previewImages.fromData(job.partial.source_image);
          this.partialImage = true;
          this.image.src = url;
          this.preview.src = url;
          this.preview.hidden = false;
          this.image.onload = () => this.draw();
        }
        if (job.partial?.components) {
          this.parts = job.partial.components;
          this.draw();
        }
        if (job.error) throw Error(job.error.code);
        if (job.result) {
          this.result = job.result;
          this.apply(job.result, file);
          this.previewImages.clear();
          this.image.src = job.result.source_image || this.url;
          this.preview.src = job.result.source_image || this.url;
          this.boxes.width = this.boxes.height = 1;
          this.renderResult();
          document.dispatchEvent(
            new CustomEvent("workspace:imported", {
              detail: {
                name: file.name,
                parts: job.result.netlist.components.length,
                original:
                  file.type === "application/pdf"
                    ? job.result.source_image
                    : this.url,
              },
            }),
          );
          break;
        }
        await new Promise((resolve) => setTimeout(resolve, 400));
      }
    } catch (error) {
      if (generation === this.generation) {
        if (this.job)
          void fetch("/api/analyze/" + this.job, { method: "DELETE" }).catch(
            () => {},
          );
        this.fail(
          controller.signal.aborted
            ? "timeout"
            : error instanceof TypeError
              ? "network"
              : (error as Error).message,
        );
      }
    } finally {
      clearTimeout(timeout);
      if (generation === this.generation) {
        this.cancel.hidden = true;
        this.job = "";
        this.setBusy(false);
      }
    }
  }
  private stopPrevious() {
    this.controller?.abort();
    if (this.job) {
      const id = this.job;
      this.job = "";
      ++this.generation;
      this.controller?.abort();
      void fetch("/api/analyze/" + id, { method: "DELETE" }).catch(() => {});
    }
  }
  private setBusy(busy: boolean) {
    const frame = this.preview.parentElement!;
    frame.classList.toggle("loading", busy);
    frame.setAttribute("aria-busy", String(busy));
  }
  private fail(code: string) {
    this.errorCode = [
      "unsupported_type",
      "too_large",
      "undecodable",
      "invalid_page",
      "busy",
      "rate_limited",
      "expired",
      "cancelled",
      "timeout",
      "network",
    ].includes(code)
      ? code
      : "server_error";
    this.cancel.hidden = true;
    this.stepper.hidden = true;
    this.retry.hidden = false;
    this.setBusy(false);
    this.translate();
  }
  private setStage(index: number) {
    this.index = index;
    Array.from(this.stepper.children).forEach((el, i) => {
      el.className = i < index ? "complete" : i === index ? "current" : "";
      if (i === index) el.setAttribute("aria-current", "step");
      else el.removeAttribute("aria-current");
    });
    this.translate();
  }
  private draw() {
    this.boxes.hidden = !this.show.checked || !this.parts.length;
    if (!this.image.naturalWidth) return;
    this.boxes.width = this.image.naturalWidth;
    this.boxes.height = this.image.naturalHeight;
    const ctx = this.boxes.getContext("2d")!;
    ctx.strokeStyle = "#0072b2";
    ctx.fillStyle = "#003a5c";
    ctx.lineWidth = 2;
    ctx.font = "14px sans-serif";
    for (const c of this.parts) {
      const [x, y, x2, y2] = c.bbox;
      ctx.strokeRect(x, y, x2 - x, y2 - y);
      ctx.fillText(
        `${t("type." + c.type)} ${Math.round(c.confidence * 100)}%`,
        x,
        Math.max(14, y - 4),
      );
    }
  }
  private renderResult() {
    const r = this.result!;
    const counts = { given: 0, solved: 0, assumed: 0, user: 0 };
    r.netlist.components.forEach((c) => counts[c.value.status]++);
    const confidence = r.netlist.components.length
      ? r.netlist.components.reduce((s, c) => s + c.confidence, 0) /
        r.netlist.components.length
      : 0;
    this.summary.replaceChildren();
    const summary = node("p", this.summary);
    summary.textContent = t("upload.summary", {
      parts: digits(String(r.netlist.components.length)),
      nodes: digits(String(r.netlist.nodes.length)),
      given: digits(String(counts.given)),
      solved: digits(String(counts.solved)),
      assumed: digits(String(counts.assumed)),
      confidence: digits(String(Math.round(confidence * 100))),
      time: format(r.timings.total || this.elapsed, "s"),
    });
    node("p", this.summary).textContent = [
      ...new Set(r.netlist.components.map((c) => t("type." + c.type))),
    ].join(" · ");
    if (r.warnings.some((w) => w.code === "image_edge_cut")) {
      const edge = node("p", this.summary, "warn.image_edge_cut");
      edge.className = "image-edge-notice";
      edge.textContent = t("warn.image_edge_cut");
    }
    const style = r.style_estimate;
    if (style)
      node("p", this.summary).textContent = t(
        style.override ? "style.overridden" : "style.estimated",
        {
          style: t("style." + style.effective_style),
          confidence: digits(String(Math.round(style.confidence * 100))),
        },
      );
    const details = node("details", this.summary);
    const grouped = new Map<
      string,
      { key: string; count: number; ref: string | null }
    >();
    for (const warning of r.warnings) {
      const group = grouped.get(warning.code) || {
        key: warning.message_key,
        count: 0,
        ref: warning.ref,
      };
      group.count++;
      grouped.set(warning.code, group);
    }
    node("summary", details).textContent =
      t("edit.details") + " (" + grouped.size + ")";
    for (const w of grouped.values()) {
      const line = node("p", details);
      line.textContent = t(w.key) + " (" + digits(String(w.count)) + ") ";
      const fix = node("button", line, "upload.fix");
      fix.onclick = () => {
        if (!document.getElementById("app")!.classList.contains("editing"))
          document.getElementById("edit")!.click();
        document.dispatchEvent(
          new CustomEvent("circuit:fix", { detail: { ref: w.ref } }),
        );
      };
    }
    const provenance = r.provenance || "demo_fallback";
    this.provenance.className = "banner provenance " + provenance;
    this.provenance.textContent = t("provenance." + provenance);
    if (r.warnings.some((w) => w.code === "detector_unavailable"))
      this.provenance.textContent += " " + t("error.missing_weights");
    if (r.diagnostics?.trace?.budget_exceeded)
      this.provenance.textContent += " " + t("upload.tracing_incomplete");
    if (
      r.diagnostics?.stages?.some((s) =>
        ["timeout", "limited"].includes(s.status),
      )
    )
      this.provenance.textContent += " " + t("upload.ocr_timeout");
    if (
      provenance !== "demo_fallback" &&
      r.netlist.components.some((c) => c.value.status === "assumed")
    )
      this.provenance.textContent += " " + t("upload.assumed_values");
    const dropped = r.netlist.components
      .filter((c) => c.disabled)
      .map((c) => c.id);
    if (dropped.length)
      this.provenance.textContent +=
        " " + t("upload.dropped", { parts: dropped.join(", ") });
    document.getElementById("overlay")!.dataset.provenance = provenance;
  }
}
