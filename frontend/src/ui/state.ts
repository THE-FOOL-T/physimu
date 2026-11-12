import type { Netlist, Solution } from "../types";
/** A workspace owns its state; loading a circuit resets its simulation and editor. */
export function createAppState() {
  return {
    net: null! as Netlist,
    automatic: null! as Netlist,
    solution: null! as Solution,
    selected: "",
    editing: false,
    online: false,
    modelStatus: "warming",
    playing: true,
    mode: "steady",
    time: 0,
    state: {} as Record<string, number>,
    duration: 5,
    dt: 0.01,
    title: "",
    lastSolve: 0,
    regions: [] as Netlist[],
    imageBlob: null as Blob | null,
    objectUrl: "",
    interaction: "none" as "none" | "add" | "place" | "bend",
    withoutShort: null as number | null,
    uploadBusy: false,
    graphHistory: [] as { time: number; v: number; i: number }[],
  };
}

export type AppState = ReturnType<typeof createAppState>;
