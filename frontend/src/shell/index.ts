// Stable shared imports backed by the shell implementations.
export { UploadWorkspace } from "./upload";
export type { AnalysisResult } from "./upload";
export { organizeWorkspace, activateTab } from "./workspace";
export { translateApp } from "./translation";
export { ImageStore, selfContained, withoutImage } from "./image-store";
export {
  language,
  setLanguage,
  t,
  format,
  banglaDigits,
  setDigits,
} from "./language";
export { $, esc, options } from "./dom";
export { mountDomainSwitch } from "./domain-switch";
export type { DomainModule, DomainHandle, DomainId } from "../domains/index";
export * from "../shared/sim/index";

export interface ShellContext {
  t(key: string): string;
}
