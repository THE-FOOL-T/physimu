import type { AppState } from "./state";
import { $, esc } from "../../../shell/dom";
import { t } from "../../../shell/language";
import { componentIcon } from "./icons";
import { voltageTypes } from "../solver/mna";
import type { Component } from "../types";

function parameterCard(c: Component, appState: AppState) {
  const value = c.value.number || 0,
    unit = c.value.unit === "ohm" ? "Ω" : c.value.unit;
  return /* HTML */ `<div
    class="control ${Math.min(c.confidence, c.value.confidence) < 0.65
      ? "low-confidence"
      : ""}"
    data-component="${esc(c.id)}"
  >
    <div class="control-top">
      <button
        class="quiet control-name"
        data-action="select"
        data-id="${esc(c.id)}"
      >
        ${componentIcon(c.type)}${esc(c.id)}${c.virtual ? " ◇" : ""}</button
      ><span class="status ${esc(c.value.status)}"
        >${esc(t(c.value.status))}</span
      >${c.value.unit_inferred
        ? `<small class="unit-guessed">${esc(t("ocr.unit_guessed"))}</small>`
        : ""}${c.value.status === "assumed" && c.value.source === "prior"
        ? `<small class="missing-value">${esc(t("ocr.not_found"))}</small>`
        : ""}<small class="confidence"
        >${esc(
          t("ui.confidence", {
            value: String(
              Math.round(Math.min(c.confidence, c.value.confidence) * 100),
            ),
          }),
        )}</small
      >
    </div>
    ${c.type === "switch"
      ? `<button class="small" data-action="switch" data-id="${esc(c.id)}">${esc(t(c.switch_closed ? "closed" : "open"))}</button>`
      : `<div class="control-inputs"><input aria-label="${esc(c.id)} ${esc(t("value"))}" type="range" min="${value > 0 ? value / 10 : 0}" max="${value > 0 ? value * 3 : 100}" step="any" value="${value}" data-param="${esc(c.id)}"><input aria-label="${esc(c.id)} ${esc(t("value"))} ${esc(t("ui.number"))}" type="number" step="any" value="${value}" data-param="${esc(c.id)}"><span class="unit" title="${esc(t("unit." + c.value.unit))}">${esc(unit)}</span></div>`}${voltageTypes.has(
      c.type,
    )
      ? `<div class="row section-gap"><button class="small quiet" data-action="flip" data-id="${esc(c.id)}">⇄ ${esc(t("polarity"))}</button><label class="small">${esc(t("internal_r"))}<input class="tiny-input" type="number" min="0" step=".01" value="${c.internal_resistance ?? appState.solution.components[c.id]?.internal_resistance ?? 0}" data-internal="${esc(c.id)}"></label></div>`
      : ""}${c.type === "capacitor"
      ? `<label class="small row section-gap">${esc(t("initial_v"))}<input class="tiny-input" type="number" step="any" value="${c.initial_voltage}" data-initial="${esc(c.id)}"></label>`
      : ""}
  </div>`;
}
export function renderParameters(appState: AppState) {
  $("controls").innerHTML = appState.net.components
    .filter((c) => !c.disabled)
    .map((c) => parameterCard(c, appState))
    .join("");
}

export function addInductorControls(appState: AppState) {
  for (const c of appState.net.components.filter(
    (c) => c.type === "inductor" && !c.disabled,
  )) {
    const block = [
      ...document.querySelectorAll<HTMLElement>("[data-component]"),
    ].find((el) => el.dataset.component === c.id);
    if (!block) continue;
    const label = document.createElement("label");
    label.className = "small row section-gap";
    label.append(document.createTextNode(t("initial_i")));
    const input = document.createElement("input");
    input.type = "number";
    input.step = "any";
    input.className = "tiny-input";
    input.value = String(c.initial_current);
    input.dataset.initialCurrent = c.id;
    label.append(input);
    block.append(label);
  }
}
