import { t } from "../../shell";

export function el<K extends keyof HTMLElementTagNameMap>(
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
export function button(parent: HTMLElement, key: string, action: () => void) {
  const b = el("button", parent, key);
  b.type = "button";
  b.dataset.action = key;
  b.addEventListener("click", action);
  return b;
}
export function select(
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
export function input(
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
