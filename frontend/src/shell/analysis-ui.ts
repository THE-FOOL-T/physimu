/** Shared upload preview and stepper markup. Domain controllers own the evidence. */
export type AnalysisStepStatus =
  | "pending"
  | "running"
  | "completed"
  | "partial"
  | "failed"
  | "blocked"
  | "skipped";
export interface AnalysisStepState {
  id: string;
  status: AnalysisStepStatus;
  reason?: string;
  method?: string;
}

export function createAnalysisPreview(
  parent: HTMLElement,
  imageId: string,
  canvasId: string,
) {
  const frame = document.createElement("div");
  frame.className = "upload-preview";
  parent.append(frame);
  const image = document.createElement("img");
  image.dataset.testid = imageId;
  image.hidden = true;
  const canvas = document.createElement("canvas");
  canvas.dataset.testid = canvasId;
  canvas.hidden = true;
  frame.append(image, canvas);
  return { frame, image, canvas };
}

export class AnalysisStepper {
  constructor(
    readonly element: HTMLOListElement,
    private prefix = "stage.",
  ) {
    element.className = "stepper";
  }
  stages(ids: string[]) {
    this.element.replaceChildren();
    for (const id of ids) {
      const item = document.createElement("li");
      item.dataset.stage = id;
      item.dataset.i18n = this.prefix + id;
      this.element.append(item);
    }
  }
  /** Legacy Circuit index behavior is preserved exactly. */
  index(index: number) {
    Array.from(this.element.children).forEach((item, i) => {
      item.className = i < index ? "complete" : i === index ? "current" : "";
      if (i === index) item.setAttribute("aria-current", "step");
      else item.removeAttribute("aria-current");
    });
  }
  /** Explicit execution states, including skipped/blocked work, never inferred. */
  update(states: AnalysisStepState[]) {
    for (const item of this.element.querySelectorAll<HTMLElement>("li")) {
      const state = states.find((s) => s.id === item.dataset.stage);
      const status = state?.status ?? "pending";
      item.dataset.status = status;
      item.className =
        status === "completed"
          ? "complete"
          : status === "running"
            ? "current"
            : status;
      if (status === "running") item.setAttribute("aria-current", "step");
      else item.removeAttribute("aria-current");
      item.title = state?.reason ?? "";
    }
  }
}
