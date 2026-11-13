import type { Scene } from "./types";
import { parseScene } from "./validate";

export interface MechanicsResult {
  domain: "mechanics";
  provenance: "extracted" | "partial" | "unsupported";
  reason: string | null;
  scene: Scene;
  source_image: string;
  warnings: Scene["warnings"];
  timings: Record<string, number | null>;
}
export interface DetectionBox {
  id: string;
  type: string;
  bbox: [number, number, number, number];
  confidence: number;
}
export interface AnalysisProgress {
  stage: string;
  percent: number;
  elapsed_seconds: number;
  partial?: {
    source_image?: string;
    width?: number;
    height?: number;
    detections?: DetectionBox[];
    texts?: { text: string; bbox: number[] }[];
  };
}
export interface MechanicsAnalysisOptions {
  style?: "auto" | "printed" | "handwritten";
  useLabelReader?: boolean;
}

export function parseResult(input: unknown): MechanicsResult {
  const r = input as MechanicsResult;
  if (
    !r ||
    r.domain !== "mechanics" ||
    !["extracted", "partial", "unsupported"].includes(r.provenance) ||
    typeof r.source_image !== "string" ||
    !r.source_image.startsWith("data:image/png;base64,")
  )
    throw new Error("mech.invalid_analysis");
  const scene = parseScene(r.scene);
  if (scene.meta.provenance !== r.provenance)
    throw new Error("mech.invalid_analysis");
  return { ...r, scene };
}

/** One generation owns one job. Cancellation also rejects late successful responses. */
export class MechanicsAnalysis {
  private generation = 0;
  private controller?: AbortController;
  private job = "";
  constructor(private transport: typeof fetch = (...args) => fetch(...args)) {}
  cancel() {
    this.generation++;
    this.controller?.abort();
    const job = this.job;
    this.job = "";
    if (job)
      void this.transport(`/api/analyze/${encodeURIComponent(job)}`, {
        method: "DELETE",
      }).catch(() => {});
  }
  async start(
    file: File,
    lang: string,
    progress: (p: AnalysisProgress) => void | Promise<void>,
    options: MechanicsAnalysisOptions = {},
  ): Promise<MechanicsResult | null> {
    this.cancel();
    const token = this.generation,
      controller = new AbortController();
    this.controller = controller;
    const active = () =>
      token === this.generation && !controller.signal.aborted;
    const form = new FormData();
    form.append("image", file);
    form.append("domain", "mechanics");
    form.append("lang", lang);
    form.append("style", options.style ?? "auto");
    form.append("use_label_reader", String(options.useLabelReader === true));
    const response = await this.transport("/api/analyze/start", {
      method: "POST",
      body: form,
      signal: controller.signal,
    });
    const received = await response.json();
    if (!response.ok)
      throw new Error(`mech.${received?.detail?.code ?? "analysis_failed"}`);
    if (!active()) {
      if (typeof received.job_id === "string")
        void this.transport(
          `/api/analyze/${encodeURIComponent(received.job_id)}`,
          { method: "DELETE" },
        ).catch(() => {});
      return null;
    }
    if (
      received.domain !== "mechanics" ||
      typeof received.job_id !== "string" ||
      !Array.isArray(received.stages)
    )
      throw new Error("mech.invalid_analysis");
    this.job = received.job_id;
    let hasImage = false;
    while (active()) {
      const poll = await this.transport(
        `/api/analyze/${encodeURIComponent(this.job)}?include_image=${!hasImage}`,
        { signal: controller.signal },
      );
      const job = await poll.json();
      if (!active()) return null;
      if (!poll.ok || job.error)
        throw new Error(
          `mech.${job?.error?.code ?? job?.detail?.code ?? "analysis_failed"}`,
        );
      if (typeof job.stage !== "string" || !Number.isFinite(job.percent))
        throw new Error("mech.invalid_analysis");
      await progress(job);
      if (!active()) return null;
      if (job.partial?.source_image && job.partial.width && job.partial.height)
        hasImage = true;
      if (job.result) {
        this.job = "";
        return parseResult(job.result);
      }
      await new Promise<void>((resolve) => {
        const done = () => {
          clearTimeout(timer);
          controller.signal.removeEventListener("abort", done);
          resolve();
        };
        const timer = setTimeout(done, 100);
        controller.signal.addEventListener("abort", done, { once: true });
      });
    }
    return null;
  }
}
