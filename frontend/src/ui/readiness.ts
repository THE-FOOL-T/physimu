export function readiness(health: { detector?: string; ocr?: string }): string {
  if (health.detector !== "ready") return health.detector || "warming";
  if (health.ocr === "warming") return "warming";
  if (health.ocr && health.ocr !== "ready") return "ocr_unavailable";
  return "ready";
}
