/// <reference types="vite/client" />
import {
  SimulationClock,
  simulationControls,
  parameterPanel,
  drawGraphs,
  cssToNative,
} from "../../shell";
import { parseScene } from "./validate";
import { BindingEngine } from "./bindings";
import { MechanicsRenderer, type RenderOptions } from "./renderer";
import { archetypes } from "./archetypes";
import { sample } from "./sampling";
import type { Point, Scene } from "./types";
import "./dev.css";

const jsons = import.meta.glob("../../../../fixtures/mechanics/*.json", {
  eager: true,
  import: "default",
});
const images = import.meta.glob("../../../../fixtures/mechanics/*.png", {
  eager: true,
  query: "?url",
  import: "default",
}) as Record<string, string>;
const fixtures = Object.fromEntries(
  Object.entries(jsons).map(([path, json]) => [
    path.split("/").at(-1)!.replace(".json", ""),
    { scene: parseScene(json), url: images[path.replace(".json", ".png")] },
  ]),
);
const root = document.getElementById("mechanics-dev")!;
root.innerHTML = `<h1>Mechanics fixture lab <small>M2</small></h1>
<p class="notice">Synthetic, authored diagrams. Producing a simulation does not establish recognition or physical correctness. No backend is used here.</p>
<div class="fixture-bar"><label>Fixture <select aria-label="Fixture" id="fixture"></select></label>
<strong id="modified" hidden>Modified</strong><button id="back">Back to original</button>
<label>View <select aria-label="View zoom" id="zoom"><option value="1">100% native pixels</option><option value="0.5">50%</option><option value="2">200%</option></select></label></div>
<p id="status" role="status"></p><p id="regime"></p><p id="warnings" role="alert"></p>
<div class="lab-layout"><section aria-label="Simulation"><div id="transport" class="transport"></div>
<div class="canvas-scroll" tabindex="0" aria-label="Diagram viewport, scroll to pan"><canvas id="diagram" aria-label="Mechanics diagram with drag handles"></canvas></div>
<p>Scroll or drag blank paper to pan. Square handles change initial values at t = 0. Geometry handles require Unlock. Dashed paths and labelled vectors distinguish overlays.</p>
<details open><summary>Readouts</summary><pre id="readouts" tabindex="0" aria-label="Simulation readouts"></pre></details>
<section id="graph-section" aria-label="Position velocity and energy graphs"><div class="energy-bars"><label>Kinetic energy <meter id="kinetic" min="0" max="1" value="0"></meter><output id="kinetic-value"></output></label><label>Potential energy <meter id="potential" min="0" max="1" value="0"></meter><output id="potential-value"></output></label></div><canvas id="graphs" width="800" height="450"></canvas></section></section>
<aside aria-label="Parameters"><h2>Parameters</h2><p>Every input carries its status and confidence. Scale-derived distances and times are assumed when scale is assumed.</p><div id="parameters"></div></aside></div>`;
const select = root.querySelector<HTMLSelectElement>("#fixture")!,
  diagram = root.querySelector<HTMLCanvasElement>("#diagram")!;
const parameters = root.querySelector<HTMLElement>("#parameters")!,
  warnings = root.querySelector<HTMLElement>("#warnings")!;
const clock = new SimulationClock(),
  options: RenderOptions = {
    forces: true,
    components: false,
    trail: true,
    original: false,
    marker: false,
    handles: true,
  };
const motion = matchMedia("(prefers-reduced-motion: reduce)");
let engine: BindingEngine,
  renderer: MechanicsRenderer,
  scene: Scene,
  zoom = 1,
  ready = false,
  loading = 0;
let drag: string | null = null,
  pendingPoint: Point | null = null,
  dragScheduled = false;
let renderTimes: number[] = [],
  frameIntervals: number[] = [],
  lastPlayingFrame: number | null = null;
let backgroundHash = "";
let solveRevision = 0;
let pan: { x: number; y: number; left: number; top: number } | null = null;
const viewport = root.querySelector<HTMLElement>(".canvas-scroll")!;
for (const name of Object.keys(fixtures).sort()) {
  const option = new Option(name.replaceAll("_", " "), name);
  select.add(option);
}
const controls = simulationControls(root.querySelector("#transport")!, {
  play() {
    if (engine.trajectory.supported) {
      clock.play();
      render();
    }
  },
  pause() {
    clock.pause();
    render();
  },
  reset() {
    clock.reset();
    render();
  },
  step() {
    clock.step();
    render();
  },
  seek(t) {
    clock.pause();
    clock.seek(t);
    render();
  },
  speed(v) {
    clock.setSpeed(v);
  },
  toggle(key, value) {
    if (key === "graphs")
      root.querySelector<HTMLElement>("#graph-section")!.hidden = !value;
    else (options as unknown as Record<string, boolean>)[key] = value;
    render();
  },
});
function rows() {
  parameterPanel(
    parameters,
    engine.rows(),
    (id, n) => change(() => engine.set(id, n, true)),
    (id) => {
      engine.unlock(id);
      rows();
    },
  );
}
function change(mutate: () => unknown) {
  const revision = ++solveRevision;
  const playing = clock.playing;
  mutate();
  clock.duration = engine.trajectory.duration;
  clock.seek(0);
  if (!engine.trajectory.supported) clock.pause();
  else if (playing) clock.play();
  renderer.fitTrajectory(engine.trajectory, engine.params);
  rows();
  root.querySelector<HTMLElement>("#modified")!.hidden = !engine.modified;
  backgroundHash = renderer.backgroundHash(
    engine.params,
    engine.trajectory.states[0],
  );
  render();
  if (engine.preview)
    requestAnimationFrame(() => {
      if (revision !== solveRevision) return;
      const time = clock.displayTime;
      engine.complete();
      clock.duration = engine.trajectory.duration;
      clock.seek(time);
      renderer.fitTrajectory(engine.trajectory, engine.params);
      render();
    });
}
function render() {
  if (!ready) return;
  const start = performance.now(),
    run = engine.trajectory;
  const time = clock.displayTime;
  controls.update(time, run.duration, clock.playing);
  const warningCodes = [
    ...new Set([
      ...scene.warnings.map((w) => w.code),
      ...run.warnings,
      ...renderer.warnings,
    ]),
  ];
  warnings.textContent = renderer.degraded
    ? `${renderer.warnings.join(" · ")}: composition or canvas extent check failed. Showing the untouched original with overlays only; confidence reduced.`
    : warningCodes.join(" · ");
  const status = root.querySelector<HTMLElement>("#status")!;
  status.textContent = `Authored / synthetic · ${run.supported ? "simulation available" : "unsupported: " + run.reason} · render confidence ${renderer.frame0.mean_absolute_channel === null ? "unverified" : Math.round(renderer.confidence * 100) + "%"}${scene.frame.px_per_m.status === "assumed" ? " · scale, distances and times assumed" : ""}${motion.matches ? " · Reduced motion: still preview by default" : ""}`;
  let regime;
  try {
    regime = archetypes[scene.archetype].regime(scene, engine.params);
  } catch {
    regime = { message: "Invalid or unsupported parameters.", warnings: [] };
  }
  root.querySelector<HTMLElement>("#regime")!.textContent =
    regime.message +
    (regime.warnings.length ? " Assumed values influence this regime." : "");
  if (run.states.length) {
    const st = sample(run, time);
    options.handles = time === 0;
    renderer.render(diagram, engine.params, st, run, options);
    diagram.style.zoom = String(zoom);
    root.querySelector<HTMLElement>("#readouts")!.textContent = JSON.stringify(
      {
        time_s: +time.toFixed(3),
        position_m: st.positions,
        velocity_m_s: st.velocities,
        kinetic_J: st.kinetic,
        potential_J: st.potential,
        total_energy_J: st.kinetic + st.potential,
        momentum_kg_m_s: st.momentum,
        ...run.metrics,
        ...(st.scalars.angle_deg !== undefined
          ? { angle_deg: st.scalars.angle_deg }
          : {}),
        events: run.events,
      },
      null,
      2,
    );
    const id = scene.bodies[0].id,
      states = run.states;
    const axis =
      scene.params.vertical?.number === 1 || scene.archetype === "atwood"
        ? "y"
        : "x";
    for (const key of ["kinetic", "potential"] as const) {
      const meter = root.querySelector<HTMLMeterElement>(`#${key}`)!;
      meter.min = Math.min(0, ...states.map((s) => s[key]));
      meter.max = Math.max(meter.min + 1e-8, ...states.map((s) => s[key]));
      meter.value = st[key];
      root.querySelector<HTMLOutputElement>(`#${key}-value`)!.value =
        `${st[key].toFixed(2)} J`;
    }
    drawGraphs(
      root.querySelector("#graphs")!,
      run.times,
      [
        {
          label: `${id} position ${axis}`,
          unit: "m",
          values: states.map((s) => s.positions[id][axis]),
          color: "#165f9e",
          dash: [],
        },
        {
          label: `${id} velocity ${axis}`,
          unit: "m/s",
          values: states.map((s) => s.velocities[id][axis]),
          color: "#005b42",
          dash: [5, 3],
        },
        {
          label: "Total mechanical energy",
          unit: "J",
          values: states.map((s) => s.kinetic + s.potential),
          color: "#6b318c",
          dash: [2, 3],
        },
      ],
      time,
    );
  } else {
    renderer.showSource(diagram);
    diagram.style.zoom = String(zoom);
    root.querySelector<HTMLElement>("#readouts")!.textContent =
      `Unsupported: ${run.reason}. Source retained; no trajectory was generated.`;
  }
  renderTimes.push(performance.now() - start);
  if (renderTimes.length > 600) renderTimes.shift();
}
async function load(name: string) {
  solveRevision++;
  const token = ++loading;
  ready = false;
  clock.reset();
  select.value = name;
  const fixture = fixtures[name];
  scene = structuredClone(fixture.scene);
  if (new URLSearchParams(location.search).has("unknownType")) {
    scene.bodies[0].type = "unknown_fixture_object";
    scene = parseScene(scene);
  }
  if (
    new URLSearchParams(location.search).has("checkFault") &&
    scene.archetype === "pendulum"
  ) {
    scene.links[0].a.point[0] += 80;
    scene.warnings.push({
      code: "dev_calibration_fault",
      ref: "L1",
      message_key: "mech.dev_calibration_fault",
    });
  }
  engine = new BindingEngine(scene);
  const loaded = await MechanicsRenderer.load(scene, fixture.url);
  if (token !== loading) return;
  renderer = loaded;
  if (engine.trajectory.states.length)
    renderer.renderFrame0Check(engine.trajectory.states[0]);
  renderer.fitTrajectory(engine.trajectory, {});
  backgroundHash = renderer.backgroundHash();
  clock.duration = engine.trajectory.duration;
  renderTimes = [];
  frameIntervals = [];
  rows();
  root.querySelector<HTMLElement>("#modified")!.hidden = true;
  ready = true;
  render();
  const body = engine.trajectory.states.length
    ? archetypes[scene.archetype].layout(scene, {}, engine.trajectory.states[0])
        .bodies[0]
    : null;
  if (body && viewport.scrollWidth > viewport.clientWidth) {
    viewport.scrollLeft = Math.max(
      0,
      body.anchor[0] + renderer.padding.left - viewport.clientWidth / 2,
    );
    viewport.scrollTop = Math.max(
      0,
      body.anchor[1] + renderer.padding.top - viewport.clientHeight / 2,
    );
  }
  // No autoplay: reduced-motion users get the same predicted path and labelled vectors.
}
select.addEventListener("change", () => void load(select.value));
root
  .querySelector("#back")!
  .addEventListener("click", () => change(() => engine.backToOriginal()));
root.querySelector("#zoom")!.addEventListener("change", (event) => {
  zoom = Number((event.target as HTMLSelectElement).value);
  render();
});
motion.addEventListener("change", () => {
  if (motion.matches) clock.pause();
  render();
});
function pointerPoint(event: PointerEvent): Point {
  const rect = diagram.getBoundingClientRect();
  return cssToNative([event.clientX - rect.left, event.clientY - rect.top], {
    x: renderer.padding.left,
    y: renderer.padding.top,
    zoom,
  });
}
diagram.addEventListener("pointerdown", (event) => {
  if (!ready) return;
  const point = pointerPoint(event),
    draw = engine.trajectory.states.length
      ? archetypes[scene.archetype].layout(
          scene,
          engine.params,
          engine.trajectory.states[0],
        )
      : null;
  const handle =
    clock.displayTime === 0 && !options.original && !renderer.degraded
      ? draw?.handles.find(
          (h) => Math.hypot(h.point[0] - point[0], h.point[1] - point[1]) < 22,
        )
      : null;
  const startPan = () => {
    pan = {
      x: event.clientX,
      y: event.clientY,
      left: viewport.scrollLeft,
      top: viewport.scrollTop,
    };
    event.preventDefault();
    diagram.setPointerCapture(event.pointerId);
  };
  if (!handle) {
    startPan();
    return;
  }
  const binding = scene.bindings.find((b) => b.handle === handle.id)!;
  if (binding.class === "geometry" && !engine.unlocked.has(binding.id)) {
    startPan();
    return;
  }
  event.preventDefault();
  clock.pause();
  drag = handle.id;
  diagram.setPointerCapture(event.pointerId);
});
diagram.addEventListener("pointermove", (event) => {
  if (pan) {
    viewport.scrollLeft = pan.left + pan.x - event.clientX;
    viewport.scrollTop = pan.top + pan.y - event.clientY;
    return;
  }
  if (!drag) return;
  pendingPoint = pointerPoint(event);
  if (dragScheduled) return;
  dragScheduled = true;
  requestAnimationFrame(() => {
    dragScheduled = false;
    if (pendingPoint && drag) {
      const point = pendingPoint;
      pendingPoint = null;
      change(() => engine.drag(drag!, point, true));
    }
  });
});
const endDrag = () => {
  pan = null;
  if (pendingPoint && drag) {
    const point = pendingPoint;
    change(() => engine.drag(drag!, point, true));
  }
  drag = null;
  pendingPoint = null;
};
diagram.addEventListener("pointerup", endDrag);
diagram.addEventListener("pointercancel", endDrag);
function frame(timestamp: number) {
  if (ready && clock.playing) {
    if (lastPlayingFrame !== null)
      frameIntervals.push(timestamp - lastPlayingFrame);
    lastPlayingFrame = timestamp;
    if (frameIntervals.length > 600) frameIntervals.shift();
    clock.tick(timestamp);
    render();
  } else lastPlayingFrame = null;
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
// Read-only inspection for fixture QA. User actions exercise real controls/handles.
Object.defineProperty(window, "mechanicsDev", {
  get: () => ({
    ready,
    fixture: select.value,
    time: clock.displayTime,
    playing: clock.playing,
    modified: engine?.modified,
    frame0: renderer?.frame0,
    degraded: renderer?.degraded,
    confidence: renderer?.confidence,
    backgroundHash,
    params: structuredClone(engine?.params ?? {}),
    document: structuredClone(engine?.document ?? {}),
    padding: renderer?.padding,
    dpr: renderer?.dpr,
    renderTimes: [...renderTimes],
    frameIntervals: [...frameIntervals],
    state: engine?.trajectory.states.length
      ? sample(engine.trajectory, clock.displayTime)
      : null,
    draw:
      ready && engine.trajectory.states.length
        ? archetypes[scene.archetype].layout(
            scene,
            engine.params,
            sample(engine.trajectory, clock.displayTime),
          )
        : null,
    duration: engine?.trajectory.duration,
    events: engine?.trajectory.events,
  }),
});
const requested = new URLSearchParams(location.search).get("fixture");
void load(
  requested && fixtures[requested] ? requested : "projectile_ground",
).catch((error) => {
  warnings.textContent = String(error);
});
