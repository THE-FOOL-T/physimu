import type { AppState } from "./state";
import { $ } from "./dom";
import { t, language } from "../i18n";
import { friendlyFilename } from "./filenames";
export function translateApp(appState: AppState, children: () => void) {
  for (const [id, key] of Object.entries({
    language: "ui.switch_language",
    "original-preview": "upload.preview",
    overlay: "ui.canvas",
    graph: "history",
    "component-select": "component",
    "merge-a": "ui.first_node",
    "merge-b": "ui.second_node",
    "netlist-json": "json",
    "analysis-mode": "ui.analysis_mode",
    direction: "ui.direction",
  }))
    $(id)?.setAttribute("aria-label", t(key));

  document
    .querySelectorAll<HTMLElement>("[data-i18n]")
    .forEach((el) => (el.textContent = t(el.dataset.i18n!)));
  document
    .querySelectorAll<HTMLInputElement>("[data-i18n-placeholder]")
    .forEach((el) => (el.placeholder = t(el.dataset.i18nPlaceholder!)));
  $("api-state").textContent = t(
    appState.online ? "model." + appState.modelStatus : "offline",
  );
  children();
  document
    .querySelectorAll<HTMLElement>("[data-i18n-aria]")
    .forEach((el) => el.setAttribute("aria-label", t(el.dataset.i18nAria!)));
  $("footer").textContent =
    language === "bn"
      ? t("draft")
      : appState.online
        ? t("ready_hint")
        : t("offline_hint");
  $("edit").textContent = t(appState.editing ? "done" : "edit");
  $("play").textContent = t(appState.playing ? "pause" : "play");
  for (const option of $<HTMLSelectElement>("demo").options) {
    const key =
      option.value === "rc"
        ? "rc_demo"
        : "demo." + option.value.split("/").at(-1)!.replace(".json", "");
    if (t(key) !== key) option.textContent = t(key);
  }
  const key = "demo." + appState.title.toLowerCase().replaceAll(" ", "-");
  $("circuit-title").textContent =
    t(key) !== key
      ? t(key)
      : appState.title.startsWith("RC ·")
        ? t("rc_demo")
        : friendlyFilename(appState.title);
  $("circuit-title").title = appState.title;
  document.dispatchEvent(new Event("workspace:translate"));
}
