import type { Scene, Params } from "./types";
import { valueAt } from "./validate";

/** Explicit label correction only. Unitless dimensional numbers are never guessed. */
export function correctedQuantity(
  raw: string,
): { number: number; unit: string } | null {
  const text = raw
    .normalize("NFC")
    .replace(/[০-৯]/g, (c) => String("০১২৩৪৫৬৭৮৯".indexOf(c)))
    .replace(/[₀-₉]/g, (c) => String("₀₁₂₃₄₅₆₇₈₉".indexOf(c)))
    .replace("−", "-")
    .replace("²", "^2");
  const match = text.match(
    /^\s*(?:([A-Za-zμµθΘω][\wμ]*)\s*[:=]\s*)?([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(kg\/s|1\/s|rad\/s|m\/s\^?2|m\/s|N\/m|kg|cm|mm|deg|°|g|m|N)?\s*$/,
  );
  if (!match) return null;
  const number = Number(match[2]),
    unit = match[3];
  if (!Number.isFinite(number)) return null;
  if (!unit)
    return /^(?:μ[sk]?|µ[sk]?|mu_?[sk]?|e)$/.test(match[1] ?? "")
      ? { number, unit: "1" }
      : null;
  const conversion: Record<string, [number, string]> = {
    g: [0.001, "kg"],
    cm: [0.01, "m"],
    mm: [0.001, "m"],
    "°": [1, "deg"],
    "m/s2": [1, "m/s^2"],
  };
  const [factor, canonical] = conversion[unit] ?? [1, unit];
  return { number: number * factor, unit: canonical };
}

export function labelCorrection(scene: Scene, path: string, text: string) {
  const value = correctedQuantity(text),
    target = valueAt(scene, path);
  if (!value) return null;
  if (value.unit === target.unit) return value;
  if (
    scene.archetype === "pendulum" &&
    path === "params.angular_speed" &&
    value.unit === "m/s"
  ) {
    const length = scene.links[0]?.length_m?.number;
    if (length && length > 0)
      return { number: value.number / length, unit: "rad/s" };
  }
  return null;
}

/** Bound annotations keep the unit of the original observation when it is a
 * derived representation of the authoritative angular-speed Value. */
export function labelQuantity(
  scene: Scene,
  path: string,
  text: string,
  params: Params,
) {
  const value = valueAt(scene, path),
    number = params[path] ?? value.number;
  if (
    scene.archetype === "pendulum" &&
    path === "params.angular_speed" &&
    correctedQuantity(text)?.unit === "m/s" &&
    number !== null
  ) {
    const link = scene.links[0],
      length = params[`links.${link.id}.length_m`] ?? link.length_m?.number;
    if (length && length > 0) return { number: number * length, unit: "m/s" };
  }
  return { number, unit: value.unit };
}
