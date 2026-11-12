import { groupWarnings } from "./warnings";
import type { AppState } from "./state";
import { $, esc } from "./dom";
import { t, format } from "../i18n";
import type { Renderer } from "../overlay/renderer";
import { updateSourceControl } from "./workspace";
import { supported } from "../solver/mna";
import { precheck } from "./precheck";
export function renderMeasurements(
  appState: AppState,
  renderer: Renderer,
  updateEditor: () => void,
  renderExplanations: () => void,
) {
  updateSourceControl(appState.net);
  renderExplanations();
  $("supplied").textContent = format(
    appState.solution.total_power_supplied,
    "W",
  );
  $("consumed").textContent = format(
    appState.solution.total_power_consumed,
    "W",
  );
  $("equivalent").textContent =
    appState.solution.equivalent_resistance === null
      ? "—"
      : format(appState.solution.equivalent_resistance, "Ω");
  $("solve-time").textContent = `${appState.lastSolve.toFixed(2)} ms`;
  $("readout").innerHTML = appState.net.components
    .filter((c) => appState.solution.components[c.id])
    .map((c) => {
      const r = appState.solution.components[c.id];
      if (!supported.has(c.type))
        return `<tr data-select="${esc(c.id)}" tabindex="0"><td>${esc(c.id)}</td><td colspan="3">${esc(t("ui.unknown_short"))}</td></tr>`;
      return `<tr data-select="${esc(c.id)}" class="${appState.selected === c.id ? "selected" : ""}" tabindex="0"><td>${esc(c.id)}</td><td>${esc(format(r.v_drop, "V"))}</td><td>${esc(format(r.current, "A"))}</td><td>${esc(format(r.power, "W"))}</td></tr>`;
    })
    .join("");
  $("nodes").innerHTML = Object.entries(appState.solution.node_voltages)
    .map(
      ([id, v]) =>
        `<span class="node-tag">${esc(id)} <b>${esc(format(v, "V"))}</b></span>`,
    )
    .join("");
  const c = appState.net.components.find((c) => c.id === appState.selected),
    r = c && appState.solution.components[c.id];
  renderer.selected = appState.selected;
  $("inspector").innerHTML =
    c && r
      ? /* HTML */ `<span class="eyebrow"
            >${esc(t("type." + c.type))}
            ${c.virtual ? " / " + esc(t("virtual")) : ""}</span
          >
          <p class="section-gap">
            ${esc(
              t("explain.component", {
                id: c.id,
                current: format(r.current, "A"),
                voltage: format(r.v_drop, "V"),
              }),
            )}
          </p>
          <div class="reading">
            <div>
              <span class="muted small">${esc(t("power"))}</span
              ><strong class="mono">${esc(format(r.power, "W"))}</strong>
            </div>
            <div>
              <span class="muted small">${esc(t(c.value.status))}</span>${c
                .value.unit_inferred
                ? `<small class="unit-guessed">${esc(t("ocr.unit_guessed"))}</small>`
                : ""}${c.value.status === "assumed" &&
              c.value.source === "prior"
                ? `<small class="missing-value">${esc(t("ocr.not_found"))}</small>`
                : ""}<strong class="mono"
                >${esc(
                  format(
                    c.value.number || 0,
                    c.value.unit === "ohm" ? "Ω" : c.value.unit,
                  ),
                )}</strong
              >
            </div>
          </div>
          ${r.internal_power
            ? `<p class="section-gap small">${esc(t("internal_power"))}: ${esc(format(r.internal_power, "W"))}</p>`
            : ""}<button class="small section-gap" id="short-add">
            ${esc(
              t(
                appState.net.components.some((c) => c.id === "SHORT")
                  ? "remove_short"
                  : "short_mode",
              ),
            )}
          </button>`
      : esc(t("inspect"));
  if (c && !supported.has(c.type))
    $("inspector").textContent = t("ui.unknown_block", {
      type: t("type." + c.type),
    });
  if (c && r && ["ammeter", "galvanometer"].includes(c.type)) {
    const deflection = document.createElement("p");
    deflection.className = "small section-gap";
    deflection.textContent = t("explain.deflection", {
      direction: r.deflection > 0 ? "→" : r.deflection < 0 ? "←" : "0",
    });
    $("inspector").append(deflection);
  }
  const warnings = appState.solution.warnings;
  renderer.issues = precheck(appState.net, renderer.ghosts).issues;
  const grouped = groupWarnings(warnings);
  $("warning-count").textContent = String(grouped.length);
  $("notices").replaceChildren(
    ...grouped.map(({ warning, refs }) => {
      const row = document.createElement("div");
      row.className = "notice";
      row.textContent =
        t(warning.message_key) +
        (refs.size > 1
          ? " · " + t("warning.group", { count: String(refs.size) })
          : warning.ref
            ? " ? " + warning.ref
            : "");
      const issue = renderer.issues.find(
        (i) => i.code === warning.code && refs.has(i.ref),
      );
      if (issue) {
        const button = document.createElement("button");
        button.dataset.issue = issue.id;
        button.textContent = t("trace.fix");
        row.append(button);
      }
      return row;
    }),
  );
  if (!grouped.length) $("notices").textContent = t("empty");
  $("banner").textContent =
    appState.net.meta.style === "handwritten"
      ? t("handwritten")
      : appState.net.meta.degraded
        ? t("warn.uncertain_topology")
        : "";
  $("short-banner").textContent = appState.solution.short_circuit.detected
    ? `${t("short")} · ${t("ideal")}${appState.withoutShort !== null ? " " + t("without_short", { current: format(appState.withoutShort, "A") }) : ""}`
    : "";
  $("voltage-high").textContent = format(
    Math.max(...Object.values(appState.solution.node_voltages), 0),
    "V",
  );
  $("physical-time").textContent = format(appState.time, "s");
  renderer.selected = appState.selected;
  updateEditor();
}
