import type { Scene, State } from "./types";
import { t } from "../../shell";
import { componentName } from "./upload-panel";

const nodes = new WeakMap<HTMLElement, Map<string, HTMLElement>>();
/** Playback updates existing text nodes; it does not rebuild the inspector each frame. */
export function updateReadouts(
  root: HTMLElement,
  scene: Scene,
  state: State,
  number: (n: number, places?: number) => string,
) {
  let fields = nodes.get(root);
  if (!fields) {
    fields = new Map();
    nodes.set(root, fields);
    root.replaceChildren();
  }
  const rows: [string, string][] = [
    ["kinetic", `${t("mech.kinetic")}: ${number(state.kinetic)} J`],
    ["potential", `${t("mech.potential")}: ${number(state.potential)} J`],
    [
      "momentum_x",
      `${t("mech.momentum_x")}: ${number(state.momentum.x)} kg m/s`,
    ],
    [
      "momentum_y",
      `${t("mech.momentum_y")}: ${number(state.momentum.y)} kg m/s`,
    ],
    ...Object.entries(state.velocities).map(([id, v]): [string, string] => [
      id,
      `${componentName(scene, id)} · ${t("mech.velocity")}: (${number(v.x)}, ${number(v.y)}) m/s`,
    ]),
  ];
  const keys = new Set(rows.map(([key]) => key));
  for (const [key, node] of fields)
    if (!keys.has(key) || node.parentElement !== root) {
      node.remove();
      fields.delete(key);
    }
  for (const [key, text] of rows) {
    let node = fields.get(key);
    if (!node) {
      node = document.createElement("p");
      fields.set(key, node);
      root.append(node);
    }
    if (node.textContent !== text) node.textContent = text;
  }
}
