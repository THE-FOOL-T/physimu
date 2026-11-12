import {
  t,
  language,
  banglaDigits,
  SimulationClock,
  parameterPanel,
  drawGraphs,
} from "../../shell";
import type { DomainHandle } from "../../shell";
import type { Scene, Point, ArchetypeId, BBox } from "./types";
import { BindingEngine } from "./bindings";
import { MechanicsRenderer, type RenderOptions } from "./renderer";
import { archetypes } from "./archetypes";
import { sample } from "./sampling";
import { parseScene, valueAt } from "./validate";
import { fixture, fixtureNames } from "./catalog";
import {
  stencil,
  emptyScene,
  objects,
  nameOf,
  rename,
  handles,
  moveHandle,
  setBox,
  attach,
  addLine,
  assignValue,
  userValue,
  switchArchetype,
  valuePaths,
  SceneHistory,
  calibrate,
  removeObject,
  type Handle,
  type EditState,
} from "./authoring";
import {
  project,
  parseProject,
  restoreEngine,
  checkImage,
  readFile,
  download,
} from "./project";
import "./workspace.css";

const numberText = (n: number, places = 2) => {
  const v = n.toFixed(places);
  return banglaDigits ? v.replace(/\d/g, (d) => "০১২৩৪৫৬৭৮৯"[Number(d)]) : v;
};
function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  parent?: HTMLElement,
  key?: string,
) {
  const n = document.createElement(tag);
  if (key) {
    n.dataset.i18n = `mech.${key}`;
    n.textContent = t(`mech.${key}`);
  }
  parent?.append(n);
  return n;
}
function button(parent: HTMLElement, key: string, action: () => void) {
  const b = el("button", parent, key);
  b.type = "button";
  b.dataset.action = key;
  b.addEventListener("click", action);
  return b;
}
function select(
  parent: HTMLElement,
  key: string,
  items: string[],
  action: (value: string) => void,
) {
  const label = el("label", parent);
  el("span", label, key);
  const input = el("select", label);
  input.dataset.field = key;
  for (const item of items) {
    const o = el("option", input);
    o.value = item;
    o.textContent =
      t(`mech.${item}`) === `mech.${item}` ? item : t(`mech.${item}`);
  }
  input.addEventListener("change", () => action(input.value));
  return input;
}
function input(
  parent: HTMLElement,
  key: string,
  value: string,
  apply: (value: string) => void,
  type = "text",
) {
  const label = el("label", parent);
  el("span", label, key);
  const n = el("input", label);
  n.type = type;
  n.value = value;
  n.dataset.field = key;
  n.addEventListener("change", () => apply(n.value));
  return n;
}
const archetypeIds = Object.keys(archetypes) as ArchetypeId[];
type Tool =
  | "select"
  | "rope"
  | "spring"
  | "incline"
  | "floor"
  | "mask"
  | "repair";

export class MechanicsWorkspace implements DomainHandle {
  readonly root = el("main");
  private image = "";
  private engine: BindingEngine | null = null;
  private renderer: MechanicsRenderer | null = null;
  private history = new SceneHistory();
  private clock = new SimulationClock();
  private generation = 0;
  private active = false;
  private raf = 0;
  private editing = false;
  private selected = "";
  private tool: Tool = "select";
  private points: Point[] = [];
  private drag: { handle: Handle; point: Point } | null = null;
  private options: RenderOptions = {
    forces: true,
    components: false,
    trail: true,
    original: false,
    marker: true,
    handles: false,
  };
  private mode = matchMedia("(prefers-reduced-motion: reduce)");
  private provenance: HTMLElement;
  private notice: HTMLElement;
  private validation: HTMLElement;
  private regime: HTMLElement;
  private modified: HTMLElement;
  private canvas: HTMLCanvasElement;
  private viewport: HTMLElement;
  private params: HTMLElement;
  private editor: HTMLElement;
  private warnings: HTMLElement;
  private readouts: HTMLElement;
  private graph: HTMLCanvasElement;
  private objectSelect: HTMLSelectElement;
  private archetypeSelect: HTMLSelectElement;
  private scrub: HTMLInputElement;
  private time: HTMLElement;
  private tabs = new Map<string, HTMLElement>();
  private undoButton: HTMLButtonElement;
  private redoButton: HTMLButtonElement;
  private playButton: HTMLButtonElement;
  private runButton: HTMLButtonElement;
  private locale = "";
  constructor() {
    this.root.className = "mechanics-workspace";
    this.root.dataset.testid = "mechanics-workspace";
    el("h1", this.root, "title");
    this.provenance = el("p", this.root);
    this.provenance.dataset.testid = "mechanics-provenance";
    const top = el("div", this.root);
    top.className = "mech-toolbar";
    const label = el("label", top);
    el("span", label, "upload_image");
    const upload = el("input", label);
    upload.type = "file";
    upload.accept = "image/png,image/jpeg,image/webp";
    upload.dataset.testid = "mechanics-image";
    upload.addEventListener("change", () => {
      const f = upload.files?.[0];
      if (f) void this.upload(f);
      upload.value = "";
    });
    const il = el("label", top);
    el("span", il, "import_project");
    const importer = el("input", il);
    importer.type = "file";
    importer.accept = "application/json,.json";
    importer.dataset.testid = "mechanics-import";
    importer.addEventListener("change", () => {
      const f = importer.files?.[0];
      if (f) void this.import(f);
      importer.value = "";
    });
    button(top, "export_project", () => {
      if (this.engine)
        download(
          new Blob(
            [JSON.stringify(project(this.engine, this.image), null, 2)],
            { type: "application/json" },
          ),
          "mechanics-project.json",
        );
    });
    button(top, "export_png", () =>
      this.canvas.toBlob((blob) => {
        if (blob) download(blob, "mechanics-overlay.png");
      }),
    );
    const fixtures = select(
      top,
      "synthetic_fixture",
      ["choose_fixture", ...fixtureNames],
      (v) => {
        if (fixtureNames.includes(v)) void this.loadFixture(v);
      },
    );
    fixtures.dataset.testid = "mechanics-fixture";
    this.archetypeSelect = select(top, "archetype", archetypeIds, (v) =>
      this.edit((s) => switchArchetype(s, v as ArchetypeId)),
    );
    button(top, "place_template", () => {
      if (!this.engine) return;
      const id = this.archetypeSelect.value as ArchetypeId;
      if (id === "unsupported") return;
      const name = fixtureNames.find((n) => fixture(n).scene.archetype === id)!;
      this.edit((s) => Object.assign(s, stencil(fixture(name).scene, s.image)));
      this.editing = true;
      this.refresh();
    });
    el("p", this.root, "author_hint");
    el("p", this.root, "review");
    this.notice = el("p", this.root);
    this.notice.setAttribute("role", "status");
    this.notice.dataset.testid = "mechanics-notice";
    this.validation = el("p", this.root);
    this.validation.dataset.testid = "mechanics-validation";
    const controls = el("div", this.root);
    controls.className = "mech-toolbar";
    button(controls, "edit_scene", () => {
      this.editing = true;
      this.clock.reset();
      this.points = [];
      this.refresh();
    });
    this.runButton = button(controls, "run", () => {
      this.editing = false;
      this.points = [];
      this.clock.reset();
      void this.prepare();
      this.refresh();
    });
    this.playButton = button(controls, "play", () => {
      if (this.engine?.trajectory.supported && !this.editing) {
        this.clock.play();
        this.refreshPlayback();
      }
    });
    button(controls, "pause", () => {
      this.clock.pause();
      this.refreshPlayback();
    });
    button(controls, "reset", () => {
      this.clock.reset();
      this.render();
    });
    button(controls, "step", () => {
      this.clock.step();
      this.render();
    });
    const speed = select(
      controls,
      "speed",
      ["0.25", "0.5", "1", "2", "4"],
      (v) => this.clock.setSpeed(Number(v)),
    );
    speed.value = "1";
    this.undoButton = button(controls, "undo", () => this.travel(false));
    this.redoButton = button(controls, "redo", () => this.travel(true));
    button(controls, "back_original", () =>
      this.change(() => this.engine!.backToOriginal()),
    );
    this.modified = el("strong", controls);
    this.modified.dataset.testid = "mechanics-modified";
    const tl = el("label", this.root);
    el("span", tl, "time");
    this.scrub = el("input", tl);
    this.scrub.type = "range";
    this.scrub.min = "0";
    this.scrub.step = "0.004166666667";
    this.scrub.dataset.testid = "mechanics-time";
    this.scrub.addEventListener("input", () => {
      this.clock.pause();
      this.clock.seek(Number(this.scrub.value));
      this.render();
    });
    this.time = el("output", tl);
    const layout = el("div", this.root);
    layout.className = "mech-layout";
    const dp = el("section", layout);
    el("h2", dp, "diagram");
    const oc = el("div", dp);
    oc.className = "mech-toolbar";
    for (const key of [
      "forces",
      "components",
      "trail",
      "original",
      "marker",
    ] as const) {
      const l = el("label", oc),
        c = el("input", l);
      c.type = "checkbox";
      c.checked = this.options[key];
      c.dataset.overlay = key;
      el("span", l, key);
      c.addEventListener("change", () => {
        this.options[key] = c.checked;
        this.render();
      });
    }
    select(oc, "zoom", ["fit", "1", "1.5", "2"], () => this.render());
    this.viewport = el("div", dp);
    this.viewport.className = "mech-viewport";
    this.canvas = el("canvas", this.viewport);
    this.canvas.tabIndex = 0;
    this.canvas.setAttribute("role", "img");
    this.canvas.dataset.testid = "mechanics-canvas";
    this.canvas.width = 800;
    this.canvas.height = 520;
    this.canvas.addEventListener("pointerdown", (e) => this.down(e));
    this.canvas.addEventListener("pointermove", (e) => {
      if (this.drag) {
        this.drag.point = this.nativePoint(e);
        this.render();
      }
    });
    this.canvas.addEventListener("pointerup", (e) => this.up(e));
    this.canvas.addEventListener("pointercancel", () => {
      this.drag = null;
      this.render();
    });
    this.canvas.addEventListener("keydown", (e) => this.key(e));
    const aside = el("aside", layout),
      tablist = el("div", aside);
    tablist.className = "mech-tabs";
    tablist.setAttribute("role", "tablist");
    tablist.setAttribute("aria-label", t("mech.panels"));
    for (const name of ["parameters", "warnings", "readouts", "graphs"]) {
      const b = button(tablist, name, () => this.tab(name));
      b.setAttribute("role", "tab");
      b.id = `mech-tab-${name}`;
      b.setAttribute("aria-controls", `mech-panel-${name}`);
      const panel = el("section", aside);
      panel.id = `mech-panel-${name}`;
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", b.id);
      this.tabs.set(name, panel);
      b.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
          e.preventDefault();
          const names = [...this.tabs.keys()],
            i = names.indexOf(name),
            next = names[(i + (e.key === "ArrowRight" ? 1 : 3)) % 4];
          this.tab(next);
          this.root
            .querySelector<HTMLButtonElement>(`#mech-tab-${next}`)!
            .focus();
        }
      });
    }
    this.params = el("div", this.tabs.get("parameters")!);
    this.params.dataset.testid = "mechanics-parameters";
    this.regime = el("p", this.tabs.get("parameters")!);
    this.regime.dataset.testid = "mechanics-regime";
    this.editor = el("section", this.tabs.get("parameters")!);
    this.editor.className = "mech-editor";
    el("h2", this.editor, "scene_editor");
    this.objectSelect = select(this.editor, "object", [], (v) => {
      this.selected = v;
      this.refreshEditor();
      this.render();
    });
    select(
      this.editor,
      "tool",
      ["select", "rope", "spring", "incline", "floor", "mask", "repair"],
      (v) => {
        this.tool = v as Tool;
        this.points = [];
        this.editing = true;
        this.clock.reset();
        this.render();
      },
    ).dataset.testid = "mechanics-tool";
    button(this.editor, "finish_shape", () => this.finishShape());
    button(this.editor, "cancel_shape", () => {
      this.points = [];
      this.render();
    });
    el("p", this.editor, "edit_hint");
    el("div", this.editor).dataset.testid = "mechanics-object-fields";
    this.warnings = el("div", this.tabs.get("warnings")!);
    this.warnings.dataset.testid = "mechanics-warnings";
    this.readouts = el("div", this.tabs.get("readouts")!);
    this.readouts.dataset.testid = "mechanics-readouts";
    this.graph = el("canvas", this.tabs.get("graphs")!);
    this.graph.width = 600;
    this.graph.height = 480;
    this.graph.setAttribute("role", "img");
    this.graph.dataset.testid = "mechanics-graphs";
    const chips = el("section", this.editor);
    el("h3", chips, "unplaced_values");
    el("div", chips).dataset.testid = "mechanics-chips";
    button(chips, "add_value", () =>
      this.edit((s) => {
        let n = 1;
        while (`unplaced_${n}` in s.params) n++;
        s.params[`unplaced_${n}`] = userValue(null, "kg");
      }),
    );
    this.mode.addEventListener("change", () => {
      if (this.mode.matches) this.clock.pause();
      this.refreshWarnings();
      this.render();
    });
    this.tab("parameters");
    this.refresh();
  }
  mount(container: HTMLElement) {
    this.active = true;
    container.append(this.root);
    document.addEventListener("workspace:translate", this.translate);
    this.translate();
    if (this.engine) void this.prepare();
    this.frame();
    return this;
  }
  unmount() {
    this.active = false;
    ++this.generation;
    this.clock.pause();
    cancelAnimationFrame(this.raf);
    document.removeEventListener("workspace:translate", this.translate);
    this.drag = null;
    this.points = [];
    this.root.remove();
  }
  getDocument() {
    return this.engine ? project(this.engine, this.image) : null;
  }
  inspect() {
    return {
      project: this.getDocument(),
      time: this.clock.displayTime,
      playing: this.clock.playing,
      editing: this.editing,
      active: this.active,
      frame0: this.renderer?.frame0,
      degraded: this.renderer?.degraded,
      background: this.renderer?.backgroundHash(),
      padding: this.renderer?.padding,
      dpr: this.renderer?.dpr,
      supported: this.engine?.trajectory.supported,
      handles: this.engine
        ? structuredClone(handles(this.engine.original))
        : [],
    };
  }
  private translate = () => {
    const locale = `${language}/${banglaDigits}`;
    if (this.locale === locale) return;
    this.locale = locale;
    this.refresh();
  };
  private tab(name: string) {
    for (const [key, panel] of this.tabs) {
      panel.hidden = key !== name;
      const b = this.root.querySelector(`[aria-controls="${panel.id}"]`)!;
      b.setAttribute("aria-selected", String(key === name));
      b.setAttribute("tabindex", key === name ? "0" : "-1");
    }
    if (this.canvas) this.render();
  }
  private report(error: unknown) {
    const key = error instanceof Error ? error.message : String(error);
    this.notice.textContent = key.startsWith("mech.")
      ? t(key)
      : `${t("mech.validation_failed")}: ${key}`;
  }
  private async upload(file: File) {
    const token = ++this.generation;
    try {
      if (!["image/png", "image/jpeg", "image/webp"].includes(file.type))
        throw new Error("mech.invalid_image");
      const data = await readFile(file),
        img = await checkImage(data);
      if (token !== this.generation) return;
      this.install(
        emptyScene({
          path: file.name,
          width: img.naturalWidth,
          height: img.naturalHeight,
        }),
        data,
        true,
      );
    } catch (e) {
      if (token === this.generation) this.report(e);
    }
  }
  private async import(file: File) {
    const token = ++this.generation;
    try {
      if (file.size > 44000000) throw new Error("mech.image_size");
      const p = parseProject(JSON.parse(await file.text()));
      await checkImage(
        p.source_image,
        p.scene.image.width,
        p.scene.image.height,
      );
      if (token !== this.generation) return;
      this.install(p.scene, p.source_image, false, {
        scene: p.scene,
        overrides: p.parameter_overrides,
        unlocked: p.unlocked_geometry,
      });
      this.notice.textContent = t("mech.import_valid");
    } catch (e) {
      if (token === this.generation) this.report(e);
    }
  }
  private async loadFixture(name: string) {
    const token = ++this.generation;
    try {
      const f = fixture(name),
        res = await fetch(f.url),
        data = await readFile(
          new File([await res.blob()], `${name}.png`, { type: "image/png" }),
        );
      if (token !== this.generation) return;
      this.install(f.scene, data, false);
    } catch (e) {
      if (token === this.generation) this.report(e);
    }
  }
  private install(
    scene: Scene,
    image: string,
    editing: boolean,
    state?: EditState,
  ) {
    this.clock.reset();
    this.image = image;
    this.engine = state
      ? restoreEngine(state)
      : new BindingEngine(parseScene(scene));
    this.history = new SceneHistory();
    this.editing = editing;
    this.selected = scene.bodies[0]?.id ?? objects(scene)[0]?.id ?? "";
    this.points = [];
    this.notice.textContent = "";
    this.renderer = null;
    delete this.root.dataset.ready;
    this.refresh();
    void this.prepare();
  }
  private snapshot(): EditState {
    return {
      scene: structuredClone(this.engine!.original),
      overrides: { ...this.engine!.params },
      unlocked: [...this.engine!.unlocked],
    };
  }
  private change(action: () => void) {
    if (!this.engine) return;
    const before = this.snapshot();
    try {
      action();
      this.history.push(before, this.snapshot());
      this.clock.reset();
      this.refresh();
      void this.prepare();
    } catch (e) {
      this.engine = restoreEngine(before);
      this.report(e);
    }
  }
  private edit(action: (scene: Scene) => void) {
    if (!this.engine) {
      this.notice.textContent = t("mech.choose_image");
      return;
    }
    this.change(() => {
      const old = this.engine!,
        s = structuredClone(old.original);
      action(s);
      s.meta.provenance =
        s.archetype === "unsupported" ? "unsupported" : "authored";
      const checked = parseScene(s),
        engine = new BindingEngine(checked);
      for (const id of old.unlocked)
        if (checked.bindings.some((b) => b.id === id && b.class === "geometry"))
          engine.unlock(id);
      const values: Record<string, number> = {};
      for (const b of checked.bindings) {
        try {
          if (
            b.path in old.params &&
            JSON.stringify(valueAt(old.original, b.path)) ===
              JSON.stringify(valueAt(checked, b.path))
          )
            values[b.id] = old.params[b.path];
        } catch {
          /* Removed path. */
        }
      }
      if (Object.keys(values).length) engine.setMany(values);
      this.engine = engine;
    });
  }
  private travel(redo: boolean) {
    const state = redo ? this.history.redo() : this.history.undo();
    if (!state) return;
    this.engine = restoreEngine(state);
    this.clock.reset();
    this.refresh();
    void this.prepare();
  }
  private async prepare() {
    const engine = this.engine,
      image = this.image,
      token = ++this.generation;
    if (!engine) return;
    try {
      const renderer = await MechanicsRenderer.load(engine.original, image);
      if (token !== this.generation) return;
      if (engine.trajectory.supported) {
        const initial = archetypes[engine.original.archetype].solve(
          engine.original,
          {},
        );
        if (initial.states.length)
          renderer.renderFrame0Check(initial.states[0]);
        renderer.fitTrajectory(engine.trajectory, engine.params);
      }
      this.renderer = renderer;
      this.clock.duration = engine.trajectory.duration;
      this.scrub.max = String(this.clock.duration);
      this.refreshWarnings();
      this.validation.textContent = `${t("mech.validation_ok")} · ${t(engine.trajectory.supported ? "mech.simulation_ready" : "mech.unsupported")}`;
      if (renderer.degraded)
        this.validation.textContent += ` · ${t("mech.render_notice")}`;
      this.render();
    } catch (e) {
      if (token === this.generation) {
        this.renderer = null;
        this.report(e);
      }
    }
  }
  private refresh() {
    for (const n of this.root.querySelectorAll<HTMLElement>("[data-i18n]"))
      n.textContent = t(n.dataset.i18n!);
    for (const n of this.root.querySelectorAll<HTMLSelectElement>("select"))
      for (const o of n.options) {
        const key = `mech.${o.value}`;
        if (t(key) !== key) o.textContent = t(key);
      }
    this.canvas.setAttribute("aria-label", t("mech.diagram_keyboard"));
    this.graph.setAttribute("aria-label", t("mech.graph_description"));
    this.root
      .querySelector('[role="tablist"]')!
      .setAttribute("aria-label", t("mech.panels"));
    const s = this.engine?.original;
    this.provenance.textContent = `${t("mech.provenance")}: ${t(`mech.${s?.meta.provenance ?? "unsupported"}`)}`;
    this.validation.textContent = s
      ? `${t("mech.validation_ok")} · ${numberText(objects(s).length, 0)} ${t("mech.objects")}`
      : t("mech.choose_image");
    this.archetypeSelect.value = s?.archetype ?? "unsupported";
    this.archetypeSelect.disabled = !s;
    this.undoButton.disabled = !this.history.canUndo;
    this.redoButton.disabled = !this.history.canRedo;
    this.modified.textContent = this.engine?.modified ? t("mech.modified") : "";
    this.runButton.disabled = !s;
    this.refreshPlayback();
    if (this.engine) {
      try {
        const rows = this.engine.rows().map((row) => ({
          ...row,
          label:
            t(`mech.param_${row.id}`) === `mech.param_${row.id}`
              ? row.id.replaceAll("_", " ")
              : t(`mech.param_${row.id}`),
        }));
        parameterPanel(
          this.params,
          rows,
          (id, n) => this.change(() => this.engine!.set(id, n)),
          (id) =>
            this.change(() => {
              if (this.engine!.unlocked.has(id))
                this.engine!.unlocked.delete(id);
              else this.engine!.unlock(id);
            }),
        );
        for (const row of rows) {
          const field = this.params.querySelector<HTMLElement>(
            `[data-parameter="${row.id}"]`,
          )!;
          field.querySelector("small")!.textContent = t(
            `mech.binding_${row.kind}`,
          );
          field.querySelector(".sim-badge")!.textContent =
            `${t(`mech.${row.status}`)} · ${numberText(row.confidence * 100, 0)}%`;
          const b = field.querySelector("button")!;
          b.disabled = false;
          b.textContent = t(row.locked ? "mech.unlock" : "mech.lock");
          b.setAttribute("aria-label", `${b.textContent} ${row.label}`);
          for (const i of field.querySelectorAll("input"))
            i.setAttribute("aria-label", `${row.label} ${t(`mech.${i.type}`)}`);
        }
      } catch (e) {
        this.params.replaceChildren();
        this.report(e);
      }
      try {
        const regime = archetypes[this.engine.original.archetype].regime(
          this.engine.original,
          this.engine.params,
        );
        this.regime.textContent = `${t("mech.regime")}: ${this.code(regime.code)}`;
      } catch {
        this.regime.textContent = t("mech.unsupported");
      }
    }
    this.refreshEditor();
    this.refreshWarnings();
    this.render();
  }
  private code(code: string) {
    const key = `mech.${code}`;
    return t(key) === key ? `${t("mech.diagnostic")} (${code})` : t(key);
  }
  private refreshPlayback() {
    this.editor.hidden = !this.editing;
    for (const key of ["export_project", "export_png", "place_template"]) {
      const button = this.root.querySelector<HTMLButtonElement>(
        `[data-action="${key}"]`,
      )!;
      button.disabled =
        !this.engine || (key !== "place_template" && !this.renderer);
    }
    this.playButton.disabled =
      !this.engine?.trajectory.supported || this.editing || !this.renderer;
    this.root.dataset.editing = String(this.editing);
    this.root.dataset.playing = String(this.clock.playing);
  }
  private refreshWarnings() {
    this.warnings.replaceChildren();
    const codes = [
      ...(this.engine?.original.warnings.map((w) => w.code) ?? []),
      ...(this.engine?.trajectory.warnings ?? []),
      ...(this.renderer?.warnings ?? []),
    ];
    if (this.mode.matches) codes.push("reduced_motion");
    if (
      Object.keys(this.engine?.original.params ?? {}).some((k) =>
        k.startsWith("unplaced_"),
      )
    )
      codes.push("unplaced_pending");
    for (const code of [...new Set(codes)])
      el("p", this.warnings).textContent = this.code(code);
    if (!codes.length) el("p", this.warnings, "no_warnings");
    if (this.renderer?.degraded) el("p", this.warnings, "render_notice");
  }
  private refreshEditor() {
    const s = this.engine?.original,
      fields = this.editor.querySelector<HTMLElement>(
        '[data-testid="mechanics-object-fields"]',
      )!,
      chips = this.editor.querySelector<HTMLElement>(
        '[data-testid="mechanics-chips"]',
      )!;
    fields.replaceChildren();
    chips.replaceChildren();
    this.objectSelect.replaceChildren();
    if (!s) return;
    for (const o of objects(s)) {
      const option = el("option", this.objectSelect);
      option.value = o.id;
      option.textContent = `${nameOf(s, o.id)} (${o.id})`;
    }
    if (!objects(s).some((o) => o.id === this.selected))
      this.selected = objects(s)[0]?.id ?? "";
    this.objectSelect.value = this.selected;
    const object = objects(s).find((o) => o.id === this.selected),
      body = s.bodies.find((b) => b.id === this.selected),
      link = s.links.find((l) => l.id === this.selected);
    if (object) {
      button(fields, "delete_object", () =>
        this.edit((s) => removeObject(s, object.id)),
      );
      input(fields, "name", nameOf(s, object.id), (v) =>
        this.edit((s) => rename(s, object.id, v)),
      );
      if ("type" in object)
        input(fields, "object_type", object.type, (v) =>
          this.edit((s) => {
            const o = objects(s).find((o) => o.id === object.id)!;
            if ("type" in o) o.type = v;
            s.warnings = s.warnings.filter((w) => w.code !== "unknown_type");
          }),
        );
      if (body) {
        input(fields, "box", body.bbox.join(", "), (v) =>
          this.edit((s) => setBox(s, body.id, this.coordinates(v, 4) as BBox)),
        );
        input(fields, "sprite_mask", JSON.stringify(body.mask), (v) =>
          this.edit((s) => {
            s.bodies.find((b) => b.id === body.id)!.mask = this.polygon(v);
          }),
        );
      }
      for (const h of handles(s).filter((h) => h.object === object.id))
        input(
          fields,
          h.id.endsWith(":a")
            ? "end_a"
            : h.id.endsWith(":b")
              ? "end_b"
              : h.kind === "surface"
                ? h.index === 0
                  ? "base"
                  : "tip"
                : h.kind === "body"
                  ? "anchor"
                  : "centre",
          h.point.join(", "),
          (v) =>
            this.edit((s) => moveHandle(s, h, this.coordinates(v, 2) as Point)),
        );
      if (link)
        for (const end of ["a", "b"] as const) {
          const candidates = [
              ...s.bodies,
              ...s.pulleys,
              ...s.annotations.filter((a) => a.type === "axis"),
            ].map((v) => v.id),
            sel = select(fields, `attach_${end}`, candidates, (v) =>
              this.edit((s) => attach(s, link.id, end, v)),
            );
          sel.value = link[end].ref;
        }
      if (s.surfaces.some((v) => v.id === object.id) || link) {
        const repair = s.repairs.find(
          (r) => r.surface_or_line_id === object.id,
        );
        input(
          fields,
          "repair_segments",
          JSON.stringify(repair?.segments ?? []),
          (v) =>
            this.edit((s) => {
              const segments = JSON.parse(v) as Point[][];
              if (!Array.isArray(segments))
                throw new Error("mech.invalid_points");
              s.repairs = s.repairs.filter(
                (r) => r.surface_or_line_id !== object.id,
              );
              s.repairs.push({ surface_or_line_id: object.id, segments });
            }),
        );
      }
    }
    input(fields, "paper_color", s.frame.paper_color, (v) =>
      this.edit((s) => (s.frame.paper_color = v)),
    );
    input(fields, "ink_color", s.frame.ink_color, (v) =>
      this.edit((s) => (s.frame.ink_color = v)),
    );
    input(
      fields,
      "stroke_px",
      String(s.frame.stroke_px),
      (v) => this.edit((s) => (s.frame.stroke_px = Number(v))),
      "number",
    );
    for (const path of valuePaths(s).filter(
      (p) =>
        !p.startsWith("params.unplaced_") &&
        (p.startsWith(`bodies.${this.selected}.`) ||
          p.startsWith(`links.${this.selected}.`) ||
          p.startsWith(`surfaces.${this.selected}.`) ||
          p.startsWith(`pulleys.${this.selected}.`) ||
          p.startsWith("params.") ||
          p === "frame.px_per_m" ||
          p === "constants.g"),
    )) {
      const value = valueAt(s, path),
        label = el("label", fields),
        caption = el("span", label);
      caption.textContent = `${this.valueLabel(path)} (${value.unit}) · ${t(`mech.${value.status}`)} · ${numberText(value.confidence * 100, 0)}%`;
      const n = el("input", label);
      n.type = "number";
      n.step = "any";
      n.value = value.number === null ? "" : String(value.number);
      n.dataset.valuePath = path;
      n.addEventListener("change", () =>
        this.edit((s) => {
          Object.assign(
            valueAt(s, path),
            userValue(n.value === "" ? null : n.valueAsNumber, value.unit),
          );
          if (path === "frame.px_per_m") calibrate(s);
        }),
      );
    }
    for (const [key, value] of Object.entries(s.params).filter(([k]) =>
      k.startsWith("unplaced_"),
    )) {
      const group = el("fieldset", chips);
      group.dataset.chip = key;
      el("legend", group).textContent =
        `${t("mech.unplaced_value")} ${key.split("_").at(-1)}`;
      input(
        group,
        "value",
        value.number === null ? "" : String(value.number),
        (v) =>
          this.edit((s) =>
            Object.assign(
              s.params[key],
              userValue(v === "" ? null : Number(v), value.unit),
            ),
          ),
        "number",
      );
      input(group, "unit", value.unit, (v) =>
        this.edit((s) => (s.params[key].unit = v)),
      );
      const paths = valuePaths(s).filter(
          (p) =>
            !p.startsWith("params.unplaced_") &&
            valueAt(s, p).unit === value.unit,
        ),
        target = select(
          group,
          "assign_to",
          ["choose_target", ...paths],
          () => {},
        );
      button(group, "assign_value", () =>
        this.edit((s) => assignValue(s, key, target.value)),
      );
    }
  }
  private valueLabel(path: string) {
    const key = `mech.value_${path.split(".").at(-1)}`;
    return t(key) === key ? path : t(key);
  }
  private coordinates(text: string, n: number) {
    const values = text.split(",").map((v) => Number(v.trim()));
    if (values.length !== n || values.some((v) => !Number.isFinite(v)))
      throw new Error("mech.invalid_points");
    return values;
  }
  private polygon(text: string): Point[] {
    const v = JSON.parse(text);
    if (
      !Array.isArray(v) ||
      v.length < 3 ||
      !v.every(
        (p) =>
          Array.isArray(p) &&
          p.length === 2 &&
          p.every((n) => typeof n === "number" && Number.isFinite(n)),
      )
    )
      throw new Error("mech.invalid_points");
    return v;
  }
  private nativePoint(e: PointerEvent): Point {
    const r = this.canvas.getBoundingClientRect(),
      p = this.editing
        ? { left: 0, top: 0 }
        : (this.renderer?.padding ?? { left: 0, top: 0 });
    return [
      ((e.clientX - r.left) * this.canvas.width) /
        (this.renderer?.dpr ?? 1) /
        r.width -
        p.left,
      ((e.clientY - r.top) * this.canvas.height) /
        (this.renderer?.dpr ?? 1) /
        r.height -
        p.top,
    ];
  }
  private down(e: PointerEvent) {
    if (!this.engine || !this.editing) return;
    const p = this.nativePoint(e);
    if (this.tool !== "select") {
      this.points.push(p);
      if (this.tool !== "mask" && this.points.length === 2) this.finishShape();
      else this.render();
      return;
    }
    const radius =
        (22 * this.canvas.width) /
        (this.renderer?.dpr ?? 1) /
        this.canvas.getBoundingClientRect().width,
      hit = handles(this.engine.original)
        .map((h) => ({
          h,
          d: Math.hypot(h.point[0] - p[0], h.point[1] - p[1]),
        }))
        .sort((a, b) => a.d - b.d)
        .find((v) => v.d <= radius);
    if (hit) {
      this.selected = hit.h.object;
      this.drag = { handle: hit.h, point: p };
      this.canvas.setPointerCapture(e.pointerId);
      this.clock.reset();
      this.refreshEditor();
      this.render();
      e.preventDefault();
    }
  }
  private up(e: PointerEvent) {
    if (!this.drag) return;
    const h = this.drag.handle,
      p = this.nativePoint(e);
    this.drag = null;
    this.edit((s) => moveHandle(s, h, p));
  }
  private finishShape() {
    if (!this.engine) return;
    const p = this.points;
    this.points = [];
    if (this.tool === "mask") {
      if (p.length < 3) {
        this.report(new Error("mech.invalid_points"));
        return;
      }
      this.edit((s) => {
        const b = s.bodies.find((b) => b.id === this.selected);
        if (!b) throw new Error("mech.select_body");
        b.mask = p;
      });
    } else if (p.length >= 2) {
      if (this.tool === "repair")
        this.edit((s) => {
          if (
            !s.surfaces.some((v) => v.id === this.selected) &&
            !s.links.some((v) => v.id === this.selected)
          )
            throw new Error("mech.select_line");
          let r = s.repairs.find((r) => r.surface_or_line_id === this.selected);
          if (!r) {
            r = { surface_or_line_id: this.selected, segments: [] };
            s.repairs.push(r);
          }
          r.segments.push(p);
        });
      else if (this.tool !== "select")
        this.edit((s) => {
          this.selected = addLine(
            s,
            this.tool as "rope" | "spring" | "incline" | "floor",
            p[0],
            p.at(-1)!,
          );
        });
    }
    this.render();
  }
  private key(e: KeyboardEvent) {
    if (!this.engine) return;
    if ((e.ctrlKey || e.metaKey) && ["z", "y"].includes(e.key.toLowerCase())) {
      e.preventDefault();
      this.travel(e.key.toLowerCase() === "y" || e.shiftKey);
      return;
    }
    if (e.key === "Escape") {
      this.points = [];
      this.drag = null;
      this.render();
    }
    if (e.key === "Enter" && this.tool === "mask") {
      e.preventDefault();
      this.finishShape();
    }
    if (e.key.startsWith("Arrow") && this.editing) {
      e.preventDefault();
      const h = handles(this.engine.original).find(
        (h) => h.object === this.selected,
      );
      if (h)
        this.edit((s) =>
          moveHandle(s, h, [
            h.point[0] +
              (e.key === "ArrowRight" ? 2 : e.key === "ArrowLeft" ? -2 : 0),
            h.point[1] +
              (e.key === "ArrowDown" ? 2 : e.key === "ArrowUp" ? -2 : 0),
          ]),
        );
    }
    if (e.key === " " && !this.editing) {
      e.preventDefault();
      if (this.clock.playing) this.clock.pause();
      else if (this.engine.trajectory.supported) this.clock.play();
      this.render();
    }
  }
  private render() {
    const engine = this.engine,
      r = this.renderer;
    if (!engine || !r) return;
    const s = engine.original,
      run = engine.trajectory;
    if (this.editing || !run.supported) {
      this.canvas.width = s.image.width * r.dpr;
      this.canvas.height = s.image.height * r.dpr;
      this.canvas.style.width = `${s.image.width}px`;
      this.canvas.style.height = `${s.image.height}px`;
      const ctx = this.canvas.getContext("2d")!;
      ctx.setTransform(r.dpr, 0, 0, r.dpr, 0, 0);
      ctx.drawImage(r.image, 0, 0);
      if (this.editing) {
        const draft = structuredClone(s);
        if (this.drag) moveHandle(draft, this.drag.handle, this.drag.point);
        this.drawEditor(ctx, draft);
      }
    } else
      r.render(
        this.canvas,
        engine.params,
        sample(run, this.clock.displayTime),
        run,
        {
          ...this.options,
          handles: false,
          number: numberText,
          text: (key) => {
            const id = `mech.overlay_${key.replaceAll(" ", "_")}`;
            return t(id) === id ? key : t(id);
          },
        },
      );
    const zoom = this.root.querySelector<HTMLSelectElement>(
        '[data-field="zoom"]',
      )!.value,
      w = this.canvas.width / r.dpr;
    this.canvas.style.width =
      zoom === "fit"
        ? `${Math.min(w, Math.max(200, this.viewport.clientWidth - 4))}px`
        : `${w * Number(zoom)}px`;
    this.canvas.style.height = "auto";
    this.time.textContent = `${numberText(this.clock.displayTime)} / ${numberText(run.duration)} s`;
    this.scrub.value = String(this.clock.displayTime);
    this.refreshPlayback();
    if (run.supported) {
      const state = sample(run, this.clock.displayTime);
      this.readouts.replaceChildren();
      for (const [key, value, unit] of [
        ["kinetic", state.kinetic, "J"],
        ["potential", state.potential, "J"],
        ["momentum_x", state.momentum.x, "kg m/s"],
        ["momentum_y", state.momentum.y, "kg m/s"],
      ] as const)
        el("p", this.readouts).textContent =
          `${t(`mech.${key}`)}: ${numberText(value)} ${unit}`;
      for (const [id, v] of Object.entries(state.velocities))
        el("p", this.readouts).textContent =
          `${nameOf(s, id)} · ${t("mech.velocity")}: (${numberText(v.x)}, ${numberText(v.y)}) m/s`;
      if (!this.tabs.get("graphs")!.hidden)
        drawGraphs(
          this.graph,
          run.times,
          [
            {
              label: t("mech.kinetic"),
              unit: "J",
              values: run.states.map((s) => s.kinetic),
              color: "#165f9e",
              dash: [],
            },
            {
              label: t("mech.potential"),
              unit: "J",
              values: run.states.map((s) => s.potential),
              color: "#a82e18",
              dash: [5, 3],
            },
          ],
          this.clock.displayTime,
          numberText,
          '"Noto Sans Bengali", sans-serif',
        );
    } else this.readouts.textContent = t("mech.unsupported");
    this.root.dataset.ready = "true";
  }
  private drawEditor(ctx: CanvasRenderingContext2D, s: Scene) {
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#005789";
    for (const b of s.bodies) {
      ctx.setLineDash([5, 3]);
      ctx.strokeRect(
        b.bbox[0],
        b.bbox[1],
        b.bbox[2] - b.bbox[0],
        b.bbox[3] - b.bbox[1],
      );
      ctx.setLineDash([]);
      this.line(ctx, b.mask, true);
    }
    for (const sf of s.surfaces) this.line(ctx, sf.polyline);
    for (const l of s.links) this.line(ctx, l.polyline);
    ctx.strokeStyle = "#9a3d00";
    for (const r of s.repairs) for (const p of r.segments) this.line(ctx, p);
    for (const h of handles(s)) {
      ctx.beginPath();
      ctx.arc(...h.point, 8, 0, Math.PI * 2);
      ctx.fillStyle = h.object === this.selected ? "#fff0c2" : "#ffffff";
      ctx.fill();
      ctx.strokeStyle = "#003d70";
      ctx.stroke();
      ctx.font = '14px "Noto Sans Bengali", sans-serif';
      ctx.fillStyle = "#003d70";
      ctx.fillText(
        `${nameOf(s, h.object)} ${h.index ?? h.end ?? ""}`,
        h.point[0] + 12,
        h.point[1] - 10,
      );
    }
    if (this.points.length) {
      ctx.strokeStyle = "#9a3d00";
      this.line(ctx, this.points);
      for (const p of this.points) {
        ctx.beginPath();
        ctx.arc(...p, 4, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }
  private line(ctx: CanvasRenderingContext2D, p: Point[], closed = false) {
    ctx.beginPath();
    p.forEach((v, i) => (i ? ctx.lineTo(...v) : ctx.moveTo(...v)));
    if (closed) ctx.closePath();
    ctx.stroke();
  }
  private frame = () => {
    if (!this.active) return;
    if (this.clock.playing) {
      this.clock.tick(performance.now());
      this.render();
    }
    this.raf = requestAnimationFrame(this.frame);
  };
}
