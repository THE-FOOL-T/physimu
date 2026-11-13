import type { Scene, Params } from "./types";
import type { EditState } from "./authoring";
import { parseScene, valueAt } from "./validate";
import { BindingEngine } from "./bindings";
import {
  interactionBindings,
  scalarVelocityPath,
} from "./interaction-bindings";

export interface MechanicsProject {
  format: "augphys-mechanics-project";
  version: 2;
  scene: Scene;
  recognition_scene: Scene;
  current_scene: Scene;
  source_image: string;
  parameter_overrides: Params;
  unlocked_geometry: string[];
}
export function restoreEngine(state: EditState) {
  const engine = new BindingEngine(
    parseScene(state.scene),
    state.recognition ? parseScene(state.recognition) : state.scene,
  );
  for (const id of state.unlocked) {
    if (typeof id !== "string") throw new Error("mech.invalid_project");
    engine.unlock(id);
  }
  // Apply together so dependent limits (e.g. friction/length) are resolved consistently.
  const values: Record<string, number> = {};
  for (const [path, n] of Object.entries(state.overrides)) {
    const binding = engine.original.bindings.find((b) => b.path === path);
    if (!binding || typeof n !== "number" || !Number.isFinite(n))
      throw new Error("mech.invalid_project");
    if (binding.class === "geometry") engine.unlock(binding.id);
    values[binding.id] = n;
  }
  // Dependent controls must read the final saved values regardless of JSON key order.
  engine.params = { ...state.overrides };
  if (Object.keys(values).length) engine.setMany(values);
  engine.unlocked = new Set(state.unlocked);
  if (
    JSON.stringify(Object.entries(engine.params).sort()) !==
    JSON.stringify(Object.entries(state.overrides).sort())
  )
    throw new Error("mech.override_bounds");
  return engine;
}
export function project(
  engine: BindingEngine,
  image: string,
): MechanicsProject {
  return {
    format: "augphys-mechanics-project",
    version: 2,
    scene: structuredClone(engine.original),
    recognition_scene: structuredClone(engine.recognition),
    current_scene: structuredClone(engine.document),
    source_image: image,
    parameter_overrides: { ...engine.params },
    unlocked_geometry: [...engine.unlocked],
  };
}
/** Pure contract validation, also used by unit tests. Image decoding follows before installation. */
export function parseProject(input: unknown): MechanicsProject {
  if (!input || typeof input !== "object")
    throw new Error("mech.invalid_project");
  const p = input as Omit<MechanicsProject, "version"> & { version: number };
  const keys = [
    "format",
    "version",
    "scene",
    "current_scene",
    "source_image",
    "parameter_overrides",
    "unlocked_geometry",
  ];
  if (p.version === 2) keys.push("recognition_scene");
  if (
    Object.keys(p).some((k) => !keys.includes(k)) ||
    keys.some((k) => !(k in p)) ||
    p.format !== "augphys-mechanics-project" ||
    ![1, 2].includes(p.version) ||
    !Array.isArray(p.unlocked_geometry) ||
    !p.parameter_overrides ||
    typeof p.parameter_overrides !== "object" ||
    Array.isArray(p.parameter_overrides)
  )
    throw new Error("mech.invalid_project");
  if (
    typeof p.source_image !== "string" ||
    !/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/]+={0,2}$/.test(
      p.source_image,
    ) ||
    p.source_image.length > 44000000
  )
    throw new Error("mech.invalid_image");
  const scene = interactionBindings(parseScene(p.scene)),
    current = interactionBindings(parseScene(p.current_scene));
  const recognition =
    p.version === 2 ? parseScene(p.recognition_scene) : parseScene(p.scene);
  if (
    recognition.image.width !== scene.image.width ||
    recognition.image.height !== scene.image.height
  )
    throw new Error("mech.image_dimensions");
  const overrides = { ...p.parameter_overrides };
  for (const [path, number] of Object.entries(overrides)) {
    const canonical = scalarVelocityPath(scene, path);
    if (canonical === path) continue;
    if (canonical in overrides && overrides[canonical] !== number)
      throw new Error("mech.inconsistent_project");
    overrides[canonical] = number;
    delete overrides[path];
    Object.assign(valueAt(current, canonical), {
      number,
      unit: "m/s",
      status: "user",
      source: "user",
      confidence: 1,
    });
    Object.assign(
      valueAt(current, path),
      structuredClone(valueAt(scene, path)),
    );
  }
  const engine = restoreEngine({
    scene,
    overrides,
    unlocked: p.unlocked_geometry,
    recognition,
  });
  // Canonical property order comes from the source; imported JSON may reorder keys.
  const canonical = (v: unknown): string =>
    JSON.stringify(v, (_k, x) =>
      x && typeof x === "object" && !Array.isArray(x)
        ? Object.fromEntries(
            Object.entries(x).sort(([a], [b]) => a.localeCompare(b)),
          )
        : x,
    );
  if (canonical(engine.document) !== canonical(current))
    throw new Error("mech.inconsistent_project");
  return project(engine, p.source_image);
}
export async function checkImage(
  data: string,
  width?: number,
  height?: number,
) {
  const image = new Image();
  image.src = data;
  await image.decode();
  if (
    image.naturalWidth < 1 ||
    image.naturalHeight < 1 ||
    image.naturalWidth * image.naturalHeight > 16000000 ||
    image.naturalWidth > 8000 ||
    image.naturalHeight > 8000
  )
    throw new Error("mech.image_size");
  if (
    width !== undefined &&
    (width !== image.naturalWidth || height !== image.naturalHeight)
  )
    throw new Error("mech.image_dimensions");
  return image;
}
export function readFile(file: File): Promise<string> {
  if (file.size > 32000000) return Promise.reject(new Error("mech.image_size"));
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onerror = () => reject(new Error("mech.invalid_image"));
    r.onload = () => resolve(String(r.result));
    r.readAsDataURL(file);
  });
}
export function download(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob),
    a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
