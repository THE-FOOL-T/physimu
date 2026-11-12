import type { Netlist, OCRText } from "../types";
import { Renderer, canvasToImage } from "../overlay/renderer";
import { format, t } from "../i18n";

type Actions = {
  net: () => Netlist;
  selected: () => string;
  apply: (id: string, number: number, unit: string) => void;
  optIn: () => boolean;
  notify: (message: string) => void;
};
const element = <K extends keyof HTMLElementTagNameMap>(
  tag: K,
  parent: HTMLElement,
  key?: string,
) => {
  const node = document.createElement(tag);
  parent.append(node);
  if (key) {
    node.dataset.i18n = key;
    node.textContent = t(key);
  }
  return node;
};

export class TextInspector {
  private reading = false;
  private start?: [number, number];
  private rect = document.createElement("div");
  private dialog = document.createElement("div");
  private readButton: HTMLButtonElement;
  private abort?: AbortController;
  private ignoreClick = false;
  private current?: OCRText;
  constructor(
    private renderer: Renderer,
    private actions: Actions,
  ) {
    const toolbar = document.querySelector<HTMLElement>(".canvas-toolbar")!;
    const label = element("label", toolbar);
    label.className = "toggle";
    const toggle = element("input", label);
    toggle.type = "checkbox";
    toggle.dataset.testid = "show-text";
    element("span", label, "ocr.show");
    toggle.onchange = () => (renderer.showText = toggle.checked);
    this.readButton = element("button", toolbar, "ocr.read_area");
    this.readButton.dataset.testid = "ocr-read-area";
    this.readButton.onclick = () => {
      this.reading = !this.reading;
      this.readButton.classList.toggle("active", this.reading);
      if (this.reading) actions.notify(t("ocr.drag_hint"));
    };
    document.addEventListener("circuit:tool", (event) => {
      if ((event as CustomEvent<string>).detail !== "read") {
        this.reading = false;
        this.start = undefined;
        this.rect.hidden = true;
        this.readButton.classList.remove("active");
      }
    });
    this.dialog.className = "text-popover";
    this.dialog.hidden = true;
    this.dialog.dataset.testid = "text-popover";
    this.dialog.setAttribute("role", "dialog");
    this.dialog.setAttribute("aria-label", t("ocr.found"));
    document.body.append(this.dialog);
    this.rect.className = "ocr-selection";
    this.rect.hidden = true;
    document.body.append(this.rect);
    const canvas = renderer.canvas;
    canvas.addEventListener(
      "pointerdown",
      (event) => {
        if (!this.reading) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        this.start = this.position(event);
        canvas.setPointerCapture(event.pointerId);
      },
      true,
    );
    canvas.addEventListener(
      "pointermove",
      (event) => {
        if (this.start && this.reading) {
          event.preventDefault();
          event.stopImmediatePropagation();
          const a = this.screen(this.start),
            b = this.screen(this.position(event));
          this.rect.hidden = false;
          Object.assign(this.rect.style, {
            left: Math.min(a[0], b[0]) + "px",
            top: Math.min(a[1], b[1]) + "px",
            width: Math.abs(a[0] - b[0]) + "px",
            height: Math.abs(a[1] - b[1]) + "px",
          });
        }
      },
      true,
    );
    canvas.addEventListener(
      "pointerup",
      (event) => {
        if (!this.reading || !this.start) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        this.ignoreClick = true;
        setTimeout(() => (this.ignoreClick = false), 0);
        const end = this.position(event),
          start = this.start;
        this.start = undefined;
        this.rect.hidden = true;
        this.reading = false;
        this.readButton.classList.remove("active");
        if (canvas.hasPointerCapture(event.pointerId))
          canvas.releasePointerCapture(event.pointerId);
        void this.readCrop(start, end);
      },
      true,
    );
    canvas.addEventListener(
      "click",
      (event) => {
        if (this.reading || this.ignoreClick) {
          event.preventDefault();
          event.stopImmediatePropagation();
          return;
        }
        const [x, y] = this.position(event),
          item = renderer.textHit(x, y);
        if (item) {
          event.preventDefault();
          event.stopImmediatePropagation();
          this.open(item);
        }
      },
      true,
    );
    canvas.addEventListener(
      "mousemove",
      (event) => {
        const [x, y] = this.position(event),
          item = renderer.textHit(x, y);
        if (item) {
          canvas.title = this.description(item);
          event.stopImmediatePropagation();
        }
      },
      true,
    );
    document.addEventListener("keydown", (event) => {
      if (canvas.closest("[inert]")) return;
      if (event.key === "Escape") {
        this.close();
        this.reading = false;
        this.start = undefined;
        this.rect.hidden = true;
        this.readButton.classList.remove("active");
      }
      if (
        event.key.toLowerCase() === "t" &&
        !event.ctrlKey &&
        !event.metaKey &&
        !(event.target instanceof HTMLInputElement) &&
        !(event.target instanceof HTMLTextAreaElement) &&
        !(event.target instanceof HTMLSelectElement)
      ) {
        event.preventDefault();
        this.readButton.click();
      }
    });
  }
  setTexts(texts: OCRText[]) {
    this.renderer.texts = structuredClone(texts);
  }
  reset() {
    this.abort?.abort();
    this.renderer.texts = [];
    this.close();
    this.rect.hidden = true;
    this.start = undefined;
    this.reading = false;
  }
  corrections() {
    return this.renderer.texts
      .filter((item) => item.user_confirmed)
      .map((item) => ({
        bbox: item.bbox,
        text: item.text,
        component_id: item.assigned_to || null,
        ignored: item.outcome === "ignored",
      }));
  }
  translate() {
    if (!this.dialog.hidden && this.current) this.open(this.current);
  }
  private position(event: MouseEvent | PointerEvent): [number, number] {
    return this.renderer.clientToImage(
      event.clientX,
      event.clientY,
      this.actions.net(),
    );
  }
  private screen(xy: [number, number]): [number, number] {
    return this.renderer.imageToScreen(xy, this.actions.net());
  }
  private description(item: OCRText) {
    const p = item.parsed;
    return `${item.text} → ${p?.number != null ? format(p.number, p.unit || "") : t("ocr.no_reading")} → ${t("ocr.reason." + (item.reason || "not_selected"))}`;
  }
  private close() {
    this.dialog.hidden = true;
    this.current = undefined;
  }
  open(item: OCRText, candidates: OCRText[] = []) {
    this.current = item;
    this.dialog.replaceChildren();
    this.dialog.hidden = false;
    element("strong", this.dialog, "ocr.found");
    element("p", this.dialog).textContent = this.description(item);
    if (item.engine)
      element("p", this.dialog).textContent = [
        item.raw_text || item.text,
        item.engine,
        item.rotation == null ? "" : `${item.rotation}°`,
      ]
        .filter(Boolean)
        .join(" · ");
    const targetLabel = element("label", this.dialog);
    element("span", targetLabel, "ocr.use");
    const target = element("select", targetLabel);
    target.dataset.testid = "ocr-target";
    for (const c of this.actions.net().components) {
      const option = element("option", target);
      option.value = c.id;
      option.textContent = c.id + " · " + t("type." + c.type);
    }
    target.value =
      item.assigned_to ||
      this.actions.selected() ||
      target.options[0]?.value ||
      "";
    const valueLabel = element("label", this.dialog);
    element("span", valueLabel, "value");
    const number = element("input", valueLabel);
    number.type = "number";
    number.step = "any";
    number.dataset.testid = "ocr-value";
    number.value =
      item.parsed?.number != null ? String(item.parsed.number) : "";
    const unitLabel = element("label", this.dialog);
    element("span", unitLabel, "ocr.unit");
    const unit = element("select", unitLabel);
    unit.dataset.testid = "ocr-unit";
    for (const name of ["ohm", "V", "A", "F", "H"]) {
      const option = element("option", unit);
      option.value = name;
      option.textContent = name === "ohm" ? "Ω" : name;
    }
    const updateUnit = () => {
      unit.value =
        this.actions.net().components.find((c) => c.id === target.value)?.value
          .unit || "ohm";
    };
    updateUnit();
    target.onchange = updateUnit;
    if (item.parsed?.unit) unit.value = item.parsed.unit;
    if (!candidates.length && item.alternatives?.length)
      candidates = item.alternatives.map((candidate) => ({
        ...candidate,
        bbox: candidate.bbox || item.bbox,
      }));
    if (candidates.length) {
      element("p", this.dialog, "ocr.choose");
      for (const candidate of candidates) {
        const button = element("button", this.dialog);
        button.textContent = [candidate.text, candidate.engine]
          .filter(Boolean)
          .join(" · ");
        button.onclick = () => {
          number.value =
            candidate.parsed?.number != null
              ? String(candidate.parsed.number)
              : "";
          if (candidate.parsed?.unit) unit.value = candidate.parsed.unit;
          item.raw_text ??= item.text;
          item.text = candidate.text;
        };
      }
    }
    const apply = element("button", this.dialog, "ocr.apply");
    apply.className = "primary";
    apply.dataset.testid = "ocr-apply";
    const submit = () => {
      if (
        !target.value ||
        number.value === "" ||
        !Number.isFinite(number.valueAsNumber)
      ) {
        number.focus();
        return;
      }
      this.actions.apply(target.value, number.valueAsNumber, unit.value);
      item.raw_text ??= item.text;
      item.text = number.value + " " + unit.value;
      item.assigned_to = target.value;
      item.parsed = { number: number.valueAsNumber, unit: unit.value };
      item.outcome = "assigned";
      item.reason = "assigned";
      item.user_confirmed = true;
      if (!this.renderer.texts.includes(item)) this.renderer.texts.push(item);
      this.close();
    };
    apply.onclick = submit;
    number.onkeydown = (event) => {
      if (event.key === "Enter") submit();
    };
    const ignore = element("button", this.dialog, "ocr.ignore");
    ignore.onclick = () => {
      item.outcome = "ignored";
      item.reason = "ignored";
      item.assigned_to = undefined;
      item.user_confirmed = true;
      this.close();
    };
    const close = element("button", this.dialog, "ocr.close");
    close.onclick = () => this.close();
    const [left, top] = this.screen([item.bbox[0], item.bbox[1]]),
      [right, bottom] = this.screen([item.bbox[2], item.bbox[3]]);
    const width = Math.min(300, innerWidth - 24);
    this.dialog.style.width = width + "px";
    const x =
      right + width + 12 < innerWidth
        ? right + 8
        : left - width - 8 > 8
          ? left - width - 8
          : Math.max(8, innerWidth - width - 8);
    const y =
      right + width + 12 < innerWidth || left - width - 8 > 8
        ? top
        : bottom + 8;
    Object.assign(this.dialog.style, {
      left: Math.max(8, x) + "px",
      top:
        Math.max(8, Math.min(innerHeight - this.dialog.offsetHeight - 8, y)) +
        "px",
    });
    number.focus();
  }
  private async readCrop(a: [number, number], b: [number, number]) {
    const net = this.actions.net();
    const x = Math.max(0, Math.floor(Math.min(a[0], b[0]))),
      y = Math.max(0, Math.floor(Math.min(a[1], b[1])));
    const x2 = Math.min(net.image.width, Math.ceil(Math.max(a[0], b[0]))),
      y2 = Math.min(net.image.height, Math.ceil(Math.max(a[1], b[1])));
    const width = x2 - x,
      height = y2 - y;
    if (
      width < 8 ||
      height < 8 ||
      width > 640 ||
      height > 256 ||
      width * height > net.image.width * net.image.height * 0.2
    ) {
      this.actions.notify(t("error.crop_too_large"));
      return;
    }
    if (!this.renderer.imageReady) {
      this.actions.notify(t("ocr.no_reading"));
      return;
    }
    this.abort?.abort();
    const controller = new AbortController();
    this.abort = controller;
    const crop = document.createElement("canvas");
    crop.width = width;
    crop.height = height;
    crop
      .getContext("2d")!
      .drawImage(this.renderer.image, x, y, width, height, 0, 0, width, height);
    this.actions.notify(t("ocr.reading"));
    try {
      const blob = await new Promise<Blob | null>((resolve) =>
        crop.toBlob(resolve, "image/png"),
      );
      if (!blob) return;
      const form = new FormData();
      form.append("image", blob, "label.png");
      form.append(
        "component_type",
        net.components.find((c) => c.id === this.actions.selected())?.type ||
          "resistor",
      );
      form.append("use_label_reader", String(this.actions.optIn()));
      const response = await fetch("/api/ocr-crop", {
        method: "POST",
        body: form,
        signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok) throw Error(result.detail?.code || "server_error");
      const candidates: OCRText[] = result.candidates || [];
      const item: OCRText = {
        text: candidates[0]?.text || "",
        bbox: [x, y, x2, y2],
        confidence: candidates[0]?.confidence || 0,
        parsed: candidates[0]?.parsed,
        outcome: "unassigned",
        reason: "not_selected",
      };
      this.renderer.texts.push(item);
      this.renderer.showText = true;
      const toggle = document.querySelector<HTMLInputElement>(
        "[data-testid=show-text]",
      );
      if (toggle) toggle.checked = true;
      this.open(item, candidates);
      if (!candidates.length) this.actions.notify(t("ocr.no_reading"));
    } catch (error) {
      if (!controller.signal.aborted)
        this.actions.notify(
          t(
            "error." +
              (error instanceof TypeError
                ? "network"
                : (error as Error).message),
          ),
        );
    } finally {
      crop.width = 0;
      crop.height = 0;
    }
  }
}
