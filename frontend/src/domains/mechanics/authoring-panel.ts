import { t } from "../../shell";
import type { Scene, Point, BBox } from "./types";
import { el, button, input, select } from "./workspace-dom";
import {
  objects,
  nameOf,
  removeObject,
  rename,
  setBox,
  handles,
  moveHandle,
  attach,
  valuePaths,
  userValue,
  calibrate,
  assignValue,
} from "./authoring";
import { valueAt } from "./validate";
import { labelCorrection } from "./labels";

interface AuthoringPanelHost {
  scene: Scene | undefined;
  root: HTMLElement;
  objectSelect: HTMLSelectElement;
  selected: string;
  edit(action: (scene: Scene) => void): void;
  coordinates(text: string, n: number): number[];
  polygon(text: string): Point[];
  valueLabel(path: string): string;
  numberText(n: number, places?: number): string;
}

/** Recognition repair and source-geometry authoring; physical interaction lives separately. */
export function renderAuthoringPanel(host: AuthoringPanelHost) {
  const s = host.scene,
    fields = host.root.querySelector<HTMLElement>(
      '[data-testid="mechanics-object-fields"]',
    )!,
    chips = host.root.querySelector<HTMLElement>(
      '[data-testid="mechanics-chips"]',
    )!;
  fields.replaceChildren();
  chips.replaceChildren();
  host.objectSelect.replaceChildren();
  if (!s) return host.selected;
  for (const o of objects(s)) {
    const option = el("option", host.objectSelect);
    option.value = o.id;
    option.textContent = `${nameOf(s, o.id)} (${o.id})`;
  }
  if (!objects(s).some((o) => o.id === host.selected))
    host.selected = objects(s)[0]?.id ?? "";
  host.objectSelect.value = host.selected;
  const object = objects(s).find((o) => o.id === host.selected),
    body = s.bodies.find((b) => b.id === host.selected),
    link = s.links.find((l) => l.id === host.selected);
  if (object) {
    button(fields, "delete_object", () =>
      host.edit((s) => removeObject(s, object.id)),
    );
    input(fields, "name", nameOf(s, object.id), (v) =>
      host.edit((s) => rename(s, object.id, v)),
    );
    if ("type" in object)
      input(fields, "object_type", object.type, (v) =>
        host.edit((s) => {
          const o = objects(s).find((o) => o.id === object.id)!;
          if ("type" in o) o.type = v;
          s.warnings = s.warnings.filter((w) => w.code !== "unknown_type");
        }),
      );
    if (body) {
      const contact = select(
        fields,
        "on_surface",
        [
          "none",
          ...s.surfaces
            .filter((sf) => ["floor", "incline"].includes(sf.type))
            .map((sf) => sf.id),
        ],
        (v) =>
          host.edit((scene) => {
            scene.bodies.find((b) => b.id === body.id)!.on_surface =
              v === "none" ? null : v;
          }),
      );
      contact.value = body.on_surface ?? "none";
      input(fields, "box", body.bbox.join(", "), (v) =>
        host.edit((s) => setBox(s, body.id, host.coordinates(v, 4) as BBox)),
      );
      input(fields, "sprite_mask", JSON.stringify(body.mask), (v) =>
        host.edit((s) => {
          s.bodies.find((b) => b.id === body.id)!.mask = host.polygon(v);
        }),
      );
    }
    const annotation = s.annotations.find((a) => a.id === object.id);
    if (annotation?.type === "label") {
      input(fields, "ocr_text", annotation.geometry.text ?? "", (text) =>
        host.edit((scene) => {
          const label = scene.annotations.find((a) => a.id === annotation.id)!;
          label.geometry.text = text;
          if (label.bound_to) {
            const value = labelCorrection(scene, label.bound_to, text),
              target = valueAt(scene, label.bound_to);
            if (!value || value.unit !== target.unit)
              throw new Error("mech.label_unit_required");
            Object.assign(target, userValue(value.number, target.unit));
          }
        }),
      );
      const target = select(
        fields,
        "label_parameter",
        ["none", ...valuePaths(s)],
        (path) =>
          host.edit((scene) => {
            const label = scene.annotations.find(
              (a) => a.id === annotation.id,
            )!;
            label.bound_to = path === "none" ? null : path;
            if (label.bound_to) {
              const value = labelCorrection(
                  scene,
                  label.bound_to,
                  label.geometry.text ?? "",
                ),
                target = valueAt(scene, label.bound_to);
              if (!value || value.unit !== target.unit)
                throw new Error("mech.label_unit_required");
              Object.assign(target, userValue(value.number, target.unit));
            }
            for (const b of scene.bindings) {
              b.labels = b.labels.filter((id) => id !== label.id);
              if (b.path === label.bound_to) b.labels.push(label.id);
            }
          }),
      );
      target.value = annotation.bound_to ?? "none";
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
          host.edit((s) => moveHandle(s, h, host.coordinates(v, 2) as Point)),
      );
    if (link)
      for (const end of ["a", "b"] as const) {
        const candidates = [
            ...s.bodies,
            ...s.pulleys,
            ...s.annotations.filter((a) => a.type === "axis"),
          ].map((v) => v.id),
          sel = select(fields, `attach_${end}`, candidates, (v) =>
            host.edit((s) => attach(s, link.id, end, v)),
          );
        sel.value = link[end].ref;
      }
    if (s.surfaces.some((v) => v.id === object.id) || link) {
      const repair = s.repairs.find((r) => r.surface_or_line_id === object.id);
      input(
        fields,
        "repair_segments",
        JSON.stringify(repair?.segments ?? []),
        (v) =>
          host.edit((s) => {
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
    host.edit((s) => (s.frame.paper_color = v)),
  );
  input(fields, "ink_color", s.frame.ink_color, (v) =>
    host.edit((s) => (s.frame.ink_color = v)),
  );
  input(
    fields,
    "stroke_px",
    String(s.frame.stroke_px),
    (v) => host.edit((s) => (s.frame.stroke_px = Number(v))),
    "number",
  );
  for (const path of valuePaths(s).filter(
    (p) =>
      (!p.includes(".initial.") || s.bindings.some((b) => b.path === p)) &&
      !p.startsWith("params.unplaced_") &&
      (p.startsWith(`bodies.${host.selected}.`) ||
        p.startsWith(`links.${host.selected}.`) ||
        p.startsWith(`surfaces.${host.selected}.`) ||
        p.startsWith(`pulleys.${host.selected}.`) ||
        p.startsWith("params.") ||
        p === "frame.px_per_m" ||
        p === "constants.g"),
  )) {
    const value = valueAt(s, path),
      label = el("label", fields),
      caption = el("span", label);
    caption.textContent = `${host.valueLabel(path)} (${value.unit}) · ${t(`mech.${value.status}`)} · ${host.numberText(value.confidence * 100, 0)}%`;
    const n = el("input", label);
    n.type = "number";
    n.step = "any";
    n.value = value.number === null ? "" : String(value.number);
    n.dataset.valuePath = path;
    n.addEventListener("change", () =>
      host.edit((s) => {
        Object.assign(
          valueAt(s, path),
          userValue(n.value === "" ? null : n.valueAsNumber, value.unit),
        );
        if (path === "frame.px_per_m") calibrate(s);
      }),
    );
    if (value.status === "assumed" && value.number !== null) {
      const confirm = button(fields, "confirm_assumption", () =>
        host.edit((scene) => {
          Object.assign(
            valueAt(scene, path),
            userValue(value.number, value.unit),
          );
        }),
      );
      confirm.setAttribute(
        "aria-label",
        `${t("mech.confirm_assumption")} ${host.valueLabel(path)}`,
      );
    }
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
        host.edit((s) =>
          Object.assign(
            s.params[key],
            userValue(v === "" ? null : Number(v), value.unit),
          ),
        ),
      "number",
    );
    input(group, "unit", value.unit, (v) =>
      host.edit((s) => (s.params[key].unit = v)),
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
      host.edit((s) => assignValue(s, key, target.value)),
    );
  }

  return host.selected;
}
