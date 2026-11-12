// Stable shared imports. Implementations remain at their current paths until M7.
export { UploadWorkspace } from "../ui/upload";
export type { AnalysisResult } from "../ui/upload";
export { organizeWorkspace, activateTab } from "../ui/workspace";
export { translateApp } from "../ui/translation";
export { ImageStore, selfContained, withoutImage } from "../ui/image-store";
export {
  language,
  setLanguage,
  t,
  format,
  banglaDigits,
  setDigits,
} from "../i18n";
export { $, esc, options } from "../ui/dom";
export { mountDomainSwitch } from "./domain-switch";
export type { DomainModule, DomainHandle, DomainId } from "../domains";

export interface ShellContext {
  t(key: string): string;
}
