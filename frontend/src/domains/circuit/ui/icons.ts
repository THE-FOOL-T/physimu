import type { Component } from "../types";

/** Decorative, code-native schematic symbols for parameter rows. */
export function componentIcon(type: Component["type"]): string {
  const path: Record<string, string> = {
    resistor: "M1 12h3l2-5 4 10 4-10 4 10 2-5h3",
    rheostat: "M1 12h3l2-5 4 10 4-10 4 10 2-5h3 M6 21 18 3m-5 0h5v5",
    capacitor: "M1 12h8m0-7v14m6-14v14m0-7h8",
    switch: "M1 12h5l11-7m1 7h5",
    inductor: "M1 12h3c0-8 5-8 5 0 0-8 5-8 5 0 0-8 5-8 5 0h4",
    dc_source: "M1 12h5m12 0h5 M9 12h6m-3-3v6",
    battery: "M1 12h5m0-7v14m4-11v8m4-11v14m4-11v8m0-4h5",
    ammeter: "M1 12h4m14 0h4 M8 16l4-8 4 8m-6-3h4",
    voltmeter: "M1 12h4m14 0h4 M8 8l4 8 4-8",
    galvanometer: "M1 12h4m14 0h4 M15 9c-8-5-10 10 0 6v-3h-3",
    lamp: "M1 12h4m14 0h4 M8 8l8 8m0-8-8 8",
    ground: "M12 2v10m-8 0h16m-13 4h10m-7 4h4",
    diode: "M1 12h5m0-6 10 6-10 6V6m10 0v12m0-6h7",
    current_source: "M1 12h4m14 0h4 M8 12h8m-4-4 4 4-4 4",
    ac_source: "M1 12h4m14 0h4 M7 12c2-7 3-7 5 0s3 7 5 0",
    potentiometer: "M1 12h3l2-5 4 10 4-10 4 10 2-5h3 M12 2v5m-3-3 3 3 3-3",
  };
  const circle = [
    "dc_source",
    "current_source",
    "ac_source",
    "ammeter",
    "voltmeter",
    "galvanometer",
    "lamp",
  ].includes(type)
    ? '<circle cx="12" cy="12" r="7"/>'
    : "";
  return `<svg class="part-icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${circle}<path d="${path[type] || "M1 12h4m14 0h4 M5 6h14v12H5z"}"/></svg>`;
}
