import type { Component, Netlist } from "../types";
import { componentTypes } from "./editor";
import { removeComponent, rotateComponent, unitFor } from "./edit-geometry";
import { componentIcon } from "./icons";
import { t } from "../../../shell/language";

type Actions = {
  net: () => Netlist;
  mutate: (fn: (n: Netlist) => void) => void;
  screen: (xy: number[]) => number[];
  selected: () => string;
};
const node = <K extends keyof HTMLElementTagNameMap>(
  tag: K,
  parent: HTMLElement,
  key?: string,
) => {
  const n = document.createElement(tag);
  parent.append(n);
  if (key) {
    n.dataset.i18n = key;
    n.textContent = t(key);
  }
  return n;
};
export class PartPopover {
  element = document.createElement("section");
  part = "";
  constructor(private actions: Actions) {
    this.element.className = "part-popover";
    this.element.hidden = true;
    this.element.dataset.testid = "part-popover";
    this.element.setAttribute("role", "dialog");
    document.body.append(this.element);
    this.element.addEventListener("keydown", (e) => {
      if (e.key === "Escape" || e.key === "Enter") {
        e.preventDefault();
        this.close();
        document.getElementById("overlay")?.focus();
      }
    });
    window.addEventListener("resize", () => this.place());
    document.addEventListener(
      "scroll",
      () => {
        if (!this.element.hidden) this.place();
      },
      true,
    );
  }
  open(id: string, focusValue = false) {
    const c = this.actions.net().components.find((c) => c.id === id);
    if (!c) return;
    this.part = id;
    this.element.replaceChildren();
    this.element.hidden = false;
    this.element.setAttribute("aria-label", t("edit.part_title", { part: id }));
    const head = node("div", this.element);
    head.className = "row spread";
    node("strong", head).textContent = c.id;
    const chip = node("span", head);
    chip.className = "status " + c.value.status;
    chip.textContent = t(c.value.status);
    const close = node("button", head, "ocr.close");
    close.onclick = () => this.close();
    const types = node("div", this.element);
    types.className = "part-type-grid";
    for (const type of componentTypes) {
      const button = node("button", types);
      button.type = "button";
      button.dataset.partType = type;
      button.title = t("type." + type);
      button.setAttribute("aria-label", t("type." + type));
      button.setAttribute("aria-pressed", String(c.type === type));
      button.innerHTML = componentIcon(type);
      button.onclick = () => {
        this.change((part) => {
          const unit = unitFor(type);
          if (part.value.unit !== unit)
            part.value = {
              number: null,
              unit,
              status: "assumed",
              source: "prior",
              confidence: 0,
            };
          part.type = type;
          part.disabled = false;
          part.polarity = [
            "dc_source",
            "battery",
            "ac_source",
            "current_source",
          ].includes(type)
            ? part.polarity || { positive_terminal: part.terminals[0].id }
            : null;
        });
        this.open(id);
      };
    }
    const valueLabel = node("label", this.element, "value");
    const row = node("div", this.element);
    row.className = "value-row";
    const value = node("input", row);
    value.id = "part-value";
    valueLabel.htmlFor = value.id;
    value.type = "number";
    value.step = "any";
    value.value = c.value.number === null ? "" : String(c.value.number);
    const slider = node("input", this.element);
    slider.type = "range";
    slider.min = "0";
    slider.max = String(
      Math.max(c.value.unit === "V" ? 24 : 1, (c.value.number || 1) * 3),
    );
    slider.step = "any";
    slider.value = String(c.value.number ?? 0);
    slider.dataset.testid = "part-slider";
    slider.setAttribute("aria-label", c.id + " " + t("value"));
    slider.oninput = () => {
      value.value = slider.value;
      value.dispatchEvent(new Event("input"));
    };
    value.oninput = () => {
      const number = value.value === "" ? null : Number(value.value);
      if (number !== null && !Number.isFinite(number)) return;
      slider.max = String(
        Math.max(Number(slider.max), Math.abs(number || 0) * 2),
      );
      slider.value = String(number ?? 0);
      this.change((part) => {
        part.value.number = number;
        part.value.status = "user";
        part.value.source = "user";
        part.value.confidence = 1;
        part.value.unit_inferred = false;
      });
    };
    const unit = node("select", row);
    unit.setAttribute("aria-label", t("ocr.unit"));
    unit.dataset.testid = "part-unit";
    for (const [key, label] of [
      ["ohm", "Ω"],
      ["V", "V"],
      ["A", "A"],
      ["F", "F"],
      ["H", "H"],
    ]) {
      const option = node("option", unit);
      option.value = key;
      option.textContent = label;
      option.selected = c.value.unit === key;
    }
    unit.onchange = () =>
      this.change((part) => {
        part.value.unit = unit.value;
        part.value.status = "user";
        part.value.source = "user";
      });
    const presets = node("div", this.element);
    presets.className = "row";
    for (const number of c.value.unit === "ohm"
      ? [100, 1000, 10000]
      : c.value.unit === "V"
        ? [3, 6, 12]
        : c.value.unit === "F"
          ? [1e-6, 100e-6]
          : [0.1, 1, 10]) {
      const button = node("button", presets);
      button.textContent = String(number);
      button.onclick = () => {
        value.value = String(number);
        value.dispatchEvent(new Event("input"));
      };
    }
    const nameLabel = node("label", this.element, "edit.name"),
      name = node("input", this.element);
    name.id = "part-name";
    nameLabel.htmlFor = name.id;
    name.value = c.label || c.id;
    name.maxLength = 60;
    name.onchange = () =>
      this.change((part) => (part.label = name.value.trim() || null));
    const buttons = node("div", this.element);
    buttons.className = "row";
    const rotate = node("button", buttons, "edit.rotate");
    rotate.onclick = () => {
      this.actions.mutate((n) =>
        rotateComponent(n, n.components.find((c) => c.id === id)!),
      );
      this.place();
    };
    if (
      ["dc_source", "battery", "ac_source", "current_source"].includes(c.type)
    ) {
      const flip = node("button", buttons, "edit.flip");
      flip.onclick = () =>
        this.change(
          (part) =>
            (part.polarity = {
              positive_terminal:
                part.terminals[
                  part.polarity?.positive_terminal === part.terminals[0].id
                    ? 1
                    : 0
                ].id,
            }),
        );
    }
    if (c.type === "switch") {
      const toggle = node(
        "button",
        buttons,
        c.switch_closed ? "closed" : "open",
      );
      toggle.onclick = () => {
        this.change((part) => (part.switch_closed = !part.switch_closed));
        toggle.textContent = t(
          this.actions.net().components.find((c) => c.id === id)!.switch_closed
            ? "closed"
            : "open",
        );
      };
    }
    const remove = node("button", buttons, "delete");
    remove.className = "danger";
    remove.onclick = () => {
      this.actions.mutate((n) => removeComponent(n, id));
      this.close();
    };
    this.place();
    if (innerWidth < 600) {
      const sheet = this.element.getBoundingClientRect();
      const bottom = this.actions.screen([c.bbox[0], c.bbox[3]])[1];
      if (bottom > sheet.top - 24 || bottom < 48)
        window.scrollBy(0, bottom - Math.max(64, (sheet.top - 24) / 2));
    }
    if (focusValue) value.focus({ preventScroll: true });
  }
  private change(fn: (c: Component) => void) {
    this.actions.mutate((n) => {
      const c = n.components.find((c) => c.id === this.part);
      if (c) fn(c);
    });
  }
  place() {
    const c = this.actions.net()?.components.find((c) => c.id === this.part);
    if (!c || this.element.hidden) return;
    const [x, y] = this.actions.screen([
      (c.bbox[0] + c.bbox[2]) / 2,
      (c.bbox[1] + c.bbox[3]) / 2,
    ]);
    const rect = this.element.getBoundingClientRect();
    if (innerWidth < 600) {
      this.element.style.left = "8px";
      this.element.style.top =
        Math.max(8, innerHeight - rect.height - 8) + "px";
      return;
    }
    const right = this.actions.screen([c.bbox[2], c.bbox[3]])[0] + 16;
    let left =
      right + rect.width < innerWidth - 8 ? right : x - rect.width - 30;
    let top = Math.max(8, Math.min(innerHeight - rect.height - 8, y - 32));
    if (left < 8) {
      left = 8;
      top = Math.min(
        innerHeight - rect.height - 8,
        this.actions.screen([c.bbox[0], c.bbox[3]])[1] + 20,
      );
    }
    this.element.style.left = left + "px";
    this.element.style.top = Math.max(8, top) + "px";
  }
  close() {
    this.element.hidden = true;
    this.part = "";
  }
}
