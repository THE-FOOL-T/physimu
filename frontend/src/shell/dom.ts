export const $ = <T extends HTMLElement = HTMLElement>(id: string) =>
  document.getElementById(id) as T;
export const esc = (value: unknown) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ]!,
  );
export const options = (
  items: { value: string; label: string }[],
  selected?: string,
) =>
  items
    .map(
      (i) =>
        `<option value="${esc(i.value)}" ${selected === i.value ? "selected" : ""}>${esc(i.label)}</option>`,
    )
    .join("");
