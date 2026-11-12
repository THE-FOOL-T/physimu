export interface ParameterRow {
  id: string;
  label: string;
  kind: string;
  value: number | null;
  unit: string;
  min: number;
  max: number;
  step: number;
  locked: boolean;
  status: string;
  confidence: number;
}
interface RowUI {
  field: HTMLFieldSetElement;
  title: Text;
  badge: HTMLSpanElement;
  inputs: HTMLInputElement[];
  description: HTMLElement;
  button: HTMLButtonElement;
}
const panels = new WeakMap<HTMLElement, Map<string, RowUI>>();
export function parameterPanel(
  container: HTMLElement,
  rows: ParameterRow[],
  change: (id: string, value: number) => void,
  unlock: (id: string) => void,
) {
  const fields = panels.get(container) ?? new Map<string, RowUI>();
  panels.set(container, fields);
  for (const [id, ui] of fields)
    if (!rows.some((row) => row.id === id)) {
      ui.field.remove();
      fields.delete(id);
    }
  for (const row of rows) {
    let ui = fields.get(row.id);
    if (!ui) {
      const field = document.createElement("fieldset");
      field.dataset.parameter = row.id;
      const title = document.createElement("legend");
      const titleText = document.createTextNode("");
      title.append(titleText);
      const badge = document.createElement("span");
      title.append(" ", badge);
      field.append(title);
      const inputs: HTMLInputElement[] = [];
      for (const type of ["range", "number"]) {
        const input = document.createElement("input");
        input.type = type;
        input.setAttribute("aria-label", `${row.label} ${type}`);
        input.addEventListener(type === "range" ? "input" : "change", () => {
          if (input.value !== "" && Number.isFinite(input.valueAsNumber))
            change(row.id, input.valueAsNumber);
        });
        field.append(input);
        inputs.push(input);
      }
      const description = document.createElement("small");
      field.append(description);
      const button = document.createElement("button");
      button.type = "button";
      button.addEventListener("click", () => unlock(row.id));
      field.append(button);
      container.append(field);
      ui = { field, title: titleText, badge, inputs, description, button };
      fields.set(row.id, ui);
    }
    ui.title.textContent = `${row.label} (${row.unit})`;
    ui.badge.className = `sim-badge ${row.status}`;
    ui.badge.textContent = `${row.status} · ${Math.round(row.confidence * 100)}%`;
    for (const input of ui.inputs) {
      input.min = String(row.min);
      input.max = String(row.max);
      input.step = String(row.step);
      input.value = row.value === null ? "" : String(row.value);
      input.disabled = row.locked;
    }
    ui.description.textContent =
      row.kind === "geometry"
        ? "Changing this geometry redraws the diagram."
        : row.kind === "initial"
          ? "Moves the initial state; keeps the background."
          : "Physics; keeps the original background.";
    ui.button.hidden = row.kind !== "geometry";
    ui.button.disabled = !row.locked;
    ui.button.textContent = row.locked
      ? `🔒 Unlock ${row.label}`
      : "Geometry unlocked";
    ui.button.setAttribute(
      "aria-label",
      row.locked ? `Unlock ${row.label}` : "Geometry unlocked",
    );
  }
}
