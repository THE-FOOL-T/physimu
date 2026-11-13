import { t, format } from "./language";
import type { Netlist } from "../domains/circuit/types";
import { friendlyFilename } from "./filenames";

let selectPanel: ((name: string) => void) | undefined;
export function activateTab(name: string) {
  const alias = name === "selected" || name === "graph" ? "readouts" : name;
  selectPanel?.(alias);
  if (name === "selected" || name === "graph") {
    const detail = document.getElementById(
      name + "-details",
    ) as HTMLDetailsElement | null;
    if (detail) detail.open = true;
    document.dispatchEvent(new Event("workspace:tab"));
  }
}
const make = <K extends keyof HTMLElementTagNameMap>(
  tag: K,
  parent: HTMLElement,
  key?: string,
) => {
  const el = document.createElement(tag);
  parent.append(el);
  if (key) {
    el.dataset.i18n = key;
    el.textContent = t(key);
  }
  return el;
};
export function updateSourceControl(net: Netlist) {
  const chip = document.getElementById("source-chip")!,
    source = net.components.find((c) =>
      ["dc_source", "battery", "ac_source"].includes(c.type),
    );
  chip.hidden = !source;
  if (!source) return;
  const value = source.value.number ?? 0;
  chip.querySelector<HTMLElement>("[data-source-label]")!.textContent =
    source.id + " · " + format(value, "V");
  chip.querySelector<HTMLElement>("[data-source-status]")!.textContent = t(
    source.value.status,
  );
  for (const input of chip.querySelectorAll<HTMLInputElement>("input")) {
    input.dataset.source = source.id;
    input.setAttribute("aria-label", source.id + " " + t("voltage"));
    if (input !== document.activeElement) input.value = String(value);
    if (input.type === "range" && (!input.max || value > Number(input.max)))
      input.max = String(Math.max(24, Math.abs(value) * 2));
  }
}
export function organizeWorkspace() {
  const get = (id: string) => document.getElementById(id)!;
  const layout = document.querySelector<HTMLElement>(".layout")!,
    left = document.querySelector<HTMLElement>(".left")!,
    right = document.querySelector<HTMLElement>(".right")!,
    center = document.querySelector<HTMLElement>(".center")!;
  for (const id of [
    "dropzone",
    "upload",
    "play",
    "edit",
    "controls",
    "overlay",
  ])
    get(id).dataset.testid = id;
  document.querySelector(".topnav > .muted")?.remove();
  const theme = make("button", document.querySelector(".topnav")!, "ui.theme");
  theme.id = "theme";
  theme.dataset.testid = "theme";
  const system = matchMedia("(prefers-color-scheme: dark)");
  const applyTheme = () => {
    let saved: string | null = null;
    try {
      saved = localStorage.getItem("circuit-theme");
    } catch {}
    document.documentElement.dataset.theme =
      saved || (system.matches ? "dark" : "light");
  };
  applyTheme();
  system.addEventListener("change", applyTheme);
  theme.onclick = () => {
    const next =
      document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    try {
      localStorage.setItem("circuit-theme", next);
    } catch {}
    document.documentElement.dataset.theme = next;
  };
  const stage = center.querySelector<HTMLElement>(".panel")!,
    toolbar = stage.querySelector<HTMLElement>(".toolbar")!,
    area = get("stage-area");
  toolbar.classList.add("canvas-toolbar");
  stage.insertBefore(toolbar, area);
  toolbar.append(get("direction"), get("edit"), get("export"), get("save"));
  toolbar.append(get("zoom").parentElement!);
  toolbar.append(
    document.querySelector<HTMLElement>("[data-testid=show-detections]")!
      .parentElement!,
  );
  const timeRow = get("physical-time").parentElement!,
    bottom = stage.querySelector<HTMLElement>(".stage-bottom")!;
  bottom.append(get("physical-time"));
  const speed = make("label", toolbar);
  speed.className = "speed-control";
  make("span", speed, "time_scale");
  speed.append(get("speed"));
  timeRow.remove();
  const viewport = make("div", area);
  viewport.id = "canvas-viewport";
  viewport.className = "canvas-viewport";
  viewport.append(get("canvas-shell"));
  const hint = make("p", stage, "layout.zoom_hint");
  hint.className = "mobile-zoom-hint";
  const sourceChip = make("label", toolbar);
  sourceChip.id = "source-chip";
  sourceChip.className = "source-chip";
  sourceChip.hidden = true;
  make("span", sourceChip).dataset.sourceLabel = "";
  make("small", sourceChip).dataset.sourceStatus = "";
  for (const type of ["range", "number"]) {
    const input = make("input", sourceChip);
    input.type = type;
    input.step = "any";
    if (type === "range") {
      input.min = "0";
      input.dataset.testid = "source-slider";
    }
    input.oninput = () =>
      document.dispatchEvent(
        new CustomEvent("workspace:source", {
          detail: { id: input.dataset.source, value: Number(input.value) },
        }),
      );
  }
  const editPanel = document.querySelector<HTMLElement>(".edit-panel")!;
  editPanel.classList.add("edit-dock");
  stage.insertBefore(editPanel, area);
  editPanel
    .querySelector("details summary")!
    .setAttribute("data-i18n", "ui.advanced");
  const summary = get("upload-name").parentElement!.querySelector<HTMLElement>(
    "[data-testid=result-summary]",
  )!;
  summary.classList.add("panel");
  left.append(summary);
  const parameters = get("parameters-panel"),
    warnings = get("notices").closest<HTMLElement>(".panel")!,
    selected = get("inspector").closest<HTMLElement>(".panel")!,
    readouts = get("readout").closest<HTMLElement>(".panel")!,
    graph = get("graph").closest<HTMLElement>(".panel")!;
  const readoutPane = document.createElement("section");
  readoutPane.className = "readout-sections";
  readoutPane.append(readouts);
  for (const [id, key, panel] of [
    ["selected", "selected", selected],
    ["graph", "history", graph],
  ] as const) {
    const details = make("details", readoutPane);
    details.id = id + "-details";
    details.className = "readout-details";
    make("summary", details, key);
    details.append(panel);
    details.addEventListener("toggle", () =>
      document.dispatchEvent(new Event("workspace:tab")),
    );
  }
  const explain = document.createElement("section");
  explain.className = "panel";
  make("h2", explain, "ui.explain").className = "panel-head";
  const explanation = make("ol", explain);
  explanation.id = "explanations";
  explanation.dataset.testid = "explanations";
  explanation.className = "panel-body explanation-list";
  right.prepend(document.querySelector(".metrics")!);
  const nav = make("div", right);
  nav.className = "workspace-tabs";
  nav.setAttribute("role", "tablist");
  nav.setAttribute("aria-label", t("layout.panels"));
  const items: [string, string, HTMLElement][] = [
    ["parameters", "parameters", parameters],
    ["readouts", "ui.tab_readouts", readoutPane],
    ["explain", "ui.explain", explain],
    ["warnings", "layout.checklist", warnings],
  ];
  const panes = new Map<string, HTMLElement>();
  for (const [index, [id, key, panel]] of items.entries()) {
    const b = make("button", nav, key);
    b.dataset.tab = id;
    b.id = "tab-" + id;
    b.setAttribute("role", "tab");
    b.setAttribute("aria-controls", "pane-" + id);
    const pane = make("div", right);
    pane.id = "pane-" + id;
    pane.className = "workspace-pane";
    pane.setAttribute("role", "tabpanel");
    pane.setAttribute("aria-labelledby", b.id);
    pane.append(panel);
    panes.set(id, pane);
    b.onclick = () => selectPanel?.(id);
    b.onkeydown = (e) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) return;
      e.preventDefault();
      const buttons = [...nav.querySelectorAll<HTMLButtonElement>("button")];
      const next =
        e.key === "Home"
          ? 0
          : e.key === "End"
            ? buttons.length - 1
            : (index + (e.key === "ArrowRight" ? 1 : -1) + buttons.length) %
              buttons.length;
      buttons[next].click();
      buttons[next].focus();
    };
  }
  selectPanel = (name) => {
    for (const [id, pane] of panes) {
      const active = id === name;
      pane.hidden = !active;
      const b = nav.querySelector<HTMLButtonElement>(`[data-tab="${id}"]`)!;
      b.setAttribute("aria-selected", String(active));
      b.tabIndex = active ? 0 : -1;
    }
    document.dispatchEvent(new Event("workspace:tab"));
  };
  selectPanel("parameters");
  document.addEventListener("workspace:loaded", () =>
    selectPanel?.("parameters"),
  );
  document.addEventListener("workspace:editing", (event) =>
    selectPanel?.(
      (event as CustomEvent<boolean>).detail ? "warnings" : "parameters",
    ),
  );
  get("keep-controls").append(document.createElement("br"));
  make("small", get("keep-controls"), "ui.keep_hint");
  const advanced = document.createElement("details");
  advanced.className = "import-advanced";
  make("summary", advanced, "ui.advanced");
  const saveRow = get("load").parentElement!;
  saveRow.before(advanced);
  advanced.append(saveRow);
  const problemLabel = document.createElement("label");
  problemLabel.dataset.i18n = "problem";
  problemLabel.htmlFor = "problem";
  get("problem").before(problemLabel);
  const readerToggle = get("ai-reader").closest("label")!,
    readerSettings = document.createElement("details");
  readerSettings.dataset.testid = "reader-settings";
  make("summary", readerSettings, "reader.settings");
  readerToggle.before(readerSettings);
  readerSettings.append(
    document.querySelector(".reader-disclosure")!,
    readerToggle,
  );
  const importCard = left.querySelector<HTMLElement>(".panel")!;
  importCard.classList.add("import-card");
  const strip = make("section", left);
  strip.className = "import-strip panel";
  strip.dataset.testid = "import-strip";
  const importName = make("strong", strip, "layout.import");
  importName.className = "import-name";
  const count = make("span", strip);
  count.className = "small";
  document.addEventListener("workspace:translate", () => {
    if (importName.title)
      importName.textContent = friendlyFilename(importName.title);
    if (count.dataset.count)
      count.textContent = t("layout.parts_count", {
        count: count.dataset.count,
      });
  });
  const replace = make("button", strip, "layout.replace");
  replace.onclick = () => {
    layout.classList.remove("import-collapsed");
    get("upload").click();
  };
  const original = make("button", strip, "layout.original"),
    expand = make("button", strip, "layout.expand_import");
  expand.onclick = () => layout.classList.toggle("import-collapsed");
  original.disabled = true;
  const collapse = make(
    "button",
    importCard.querySelector(".panel-head")!,
    "layout.collapse_import",
  );
  collapse.className = "quiet small";
  collapse.onclick = () => layout.classList.add("import-collapsed");
  const dialog = make("dialog", document.body);
  dialog.className = "original-dialog";
  dialog.setAttribute("aria-label", t("layout.original"));
  const close = make("button", dialog, "ocr.close");
  close.onclick = () => dialog.close();
  const originalImage = make("img", dialog);
  originalImage.alt = t("upload.preview");
  let originalUrl = "";
  original.onclick = () => {
    if (originalUrl) {
      originalImage.src = originalUrl;
      dialog.showModal();
    }
  };
  document.addEventListener("workspace:imported", (event) => {
    const detail = (
      event as CustomEvent<{ name: string; parts: number; original?: string }>
    ).detail;
    delete importName.dataset.i18n;
    importName.textContent = friendlyFilename(detail.name);
    importName.title = detail.name;
    count.dataset.count = String(detail.parts);
    count.textContent = t("layout.parts_count", {
      count: String(detail.parts),
    });
    originalUrl = detail.original || "";
    original.disabled = !originalUrl;
    layout.classList.add("import-collapsed");
  });
  document.addEventListener("workspace:importing", () => {
    layout.classList.remove("import-collapsed");
    dialog.close();
    originalImage.removeAttribute("src");
    originalUrl = "";
  });
  document.addEventListener("workspace:example", () =>
    layout.classList.remove("import-collapsed"),
  );
  const importBody = importCard.querySelector<HTMLElement>(".panel-body")!;
  const fields = make("div", importBody);
  fields.className = "import-fields";
  for (const child of [...importBody.children])
    if (child !== get("dropzone") && child !== fields) fields.append(child);
}
