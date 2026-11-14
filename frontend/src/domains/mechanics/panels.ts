import { t } from "../../shell";
import type { Scene } from "./types";
import { el, button, select } from "./workspace-dom";
import { nameOf, objects } from "./authoring";
import { valueAt } from "./validate";
import { componentName } from "./upload-panel";

export type WorkspaceMode = "explore" | "fix" | "advanced";

/** Compose existing tools into a canvas-first workspace without duplicating them. */
export class WorkspacePanels {
  readonly inspector: HTMLElement;
  readonly component: HTMLSelectElement;
  readonly uploadBody: HTMLElement;
  readonly center: HTMLElement;
  private nav: HTMLElement;
  private advanced: HTMLElement[];
  private repairs: HTMLElement[];
  private labels: HTMLElement;
  constructor(
    readonly root: HTMLElement,
    changeMode: (mode: WorkspaceMode) => void,
    selectObject: (id: string) => void,
  ) {
    const top = root.querySelector<HTMLElement>(".mech-toolbar")!;
    top.classList.add("mech-filebar");
    const layout = root.querySelector<HTMLElement>(".mech-layout")!;
    const diagram = layout.firstElementChild as HTMLElement,
      aside = layout.lastElementChild as HTMLElement;
    layout.classList.add("layout");
    diagram.classList.add("mech-diagram-panel", "center", "panel");
    aside.classList.add("mech-inspector-panel", "right", "panel");
    this.center = diagram;
    const input = el("aside", layout);
    input.className = "left mech-import-panel";
    layout.prepend(input);
    const card = el("section", input);
    card.className = "panel import-card";
    const head = el("div", card);
    head.className = "panel-head";
    el("h2", head, "upload_image");
    this.uploadBody = el("div", card);
    this.uploadBody.className = "panel-body";
    this.nav = el("nav");
    this.nav.className = "mech-modebar";
    this.nav.setAttribute("aria-label", t("mech.workspace_mode"));
    diagram.prepend(this.nav);
    button(this.nav, "explore", () => changeMode("explore"));
    button(this.nav, "fix_interpretation", () => changeMode("fix"));
    // Existing Edit scene action stays available as Advanced Authoring.
    const edit = root.querySelector<HTMLElement>('[data-action="edit_scene"]')!;
    this.nav.append(edit);
    const help = el("p", diagram, "explore_hint");
    help.className = "mech-canvas-hint";
    const controls = root.querySelector<HTMLElement>(
      '[data-action="play"]',
    )!.parentElement!;
    controls.classList.add("mech-playback");
    diagram.append(controls);
    const time = root.querySelector<HTMLElement>(
      '[data-testid="mechanics-time"]',
    )!.parentElement!;
    time.classList.add("mech-timeline");
    diagram.append(time);
    this.inspector = el("section");
    this.inspector.className = "mech-context";
    aside.prepend(this.inspector);
    el("h2", this.inspector, "component_inspector");
    this.component = select(
      this.inspector,
      "selected_component",
      [],
      selectObject,
    );
    this.component.dataset.testid = "mechanics-selection";
    this.labels = el("details", this.inspector);
    el("summary", this.labels, "linked_labels");
    const details = el("details");
    details.className = "mech-setup";
    el("summary", details, "analysis_settings");
    this.uploadBody.append(details, top);
    const analysis = root.querySelector<HTMLElement>(".mech-analysis")!;
    this.uploadBody.prepend(analysis);
    // Keep live progress/cancellation visible while settings stay out of Explore.
    const options = analysis.querySelector<HTMLElement>(".mech-toolbar")!;
    details.append(options);
    const fixture = root.querySelector<HTMLElement>(
      '[data-testid="mechanics-fixture"]',
    )!.parentElement!;
    top.append(fixture);
    const imports = root.querySelector<HTMLElement>(
      '[data-testid="mechanics-import"]',
    )!.parentElement!;
    details.append(imports);
    const correction = root.querySelector<HTMLElement>(
      '[data-action="save_correction"]',
    )!.parentElement!;
    details.append(correction);
    const archetype = root.querySelector<HTMLElement>(
      '[data-field="archetype"]',
    )!.parentElement!;
    const template = root.querySelector<HTMLElement>(
      '[data-action="place_template"]',
    )!;
    const setup = el("section", aside);
    setup.className = "mech-authoring-setup";
    setup.prepend(archetype, template);
    const hint = root.querySelector<HTMLElement>(
      '[data-i18n="mech.author_hint"]',
    )!;
    const review = root.querySelector<HTMLElement>(
      '[data-i18n="mech.review"]',
    )!;
    details.append(hint, review);
    const run = root.querySelector<HTMLElement>('[data-action="run"]')!;
    setup.append(run);
    this.advanced = [template];
    this.repairs = [setup];
    const original = root.querySelector<HTMLElement>(
      '[data-action="back_original"]',
    )!;
    original.classList.add("mech-secondary-action");
    for (const name of [
      "mechanics-provenance",
      "mechanics-notice",
      "mechanics-handwriting-notice",
      "mechanics-validation",
      "mechanics-readiness",
    ])
      diagram.insertBefore(
        root.querySelector(`[data-testid="${name}"]`)!,
        this.nav,
      );
  }
  refresh(mode: WorkspaceMode, scene: Scene | undefined, selected: string) {
    this.root.dataset.mode = mode;
    for (const [action, value] of [
      ["explore", "explore"],
      ["fix_interpretation", "fix"],
      ["edit_scene", "advanced"],
    ]) {
      const b = this.nav.querySelector<HTMLButtonElement>(
        `[data-action="${action}"]`,
      )!;
      b.setAttribute("aria-pressed", String(value === mode));
    }
    this.nav.setAttribute("aria-label", t("mech.workspace_mode"));
    for (const n of this.advanced) n.hidden = mode !== "advanced";
    for (const n of this.repairs) n.hidden = mode === "explore";
    const selectedBefore = this.component.value;
    this.component.replaceChildren();
    if (scene)
      for (const object of objects(scene).filter(
        (v) =>
          mode !== "explore" ||
          scene.bodies.includes(v as any) ||
          scene.surfaces.includes(v as any) ||
          scene.links.includes(v as any) ||
          scene.pulleys.includes(v as any),
      )) {
        const o = el("option", this.component);
        o.value = object.id;
        o.textContent =
          mode === "advanced"
            ? nameOf(scene, object.id)
            : componentName(scene, object.id);
      }
    this.component.value = selected || selectedBefore;
    this.component.disabled = !scene;
    for (const node of [...this.labels.children].slice(1)) node.remove();
    if (scene) {
      const owners = new Set([selected]);
      for (const link of scene.links)
        if ([link.a.ref, link.b.ref].includes(selected)) owners.add(link.id);
      const related = new Set(
        scene.bindings
          .filter(
            (b) =>
              owners.has(b.path.split(".")[1]) || b.path.startsWith("params."),
          )
          .map((b) => b.path),
      );
      for (const label of scene.annotations.filter(
        (a) => a.bound_to && related.has(a.bound_to),
      )) {
        const value = valueAt(scene, label.bound_to!);
        const p = el("p", this.labels);
        p.textContent = `${label.geometry.text ?? ""} → ${value.number ?? "?"} ${value.unit} · ${t(`mech.${value.status}`)}`;
      }
      this.labels.hidden = this.labels.children.length === 1;
    } else this.labels.hidden = true;
  }
}
