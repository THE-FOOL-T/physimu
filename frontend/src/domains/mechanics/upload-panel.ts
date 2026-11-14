import { t, format } from "../../shell";
import { friendlyFilename } from "../../shell/filenames";
import {
  AnalysisStepper,
  createAnalysisPreview,
  type AnalysisStepState,
} from "../../shell/analysis-ui";
import type { Scene } from "./types";
import type {
  AnalysisProgress,
  MechanicsResult,
  DetectionBox,
  OCRReading,
} from "./analysis";

const stages = [
  "received",
  "preprocess",
  "understand",
  "detect",
  "text",
  "geometry",
  "associate",
  "archetype",
  "validate",
  "build",
  "done",
];
export type SourceKind = "empty" | "upload" | "sample" | "project";
const node = <K extends keyof HTMLElementTagNameMap>(
  tag: K,
  parent: HTMLElement,
  key?: string,
) => {
  const item = document.createElement(tag);
  parent.append(item);
  if (key) {
    item.dataset.i18n = key;
    item.textContent = t(key);
  }
  return item;
};

export function componentName(scene: Scene, id: string) {
  const named = scene.annotations.find((a) => a.id === `name_${id}`)?.geometry
    .text;
  if (named) return named;
  const object = [
    ...scene.bodies,
    ...scene.links,
    ...scene.surfaces,
    ...scene.pulleys,
  ].find((o) => o.id === id);
  if (id === "pivot") return t("mech.component_pivot");
  const type =
    object && "type" in object
      ? object.type
      : scene.pulleys.some((p) => p.id === id)
        ? "pulley"
        : "object";
  const key = `mech.component_${type}`;
  return t(key) === key ? t("mech.component_object") : t(key);
}

/** Receipts, genuine stage states and evidence. Physics stays in BindingEngine. */
export class MechanicsUploadPanel {
  readonly preview: ReturnType<typeof createAnalysisPreview>;
  readonly stepper: AnalysisStepper;
  readonly banner: HTMLElement;
  private receipt: HTMLElement;
  private style: HTMLElement;
  private evidence: HTMLElement;
  private retry: HTMLButtonElement;
  private states = new Map<string, AnalysisStepState>();
  private boxes: DetectionBox[] = [];
  private texts: OCRReading[] = [];
  private geometry: Scene | null = null;
  private currentFile?: File;
  private imageVersion = 0;
  private dimensions = "";
  private bannerText = () => "";
  private styleText = () => "";
  private status: HTMLElement;
  private candidates: HTMLElement;
  private candidateEvidence?: NonNullable<
    MechanicsResult["diagnostics"]
  >["classical"];
  sourceKind: SourceKind = "empty";
  sourceName = "";
  recognitionMethod = "";
  constructor(
    parent: HTMLElement,
    center: HTMLElement,
    input: HTMLInputElement,
    analysis: HTMLElement,
    private actions: {
      upload(file: File): void;
      retry(): void;
      confirmCandidate(index: number): void;
    },
  ) {
    const card = node("section", parent);
    card.className = "upload-progress mech-upload";
    parent.prepend(card);
    const drop = node("button", card);
    drop.type = "button";
    drop.className = "dropzone";
    drop.dataset.testid = "mechanics-dropzone";
    node("strong", drop, "mech.drop_diagram");
    node("span", drop, "mech.drop_formats");
    drop.onclick = () => input.click();
    for (const name of ["dragenter", "dragover"])
      drop.addEventListener(name, (event) => {
        event.preventDefault();
        drop.classList.add("drag");
      });
    drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
    drop.addEventListener("drop", (event) => {
      event.preventDefault();
      drop.classList.remove("drag");
      const file = event.dataTransfer?.files[0];
      if (file) actions.upload(file);
    });
    const originalLabel = input.parentElement!;
    input.hidden = true;
    input.setAttribute("aria-label", t("mech.upload_image"));
    card.append(input);
    originalLabel.remove();
    this.receipt = node("p", card);
    this.receipt.dataset.testid = "mechanics-upload-receipt";
    this.receipt.setAttribute("role", "status");
    this.preview = createAnalysisPreview(
      card,
      "mechanics-source-preview",
      "mechanics-detected-preview",
    );
    this.preview.image.alt = t("upload.preview");
    this.style = node("p", card);
    this.style.dataset.testid = "mechanics-style-estimate";
    const list = node("ol", card);
    list.dataset.testid = "mechanics-analysis-stepper";
    list.hidden = true;
    this.stepper = new AnalysisStepper(list, "mech.stage_");
    this.stepper.stages(stages);
    card.append(analysis);
    this.status = analysis.querySelector(
      '[data-testid="mechanics-analysis-status"]',
    )!;
    this.retry = node("button", card, "upload.retry");
    this.retry.type = "button";
    this.retry.dataset.testid = "mechanics-retry";
    this.retry.hidden = true;
    this.retry.onclick = actions.retry;
    this.candidates = node("section", card);
    this.candidates.dataset.testid = "mechanics-pendulum-candidates";
    const details = node("details", card);
    node("summary", details, "mech.analysis_evidence");
    this.evidence = node("div", details);
    this.evidence.dataset.testid = "mechanics-analysis-evidence";
    this.banner = node("div", center);
    this.banner.className = "banner provenance example";
    this.banner.dataset.testid = "mechanics-source-identity";
    this.banner.setAttribute("role", "status");
    center.prepend(this.banner);
  }
  private updateSteps() {
    this.stepper.update([...this.states.values()]);
    for (const item of this.stepper.element.querySelectorAll<HTMLElement>(
      "[data-i18n]",
    ))
      item.textContent = t(item.dataset.i18n!);
  }
  translate() {
    this.banner.textContent = this.bannerText();
    this.style.textContent = this.styleText();
    this.receipt.textContent = `${this.currentFile ? `${t("upload.received")} · ${friendlyFilename(this.currentFile.name)} · ${format(this.currentFile.size / 1024, "KB")}` : ""}${this.dimensions ? ` · ${this.dimensions}` : ""}`;
    this.updateSteps();
    this.renderEvidence();
    this.draw();
  }
  reset(kind: SourceKind, name: string, file?: File) {
    this.sourceKind = kind;
    this.sourceName = name;
    this.recognitionMethod = "";
    this.boxes = [];
    this.texts = [];
    this.geometry = null;
    this.currentFile = file;
    this.candidates.replaceChildren();
    this.candidateEvidence = undefined;
    this.dimensions = "";
    this.imageVersion++;
    this.receipt.textContent = file
      ? `${t("upload.received")} · ${friendlyFilename(file.name)} · ${format(file.size / 1024, "KB")}`
      : "";
    this.receipt.title = file?.name ?? name;
    this.preview.image.hidden = true;
    this.preview.canvas.hidden = true;
    this.states = new Map(stages.map((id) => [id, { id, status: "pending" }]));
    this.stepper.element.hidden = true;
    this.retry.hidden = true;
    this.styleText = () => "";
    this.evidence.replaceChildren();
    this.banner.className =
      "banner provenance " + (kind === "sample" ? "example" : "partial");
    this.bannerText = () =>
      `${t(`mech.source_${kind}`)}${name ? ` · ${friendlyFilename(name)}` : ""}`;
    this.translate();
  }
  get debug() {
    return {
      sourceKind: this.sourceKind,
      sourceName: this.sourceName,
      method: this.recognitionMethod,
      stages: [...this.states.values()],
      detections: this.boxes,
      texts: this.texts,
      geometry: this.geometry,
    };
  }
  async source(url: string, width: number, height: number, file?: File) {
    const version = ++this.imageVersion;
    this.currentFile = file ?? this.currentFile;
    this.dimensions = `${width} × ${height}`;
    this.receipt.textContent = `${this.currentFile ? `${t("upload.received")} · ${friendlyFilename(this.currentFile.name)} · ${format(this.currentFile.size / 1024, "KB")} · ` : ""}${width} × ${height}`;
    this.preview.image.src = url;
    this.preview.image.hidden = false;
    try {
      await this.preview.image.decode();
    } catch {
      return;
    }
    if (version === this.imageVersion) this.draw();
  }
  start(retained = false) {
    this.stepper.element.hidden = false;
    this.retry.hidden = true;
    this.states = new Map(stages.map((id) => [id, { id, status: "pending" }]));
    this.bannerText = () =>
      `${t(retained ? "mech.reanalyzing_retained" : "mech.analyzing_source")} · ${friendlyFilename(this.sourceName)}`;
    this.banner.textContent = this.bannerText();
    this.banner.className = "banner provenance partial";
    this.updateSteps();
  }
  progress(job: AnalysisProgress) {
    const explicit = job.partial?.stage_states;
    if (explicit) {
      for (const state of explicit)
        if (state.id !== "done") this.states.set(state.id, state);
    } else {
      // History is actual server execution, not an index-based guess at skipped work.
      for (const id of job.history ?? [])
        if (id !== "queued" && id !== "done" && this.states.has(id))
          this.states.set(id, {
            id,
            status: id === job.stage ? "running" : "completed",
          });
      if (job.stage !== "done" && this.states.has(job.stage))
        this.states.set(job.stage, { id: job.stage, status: "running" });
    }
    if (job.partial?.detections) this.boxes = job.partial.detections;
    if (job.partial?.texts) this.texts = job.partial.texts;
    if (job.partial?.scene_evidence) this.geometry = job.partial.scene_evidence;
    this.updateSteps();
    this.draw();
    this.renderEvidence();
  }
  compiled(result: MechanicsResult) {
    this.candidates.replaceChildren();
    const classical = result.diagnostics?.classical;
    this.candidateEvidence = classical;
    if (
      classical &&
      !classical.accepted &&
      classical.reason === "ambiguous_pendulum_candidates"
    ) {
      node("p", this.candidates, "mech.confirm_pendulum_candidate");
      for (const [index, candidate] of classical.candidates.entries()) {
        const button = node("button", this.candidates);
        button.type = "button";
        button.textContent = `${t("mech.pendulum_candidate")} ${index + 1} · ${Math.round(candidate.confidence * 100)}%`;
        button.onclick = () => this.actions.confirmCandidate(index);
      }
    }
    for (const state of Object.values(result.diagnostics?.stage_states ?? {}))
      if (state.id !== "done") this.states.set(state.id, state);
    this.boxes = result.diagnostics?.detections ?? this.boxes;
    this.texts = result.diagnostics?.texts ?? this.texts;
    this.geometry = result.scene;
    this.recognitionMethod = result.diagnostics?.recognition?.method ?? "";
    this.states.set("build", { id: "build", status: "running" });
    const style = result.style_estimate;
    if (style)
      this.styleText = () =>
        `${t("mech.diagram_style")}: ${t(`mech.${style.effective_style}`)} · ${Math.round(style.confidence * 100)}%`;
    const method = this.recognitionMethod.includes("classical")
      ? "classical_method"
      : this.recognitionMethod === "model"
        ? "model_method"
        : "unresolved_method";
    const system =
      result.scene.archetype === "pendulum"
        ? "simple_pendulum"
        : result.scene.archetype;
    this.bannerText = () =>
      `${t("mech.recognized_system")}: ${t(`mech.${system}`)} · ${t(`mech.${method}`)}${result.diagnostics?.recognition?.model_status === "unavailable" ? ` · ${t("mech.model_unavailable_fallback")}` : ""}`;
    this.banner.className =
      "banner provenance " +
      (result.scene.archetype === "unsupported" ? "demo_fallback" : "partial");
    this.translate();
  }
  simulationReady(supported: boolean) {
    if (
      !this.states.get("build") ||
      !["running", "blocked"].includes(this.states.get("build")!.status)
    )
      return;
    this.states.set("build", {
      id: "build",
      status: supported ? "completed" : "blocked",
    });
    this.states.set("done", {
      id: "done",
      status: supported ? "completed" : "blocked",
    });
    this.status.textContent = t(
      supported ? "mech.simulation_ready" : "mech.correction_required",
    );
    this.retry.hidden = supported || !this.currentFile;
    this.updateSteps();
  }
  failed() {
    for (const state of this.states.values())
      if (state.status === "running") state.status = "failed";
    this.states.set("done", { id: "done", status: "blocked" });
    this.retry.hidden = false;
    this.updateSteps();
  }
  private renderEvidence() {
    this.evidence.replaceChildren();
    node("p", this.evidence).textContent =
      `${this.boxes.length} ${t("mech.components_found")} · ${this.texts.length} ${t("mech.labels_found")}`;
    for (const reading of this.texts)
      for (const candidate of [reading, ...(reading.alternatives ?? [])])
        node("p", this.evidence).textContent =
          `${candidate.text}${candidate.confidence !== undefined ? ` · ${Math.round(candidate.confidence * 100)}%` : ""} · ${candidate.engine ?? candidate.source ?? "OCR"}${candidate.rotation !== undefined ? ` · ${candidate.rotation}°` : ""}${candidate.binding_eligible === false ? ` · ${t("mech.ocr_orientation_excluded")}` : ""}`;
    for (const step of this.states.values())
      if (step.reason)
        node("p", this.evidence).textContent =
          `${t(`mech.stage_${step.id}`)}: ${t(`mech.${step.reason}`) === `mech.${step.reason}` ? step.reason : t(`mech.${step.reason}`)}`;
    for (const link of this.geometry?.links ?? [])
      node("p", this.evidence).textContent =
        `${componentName(this.geometry!, link.id)} ↔ ${componentName(this.geometry!, link.a.ref)}, ${componentName(this.geometry!, link.b.ref)}`;
  }
  paint(ctx: CanvasRenderingContext2D) {
    ctx.save();
    ctx.font = "13px sans-serif";
    ctx.lineWidth = 2;
    if (this.candidateEvidence && !this.candidateEvidence.accepted) {
      const scale = this.candidateEvidence.native_scale;
      ctx.strokeStyle = ctx.fillStyle = "#ab5700";
      for (const [
        index,
        candidate,
      ] of this.candidateEvidence.candidates.entries()) {
        const [x, y] = candidate.bob.center.map((v) => v * scale);
        ctx.beginPath();
        ctx.arc(x, y, candidate.bob.radius * scale + 5, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillText(`${index + 1}`, x + candidate.bob.radius * scale + 8, y);
      }
    }
    for (const box of this.boxes) {
      ctx.strokeStyle =
        box.source === "classical_vision" ? "#b56500" : "#0072b2";
      ctx.fillStyle = ctx.strokeStyle;
      const [x, y, z, v] = box.bbox;
      ctx.strokeRect(x, y, z - x, v - y);
      const key = `mech.component_${box.type}`;
      ctx.fillText(
        `${t(key) === key ? box.type : t(key)} ${Math.round(box.confidence * 100)}%`,
        x,
        Math.max(14, y - 5),
      );
    }
    ctx.strokeStyle = "#18764c";
    for (const reading of this.texts) {
      const [x, y, z, v] = reading.bbox;
      ctx.strokeRect(x, y, z - x, v - y);
    }
    ctx.strokeStyle = "#ab5700";
    ctx.setLineDash([6, 4]);
    for (const link of this.geometry?.links ?? []) {
      ctx.beginPath();
      link.polyline.forEach((p, i) =>
        i ? ctx.lineTo(...p) : ctx.moveTo(...p),
      );
      ctx.stroke();
    }
    ctx.restore();
  }
  private draw() {
    const image = this.preview.image,
      canvas = this.preview.canvas;
    if (!image.naturalWidth) return;
    canvas.width = image.naturalWidth;
    canvas.height = image.naturalHeight;
    canvas.hidden = !(
      this.boxes.length ||
      this.texts.length ||
      this.geometry?.links.length ||
      this.candidateEvidence?.candidates.length
    );
    this.paint(canvas.getContext("2d")!);
  }
}
