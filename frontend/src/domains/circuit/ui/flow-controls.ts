import { t } from "../../../shell/language";
import type { Renderer } from "../overlay/renderer";
import { saveFlow, type FlowStyle, type FlowColor } from "../overlay/flow";

export function flowControls(renderer: Renderer) {
  const menu = document.createElement("details");
  menu.className = "flow-controls";
  const summary = document.createElement("summary");
  summary.dataset.i18n = "flow.controls";
  menu.append(summary);
  const panel = document.createElement("div");
  panel.className = "flow-options";
  menu.append(panel);
  for (const [field, values] of [
    ["style", ["dots", "dashes", "arrows", "glow"]],
    ["color", ["amber", "cyan", "lime", "magenta"]],
  ] as const) {
    const label = document.createElement("label"),
      text = document.createElement("span");
    text.dataset.i18n = "flow." + field;
    label.append(text);
    const select = document.createElement("select");
    select.dataset.testid = "flow-" + field;
    select.dataset.i18nAria = "flow." + field;
    select.setAttribute("aria-label", t("flow." + field));
    for (const value of values) {
      const option = document.createElement("option");
      option.value = value;
      option.dataset.i18n = "flow." + value;
      select.append(option);
    }
    select.value = renderer.flow[field];
    select.onchange = () => {
      if (field === "style") renderer.flow.style = select.value as FlowStyle;
      else renderer.flow.color = select.value as FlowColor;
      saveFlow(renderer.flow);
    };
    label.append(select);
    panel.append(label);
  }
  const label = document.createElement("label"),
    text = document.createElement("span");
  text.dataset.i18n = "flow.size";
  label.append(text);
  const input = document.createElement("input");
  input.type = "range";
  input.min = "0";
  input.max = "2";
  input.step = "1";
  input.value = String([0.8, 1, 1.25].indexOf(renderer.flow.size));
  input.dataset.testid = "flow-size";
  input.dataset.i18nAria = "flow.size";
  input.setAttribute("aria-label", t("flow.size"));
  input.oninput = () => {
    renderer.flow.size = [0.8, 1, 1.25][Number(input.value)];
    saveFlow(renderer.flow);
  };
  label.append(input);
  panel.append(label);
  document.querySelector(".canvas-toolbar")!.append(menu);
  const close = document.createElement("button");
  close.dataset.i18n = "ocr.close";
  close.onclick = () => {
    menu.open = false;
  };
  panel.append(close);
  const state = document.createElement("span");
  state.className = "flow-state";
  state.dataset.testid = "flow-state";
  document.querySelector(".stage-bottom")!.append(state);
}
