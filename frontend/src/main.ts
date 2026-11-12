import {
  renderParameters,
  addInductorControls as renderInductors,
} from "./ui/parameters";
import { renderMeasurements } from "./ui/readouts";
import { renderExplanation } from "./ui/explain";
import { translateApp } from "./ui/translation";
import { createAppState } from "./ui/state";
import { readiness } from "./ui/readiness";
import { organizeWorkspace, activateTab } from "./ui/workspace";
import { flowControls } from "./ui/flow-controls";
import { componentIcon } from "./ui/icons";
import { TextInspector } from "./ui/text-inspector";
import { CanvasEditor } from "./ui/canvas-editor";
import { rebuildTopology } from "./ui/topology";
import { cloneForEdit } from "./ui/edit-history";
import { precheck, draftWarnings } from "./ui/precheck";
import { traceIssues, issueAt, type TraceIssue } from "./ui/trace-issues";
import { UploadWorkspace } from "./ui/upload";
import "./style.css";
import "./workspace.css";
import type { Netlist, Component } from "./types";
import {
  solve,
  voltageTypes,
  supported,
  transient as makeTransient,
} from "./solver/mna";
import { resolveLocal } from "./solver/resolve";
import { Renderer } from "./overlay/renderer";
import {
  language,
  setLanguage,
  t,
  format,
  banglaDigits,
  setDigits,
} from "./i18n";
import {
  History,
  assertNetlist,
  componentTypes,
  mergeNodes,
  splitTerminal,
  attachTerminal,
  addComponent,
  addWire,
  cutWire,
  normalizeNetlist,
} from "./ui/editor";
import rcFixture from "../../fixtures/rc_charge.json";

import { $, esc, options } from "./ui/dom";
import shell from "./ui/shell.html?raw";
import { ImageStore, selfContained, withoutImage } from "./ui/image-store";
const appState = createAppState();
function renderControls() {
  renderParameters(appState);
}
function addInductorControls() {
  renderInductors(appState);
}
function renderReadouts() {
  renderMeasurements(
    appState,
    renderer,
    () => canvasEditor?.update(),
    renderExplanations,
  );
}
function renderExplanations() {
  renderExplanation(appState);
}
function translate() {
  translateApp(appState, () => {
    uploadWorkspace.translate();
    textInspector?.translate();
    canvasEditor?.translate();
  });
}
const images = new ImageStore();
const root = $("app");
root.innerHTML = shell;

let textInspector: TextInspector | undefined;
let canvasEditor: CanvasEditor | undefined;
const history = new History(),
  renderer = new Renderer($<HTMLCanvasElement>("overlay"));
const val = (id: string) => $<HTMLInputElement>(id).value,
  check = (id: string) => $<HTMLInputElement>(id).checked;

function toast(message: string) {
  $("toast").textContent = message;
  $("toast").style.display = "block";
  window.setTimeout(() => ($("toast").style.display = "none"), 5000);
}

function loadNet(next: Netlist, name: string) {
  textInspector?.reset();
  appState.editing = false;
  renderer.edit = false;
  renderer.paused = !appState.playing;
  root.classList.remove("editing");
  next = normalizeNetlist(next);
  assertNetlist(next);
  const previousUrl = appState.net?.image.path;
  if (previousUrl !== next.image.path && !next.image.path.startsWith("blob:"))
    images.clear();
  next.image.path = images.fromData(next.image.path);
  appState.net = structuredClone(next);
  appState.automatic = structuredClone(next);
  appState.title = name;
  appState.selected = appState.net.components[0]?.id || "";
  history.undoStack = [];
  history.redoStack = [];
  appState.state = {};
  appState.time = 0;
  appState.graphHistory.length = 0;
  appState.withoutShort = null;
  appState.mode = appState.net.components.some((c) =>
    ["capacitor", "inductor"].includes(c.type),
  )
    ? "transient"
    : "steady";
  $<HTMLSelectElement>("analysis-mode").value = appState.mode;
  appState.duration = makeTransient(appState.net, undefined, 2).duration;
  setTimeStep();
  renderer.setImage(appState.net.image.path);
  $<HTMLInputElement>("zoom").value = "100";
  canvasEditor?.reset();
  refresh();
  document.dispatchEvent(new Event("workspace:loaded"));
}
function recompute() {
  const start = performance.now();
  try {
    appState.solution = solve(
      appState.net,
      appState.mode === "transient" ? appState.dt : undefined,
      appState.state,
    );
    appState.lastSolve = performance.now() - start;
  } catch {
    toast(t("error"));
    throw Error("Solve failed");
  }
}
function refresh(skipControls = false, reuseSolution = false) {
  if (!appState.net) return;
  root.dataset.provenance = appState.net.meta.provenance;
  if (!appState.editing && !reuseSolution) recompute();
  $("circuit-title").textContent = appState.title;
  $("parameter-count").textContent = String(appState.net.components.length);
  if (!skipControls) {
    renderControls();
    addInductorControls();
  }
  renderReadouts();
  graph();
  renderEditor();
  translate();
  canvasEditor?.update();
}
function mutate(fn: (n: Netlist) => void, skipControls = false) {
  const before = cloneForEdit(appState.net);
  try {
    fn(appState.net);
    if (appState.editing) rebuildTopology(appState.net);
    appState.net.warnings = appState.net.warnings.filter(
      (w) =>
        !(
          w.code === "assumed_value" &&
          appState.net.components.some(
            (c) => c.id === w.ref && c.value.status !== "assumed",
          )
        ),
    );
    assertNetlist(appState.net);
    if (!appState.editing && appState.mode === "transient") {
      appState.duration = Math.max(
        appState.duration,
        appState.time + makeTransient(appState.net, undefined, 2).duration,
      );
      setTimeStep();
    }
    history.push(before, appState.net);
    refresh(skipControls);
    if (appState.editing) canvasEditor?.changed();
  } catch {
    appState.net = before;
    if (!appState.editing) recompute();
    toast(t("error"));
  }
}
function runEdited() {
  try {
    rebuildTopology(appState.net);
    assertNetlist(appState.net);
    const checkResult = precheck(appState.net, renderer.ghosts);
    if (!checkResult.closed) {
      toast(t("edit.run_failed"));
      return false;
    }
    appState.net.warnings = draftWarnings(appState.net);
    if (check("keep")) appState.net = resolveLocal(appState.net);
    appState.time = 0;
    appState.state = {};
    setTimeStep();
    recompute();
    appState.net.meta.provenance = "edited";
    appState.net.meta.degraded = !checkResult.ready;
    appState.editing = false;
    root.classList.remove("editing");
    document.dispatchEvent(
      new CustomEvent("workspace:editing", { detail: false }),
    );
    renderer.edit = false;
    renderer.paused = !appState.playing;
    appState.time = 0;
    appState.state = {};
    appState.graphHistory.length = 0;
    refresh(false, true);
    return true;
  } catch {
    toast(t("edit.run_failed"));
    return false;
  }
}
function setTimeStep() {
  const resistances = appState.net.components
    .filter((c) =>
      ["resistor", "rheostat", "potentiometer", "lamp"].includes(c.type),
    )
    .map((c) => Math.max(1e-9, c.value.number || 10));
  const taus = appState.net.components
    .filter((c) => ["capacitor", "inductor"].includes(c.type))
    .map((c) =>
      c.type === "capacitor"
        ? (c.value.number || 1e-5) *
          (resistances.length ? Math.min(...resistances) : 10)
        : (c.value.number || 0.1) /
          (resistances.length ? Math.max(...resistances) : 10),
    );
  appState.dt = Math.max(
    appState.duration / 5000,
    Math.min(appState.duration / 500, ...taus.map((v) => v / 100)),
  );
}

function renderEditor() {
  if (!appState.editing) return;
  const c = appState.net.components.find((c) => c.id === appState.selected);
  $("component-select").innerHTML = options(
    appState.net.components.map((c) => ({ value: c.id, label: c.id })),
    appState.selected,
  );
  $("component-type").innerHTML = options(
    componentTypes.map((type) => ({ value: type, label: t("type." + type) })),
    c?.type,
  );
  const nodeOpts = appState.net.nodes.map((n) => ({
    value: n.id,
    label: n.id + (n.is_ground ? " ⏚" : ""),
  }));
  $("terminal-a").innerHTML = options(nodeOpts, c?.terminals[0].node);
  $("terminal-b").innerHTML = options(nodeOpts, c?.terminals[1].node);
  $("merge-a").innerHTML = options(nodeOpts);
  $("merge-b").innerHTML = options(nodeOpts, appState.net.nodes[1]?.id);
  const pointOpts = appState.net.wire_graph.points.map((p) => ({
    value: p.id,
    label: p.id + " / " + p.node,
  }));
  for (const id of ["wire-a", "wire-b", "terminal-point"])
    $(id).innerHTML = options(pointOpts);
  $("wire-select").innerHTML = options(
    appState.net.wire_graph.segments.map((s) => ({
      value: s.id,
      label: s.id + ": " + s.from + " → " + s.to,
    })),
  );
  $("netlist-json").textContent = JSON.stringify(appState.net, null, 2);
  $<HTMLTextAreaElement>("netlist-json").value = JSON.stringify(
    appState.net,
    null,
    2,
  );
  $<HTMLButtonElement>("undo").disabled = !history.undoStack.length;
  $<HTMLButtonElement>("redo").disabled = !history.redoStack.length;
}
function select(id: string) {
  appState.selected = id;
  activateTab("selected");
  renderReadouts();
  renderEditor();
}
function toggleShort() {
  mutate((n) => {
    const existing = n.components.find((c) => c.id === "SHORT");
    if (existing) {
      n.components = n.components.filter((c) => c.id !== "SHORT");
      return;
    }
    const c = n.components.find((c) => c.id === appState.selected);
    if (!c) return;
    appState.withoutShort = Math.abs(
      appState.solution.components[
        appState.net.components.find((c) => voltageTypes.has(c.type))?.id || ""
      ]?.current || 0,
    );
    const short = structuredClone(c);
    short.id = "SHORT";
    short.type = "switch";
    short.value = {
      number: 0.001,
      unit: "ohm",
      status: "user",
      source: "user",
      confidence: 1,
    };
    short.polarity = null;
    short.switch_closed = true;
    short.virtual = true;
    short.terminals = short.terminals.map((t, k) => ({
      ...t,
      id: `SHORT.${k ? "b" : "a"}`,
    })) as Component["terminals"];
    short.bbox = [c.bbox[0], c.bbox[1] - 24, c.bbox[2], c.bbox[3] - 24];
    n.components.push(short);
  });
}
function parameterChange(id: string, value: number) {
  if (!Number.isFinite(value)) return;
  mutate((n) => {
    const c = n.components.find((c) => c.id === id)!;
    c.value.number = value;
    c.value.status = "user";
    c.value.source = "user";
    c.value.confidence = 1;
  }, true);
  document.querySelectorAll<HTMLInputElement>(`[data-param]`).forEach((el) => {
    if (el.dataset.param === id && el !== document.activeElement)
      el.value = String(value);
  });
  document.querySelectorAll<HTMLElement>("[data-component]").forEach((el) => {
    if (el.dataset.component === id) {
      const badge = el.querySelector<HTMLElement>(".status");
      if (badge) {
        badge.className = "status user";
        badge.textContent = t("user");
      }
    }
  });
  if (check("keep") && appState.net.constraints.length)
    void resolveConstraints();
}
async function resolveConstraints() {
  if (appState.editing) return;
  appState.net = resolveLocal(appState.net);
  refresh();
}

$("controls").addEventListener("input", (e) => {
  const el = e.target as HTMLInputElement;
  if (el.dataset.param) parameterChange(el.dataset.param, Number(el.value));
});
$("controls").addEventListener("change", (e) => {
  const el = e.target as HTMLInputElement;
  if (el.dataset.internal)
    mutate((n) => {
      n.components.find(
        (c) => c.id === el.dataset.internal,
      )!.internal_resistance = Math.max(0, Number(el.value));
    });
  if (el.dataset.initial)
    mutate((n) => {
      const c = n.components.find((c) => c.id === el.dataset.initial)!;
      c.initial_voltage = Number(el.value);
      appState.state[c.id] = c.initial_voltage;
      appState.time = 0;
      appState.graphHistory.length = 0;
    });
  if (el.dataset.initialCurrent)
    mutate((n) => {
      const c = n.components.find((c) => c.id === el.dataset.initialCurrent)!;
      c.initial_current = Number(el.value);
      appState.state[c.id] = c.initial_current;
      appState.time = 0;
      appState.graphHistory.length = 0;
    });
});
$("controls").addEventListener("click", (e) => {
  const button = (e.target as HTMLElement).closest<HTMLButtonElement>(
    "[data-action]",
  );
  if (!button) return;
  const id = button.dataset.id!;
  if (button.dataset.action === "select") select(id);
  else
    mutate((n) => {
      const c = n.components.find((c) => c.id === id)!;
      if (button.dataset.action === "switch")
        c.switch_closed = !c.switch_closed;
      else
        c.polarity = {
          positive_terminal:
            c.terminals[
              c.polarity?.positive_terminal === c.terminals[0].id ? 1 : 0
            ].id,
        };
    });
});
$("readout").addEventListener("click", (e) => {
  const tr = (e.target as HTMLElement).closest<HTMLElement>("[data-select]");
  if (tr) select(tr.dataset.select!);
});
$("readout").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const id = (e.target as HTMLElement).dataset.select;
    if (id) select(id);
  }
});
$("inspector").addEventListener("click", (e) => {
  if ((e.target as HTMLElement).id === "short-add") toggleShort();
});
function focusIssue(issue: TraceIssue) {
  if (canvasEditor) {
    canvasEditor.focusIssue(issue);
    return;
  }
  renderer.highlightedIssue = issue.id;
  appState.editing = true;
  renderer.edit = true;
  root.classList.add("editing");
  if (issue.code === "missing_part") appState.interaction = "add";
  const near = [...appState.net.components].sort(
    (a, b) =>
      Math.hypot(a.bbox[0] - issue.xy[0], a.bbox[1] - issue.xy[1]) -
      Math.hypot(b.bbox[0] - issue.xy[0], b.bbox[1] - issue.xy[1]),
  )[0];
  if (near) appState.selected = near.id;
  renderEditor();
  translate();
  renderer.canvas.scrollIntoView({ block: "center", behavior: "smooth" });
  toast(t("warn." + issue.code));
}
$("notices").addEventListener("click", (e) => {
  const id = (e.target as HTMLElement).closest<HTMLElement>("[data-issue]")
    ?.dataset.issue;
  const issue = renderer.issues.find((i) => i.id === id);
  if (issue) focusIssue(issue);
});
$("language").onclick = () => {
  setLanguage(language === "en" ? "bn" : "en");
  refresh();
};
$<HTMLInputElement>("digits").checked = banglaDigits;
$("digits").onchange = () => {
  setDigits(check("digits"));
  refresh();
};
$("edit").onclick = () => {
  appState.editing = !appState.editing;
  root.classList.toggle("editing", appState.editing);
  renderer.edit = appState.editing;
  renderEditor();
  translate();
};
$("export").onclick = () => renderer.export();
$("save").onclick = async () => {
  const a = document.createElement("a"),
    url = URL.createObjectURL(
      new Blob([JSON.stringify(await selfContained(appState.net), null, 2)], {
        type: "application/json",
      }),
    );
  a.href = url;
  a.download = "netlist.json";
  a.click();
  URL.revokeObjectURL(url);
};
$("load").onclick = () => $("json-upload").click();
$("json-upload").onchange = async () => {
  const file = $<HTMLInputElement>("json-upload").files?.[0];
  if (file)
    try {
      loadNet(JSON.parse(await file.text()), file.name);
    } catch {
      toast(t("error"));
    }
};
$("image-load").onclick = () => $("image-upload").click();
$("image-upload").onchange = () => {
  const file = $<HTMLInputElement>("image-upload").files?.[0];
  if (file) {
    if (appState.objectUrl) URL.revokeObjectURL(appState.objectUrl);
    appState.objectUrl = images.fromBlob(file);
    appState.imageBlob = file;
    appState.net.image.path = appState.objectUrl;
    renderer.setImage(appState.objectUrl);
  }
};
$("play").onclick = () => {
  appState.playing = !appState.playing;
  renderer.paused = appState.editing || !appState.playing;
  translate();
};
$("restart").onclick = () => {
  appState.state = {};
  appState.time = 0;
  appState.graphHistory.length = 0;
  refresh();
};
$("analysis-mode").onchange = () => {
  appState.mode = val("analysis-mode");
  refresh();
};
$("direction").onchange = () =>
  (renderer.electron = val("direction") === "electron");
$("show-image").onchange = () => (renderer.showImage = check("show-image"));
$("zoom").oninput = () => {
  renderer.zoom = Number(val("zoom")) / 100;
  $("canvas-shell").style.width = val("zoom") + "%";
};
function undoEdit() {
  const prev = history.undo(appState.net);
  if (prev) {
    appState.net = prev;
    refresh();
    if (appState.editing) canvasEditor?.changed();
  }
}
$("undo").onclick = undoEdit;
function redoEdit() {
  const next = history.redo(appState.net);
  if (next) {
    appState.net = next;
    refresh();
    if (appState.editing) canvasEditor?.changed();
  }
}
$("redo").onclick = redoEdit;
function resetEdit() {
  history.push(appState.net, appState.automatic);
  appState.net = cloneForEdit(appState.automatic);
  appState.state = {};
  appState.time = 0;
  refresh();
  if (appState.editing) canvasEditor?.changed();
}
$("reset-auto").onclick = resetEdit;
$("component-select").onchange = () => select(val("component-select"));
$("component-type").onchange = () =>
  mutate((n) => {
    n.components.find((c) => c.id === appState.selected)!.type =
      val("component-type");
  });
for (const [id, k] of [
  ["terminal-a", 0],
  ["terminal-b", 1],
] as const)
  $(id).onchange = () => {
    const node = val(id);
    mutate((n) =>
      attachTerminal(
        n,
        n.components.find((c) => c.id === appState.selected)!,
        k,
        node,
      ),
    );
  };
$("snap-terminal").onclick = () => {
  const point = val("terminal-point");
  const p = appState.net.wire_graph.points.find((p) => p.id === point);
  if (p)
    mutate((n) =>
      attachTerminal(
        n,
        n.components.find((c) => c.id === appState.selected)!,
        0,
        p.node,
        p.id,
      ),
    );
};
$("split").onclick = () =>
  mutate((n) =>
    splitTerminal(n, n.components.find((c) => c.id === appState.selected)!, 0),
  );
$("merge").onclick = () => {
  const a = val("merge-a"),
    b = val("merge-b");
  mutate((n) => mergeNodes(n, a, b));
};
$("delete").onclick = () =>
  mutate((n) => {
    const c = n.components.find((c) => c.id === appState.selected);
    if (!c) return;
    const ids = c.terminals.map((t) => t.id);
    n.components = n.components.filter((c) => c.id !== appState.selected);
    n.wire_graph.points = n.wire_graph.points.filter(
      (p) => !ids.includes(p.id),
    );
    n.wire_graph.segments = n.wire_graph.segments.filter(
      (s) => !ids.includes(s.from) && !ids.includes(s.to),
    );
    appState.selected = n.components[0]?.id || "";
  });
$("add-type").innerHTML = options(
  componentTypes.map((type) => ({ value: type, label: t("type." + type) })),
);
$("add-coordinates").onclick = () => {
  const type = val("add-type"),
    xy: [number, number] = [Number(val("place-x")), Number(val("place-y"))];
  mutate((n) => {
    appState.selected = addComponent(n, type, xy).id;
  });
};
$("add").onclick = () => {
  appState.interaction = "add";
  toast(t("place"));
};
$("place").onclick = () => {
  appState.interaction = "place";
  toast(t("place"));
};
$("wire-add").onclick = () => {
  const a = val("wire-a"),
    b = val("wire-b");
  mutate((n) => {
    addWire(n, a, b);
  });
};
$("wire-delete").onclick = () => {
  const id = val("wire-select");
  mutate((n) => {
    cutWire(n, id);
  });
};
let bendWire = "";
$("wire-route").onclick = () => {
  appState.interaction = "bend";
  bendWire = val("wire-select");
  toast(t("wire_route"));
};
$("apply").onclick = () => {
  try {
    const next = JSON.parse(val("netlist-json"));
    assertNetlist(next);
    history.push(appState.net);
    appState.net = next;
    refresh();
  } catch {
    toast(t("error"));
  }
};
$("overlay").addEventListener("keydown", (e) => {
  const index = appState.net.components.findIndex(
    (c) => c.id === appState.selected,
  );
  if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
    e.preventDefault();
    const next =
      (index +
        (e.key === "ArrowRight" ? 1 : -1) +
        appState.net.components.length) %
      appState.net.components.length;
    select(appState.net.components[next].id);
  }
  if (e.key === "Enter") {
    e.preventDefault();
    activateTab("selected");
  }
});
$("overlay").addEventListener("mousemove", (e) => {
  const [x, y] = renderer.clientToImage(e.clientX, e.clientY, appState.net);
  const c = renderer.hit(x, y, appState.net),
    r = c && appState.solution.components[c.id];
  renderer.canvas.title =
    c && !supported.has(c.type)
      ? t("ui.unknown_block", { type: t("type." + c.type) })
      : c && r
        ? t("ui.tooltip", {
            part: c.id,
            voltage: format(r.v_drop, "V"),
            current: format(r.current, "A"),
            power: format(r.power, "W"),
          })
        : t("ui.canvas");
});
$("overlay").addEventListener("click", (e) => {
  const [x, y] = renderer.clientToImage(e.clientX, e.clientY, appState.net);
  const issue = issueAt(
    renderer.issues,
    x,
    y,
    10 / renderer.view(appState.net).scale,
  );
  if (issue && appState.interaction === "none") {
    focusIssue(issue);
    return;
  }
  if (appState.interaction === "add") {
    const type = val("add-type");
    mutate((n) => {
      appState.selected = addComponent(n, type, [x, y]).id;
    });
  } else if (appState.interaction === "place") {
    mutate((n) => {
      const c = n.components.find((c) => c.id === appState.selected);
      if (!c) return;
      const dx = x - (c.bbox[0] + c.bbox[2]) / 2,
        dy = y - (c.bbox[1] + c.bbox[3]) / 2;
      c.bbox = c.bbox.map((v, k) => v + (k % 2 ? dy : dx)) as Component["bbox"];
      for (const t of c.terminals) {
        t.xy = [t.xy[0] + dx, t.xy[1] + dy];
        const p = n.wire_graph.points.find((p) => p.id === t.id);
        if (p) p.xy = [...t.xy];
        for (const s of n.wire_graph.segments) {
          if (s.from === t.id) s.polyline[0] = [...t.xy];
          if (s.to === t.id) s.polyline[s.polyline.length - 1] = [...t.xy];
        }
      }
    });
  } else if (appState.interaction === "bend")
    mutate((n) => {
      const wire = n.wire_graph.segments.find((s) => s.id === bendWire);
      wire?.polyline.splice(wire.polyline.length - 1, 0, [x, y]);
    });
  else {
    const c = renderer.hit(x, y, appState.net);
    if (c) {
      select(c.id);
      if (c.type === "switch" && !appState.editing)
        mutate((n) => {
          n.components.find((c2) => c2.id === c.id)!.switch_closed =
            !c.switch_closed;
        });
    }
  }
  appState.interaction = "none";
});
const uploadWorkspace = new UploadWorkspace(
  $("upload-name").parentElement!,
  (result, file) => {
    appState.imageBlob = file;
    appState.regions = result.regions?.map((r) => r.netlist) || [
      result.netlist,
    ];
    loadNet(
      result.netlist,
      result.provenance === "demo_fallback"
        ? t("upload.demo_title")
        : file.name,
    );
    result.netlist.image.path = appState.net.image.path;
    result.source_image =
      result.provenance === "demo_fallback"
        ? images.fromData(result.source_image || "")
        : appState.net.image.path;
    for (const region of appState.regions)
      region.image.path = images.fromData(region.image.path);
    if (result.provenance === "demo_fallback") renderer.setImage("");
    textInspector?.setTexts(result.diagnostics?.texts || []);
    renderer.ghosts = result.diagnostics?.trace?.ghosts || [];
    renderReadouts();
  },
  () => ({
    problem_text: val("problem"),
    lang: language,
    style: val("style"),
    use_label_reader: String(check("ai-reader")),
  }),
);
organizeWorkspace();
flowControls(renderer);
const labelControl = document.createElement("label");
labelControl.className = "row";
const labelText = document.createElement("span");
labelText.dataset.i18n = "layout.labels";
labelControl.append(labelText);
const labelMode = document.createElement("select");
labelMode.id = "label-mode";
labelMode.setAttribute("aria-label", t("layout.labels"));
for (const mode of ["compact", "full", "off"] as const) {
  const option = document.createElement("option");
  option.value = mode;
  option.dataset.i18n = "layout.labels_" + mode;
  labelMode.append(option);
}
labelMode.onchange = () => {
  renderer.labelMode = labelMode.value as typeof renderer.labelMode;
};
labelControl.append(labelMode);
document.querySelector(".canvas-toolbar")!.append(labelControl);
document.addEventListener("workspace:source", (event) => {
  const { id, value } = (event as CustomEvent<{ id: string; value: number }>)
    .detail;
  parameterChange(id, value);
});
textInspector = new TextInspector(renderer, {
  net: () => appState.net,
  selected: () => appState.selected,
  optIn: () => check("ai-reader"),
  notify: toast,
  apply: (id, number, unit) =>
    mutate((n) => {
      const c = n.components.find((c) => c.id === id);
      if (c)
        c.value = {
          number,
          unit,
          status: "user",
          source: "user",
          confidence: 1,
          unit_inferred: false,
        };
    }),
});
canvasEditor = new CanvasEditor(renderer, {
  net: () => appState.net,
  automatic: () => appState.automatic,
  selected: () => appState.selected,
  editing: () => appState.editing,
  select,
  mutate,
  run: runEdited,
  undo: undoEdit,
  redo: redoEdit,
  reset: resetEdit,
  notify: toast,
  readArea: () =>
    document
      .querySelector<HTMLButtonElement>("[data-testid=ocr-read-area]")!
      .click(),
  setEditing: (value) => {
    appState.editing = value;
    renderer.edit = value;
    renderer.paused = value || !appState.playing;
    root.classList.toggle("editing", value);
    document.dispatchEvent(
      new CustomEvent("workspace:editing", { detail: value }),
    );
    if (value) rebuildTopology(appState.net);
    refresh();
  },
});
function upload(file: File) {
  return uploadWorkspace.start(file);
}
$("dropzone").onkeydown = (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    $("upload").click();
  }
};
$("upload").onchange = () => {
  const file = $<HTMLInputElement>("upload").files?.[0];
  if (file) void upload(file);
};
for (const event of ["dragenter", "dragover"])
  $("dropzone").addEventListener(event, (e) => {
    e.preventDefault();
    $("dropzone").classList.add("drag");
  });
$("dropzone").addEventListener("dragleave", () =>
  $("dropzone").classList.remove("drag"),
);
$("dropzone").addEventListener("drop", (e) => {
  e.preventDefault();
  $("dropzone").classList.remove("drag");
  const file = e.dataTransfer?.files[0];
  if (file) void upload(file);
});
$("regions").onclick = (e) => {
  const button = (e.target as HTMLElement).closest<HTMLButtonElement>(
    "[data-region]",
  );
  if (button) {
    loadNet(appState.regions[Number(button.dataset.region)], appState.title);
    $("regions")
      .querySelectorAll("button")
      .forEach((el) => el.classList.toggle("active", el === button));
  }
};
$("correction-save").onclick = async () => {
  if (!check("correction-opt")) {
    toast(t("corrections"));
    return;
  }
  try {
    const data = new FormData();
    let blob = appState.net.image.path
      ? await (await fetch(appState.net.image.path)).blob()
      : appState.imageBlob;
    if (!blob) throw Error("Missing image");
    data.append("image", blob, "source-image");
    data.append("netlist", JSON.stringify(withoutImage(appState.net)));
    data.append("opt_in", "true");
    data.append("texts", JSON.stringify(textInspector?.corrections() || []));
    const r = await fetch("/api/corrections", { method: "POST", body: data });
    if (!r.ok) throw Error("API");
    toast(t("saved"));
  } catch {
    toast(t("analysis_error"));
  }
};

function rcDemo() {
  const n = structuredClone(rcFixture.netlist) as unknown as Netlist;
  n.image = { path: "", width: 640, height: 360 };
  const coords: Record<string, [[number, number], [number, number]]> = {
    V1: [
      [100, 150],
      [100, 210],
    ],
    R1: [
      [240, 80],
      [320, 80],
    ],
    C1: [
      [480, 150],
      [480, 210],
    ],
  };
  for (const c of n.components) {
    c.terminals.forEach((t, k) => (t.xy = coords[c.id][k]));
    const [a, b] = coords[c.id];
    c.bbox = [
      Math.min(a[0], b[0]) - 10,
      Math.min(a[1], b[1]) - 10,
      Math.max(a[0], b[0]) + 10,
      Math.max(a[1], b[1]) + 10,
    ];
  }
  n.wire_graph.points = n.components.flatMap((c) =>
    c.terminals.map((t) => ({
      id: t.id,
      xy: t.xy,
      node: t.node,
      kind: "terminal",
    })),
  );
  n.wire_graph.segments = [
    {
      id: "w1",
      from: "V1.a",
      to: "R1.a",
      polyline: [
        [100, 150],
        [100, 80],
        [240, 80],
      ],
      node: "p",
      confidence: 1,
    },
    {
      id: "w2",
      from: "R1.b",
      to: "C1.a",
      polyline: [
        [320, 80],
        [480, 80],
        [480, 150],
      ],
      node: "m",
      confidence: 1,
    },
    {
      id: "w3",
      from: "C1.b",
      to: "V1.b",
      polyline: [
        [480, 210],
        [480, 280],
        [100, 280],
        [100, 210],
      ],
      node: "g",
      confidence: 1,
    },
  ];
  return n;
}
function graph() {
  const canvas = $<HTMLCanvasElement>("graph"),
    ctx = canvas.getContext("2d")!,
    dpr = devicePixelRatio || 1,
    w = canvas.clientWidth,
    h = 120;
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  ctx.scale(dpr, dpr);
  ctx.strokeStyle = "#e5e9df";
  ctx.lineWidth = 1;
  for (let y = 20; y < 110; y += 30) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
  const dynamic = appState.net.components.find(
    (c) => c.type === "capacitor" || c.type === "inductor",
  );
  if (!dynamic) {
    $("graph-caption").textContent = t("no_dynamic");
    return;
  }
  const maxT = Math.max(appState.duration, appState.time, 0.001);
  for (const [key, color] of [
    ["v", "#318c92"],
    ["i", "#db6839"],
  ] as const) {
    const max = Math.max(
      ...appState.graphHistory.map((p) => Math.abs(p[key])),
      1e-15,
    );
    ctx.beginPath();
    appState.graphHistory.forEach((p, j) => {
      const x = (p.time / maxT) * w,
        y = 100 - (p[key] / max) * 75;
      if (j === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  $("graph-caption").textContent =
    `${dynamic.id} · ${t("voltage")} / ${t("current")} · ${format(maxT, "s")}`;
}
let lastFrame = performance.now(),
  frameCount = 0;
function frame(now: number) {
  const elapsed = Math.min((now - lastFrame) / 1000, 0.1);
  lastFrame = now;
  if (appState.net && appState.solution) {
    if (
      !appState.editing &&
      appState.mode === "transient" &&
      appState.playing &&
      appState.time < appState.duration
    ) {
      const physical = (elapsed * Number(val("speed")) * appState.duration) / 8;
      const count = Math.max(1, Math.ceil(physical / appState.dt)),
        step = physical / count;
      for (let i = 0; i < count; i++) {
        appState.solution = solve(appState.net, step, appState.state);
        appState.state = appState.solution.state;
        appState.time += step;
      }
      const dynamic = appState.net.components.find(
        (c) => c.type === "capacitor" || c.type === "inductor",
      );
      if (dynamic) {
        const r = appState.solution.components[dynamic.id];
        appState.graphHistory.push({
          time: appState.time,
          v: r.v_drop,
          i: r.current,
        });
        if (appState.graphHistory.length > 1000) appState.graphHistory.shift();
      }
      if (frameCount % 5 === 0) {
        renderReadouts();
        graph();
      }
    }
    renderer.render(appState.net, appState.solution, now);
  }
  frameCount++;
  requestAnimationFrame(frame);
}
async function init() {
  translate();
  try {
    const response = await fetch("/api/health");
    appState.online = response.ok;
    if (appState.online)
      appState.modelStatus = readiness(await response.json());
  } catch {}
  const demos: { id: string; title: string; netlist: string }[] = await (
    await fetch("/demos/index.json")
  ).json();
  $("demo").innerHTML = options(
    [
      ...demos.map((d) => ({ value: d.netlist, label: d.title })),
      { value: "rc", label: "RC · charging & discharging" },
    ],
    "/demos/mixed-network.json",
  );
  $("demo").onchange = async () => {
    const path = val("demo");
    loadNet(
      path === "rc" ? rcDemo() : await (await fetch(path)).json(),
      path === "rc"
        ? "RC · charging & discharging"
        : demos.find((d) => d.netlist === path)?.title || path,
    );
    appState.regions = [];
    uploadWorkspace.example();
    $("regions").innerHTML = "";
  };
  loadNet(
    await (await fetch("/demos/mixed-network.json")).json(),
    "Mixed network",
  );
  graph();
  document.addEventListener("workspace:tab", () => {
    graph();
    renderExplanations();
  });
  window.setInterval(async () => {
    try {
      const r = await fetch("/api/health");
      appState.online = r.ok;
      if (appState.online) appState.modelStatus = readiness(await r.json());
    } catch {
      appState.online = false;
    }
    translate();
  }, 5000);
  requestAnimationFrame(frame);
}
void init();
