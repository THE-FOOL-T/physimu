export interface Value {
  number: number | null;
  unit: string;
  status: "given" | "solved" | "assumed" | "user";
  source: string;
  confidence: number;
  unit_inferred?: boolean;
}
export interface Terminal {
  id: string;
  xy: [number, number];
  node: string;
}
export interface OCRText {
  id?: string;
  text: string;
  bbox: [number, number, number, number];
  confidence: number;
  parsed?: {
    number: number | null;
    unit: string | null;
    unit_inferred?: boolean;
    label?: string | null;
  } | null;
  assigned_to?: string;
  outcome?: "assigned" | "unassigned" | "ignored";
  reason?: string;
  engine?: string;
  raw_text?: string;
  normalized_text?: string;
  rotation?: number;
  ocr_backend?: "hybrid";
  ocr_conflict?: boolean;
  provenance?: string[];
  wire_overlap?: boolean;
  candidates?: {
    component_id: string;
    role: string;
    distance: number;
    reason: string;
    score?: number;
  }[];
  symbol_proposals?: {
    text: string;
    evidence: string[];
    unit_inferred?: boolean;
  }[];
  user_confirmed?: boolean;
  alternatives?: {
    text: string;
    confidence: number;
    engine?: string;
    bbox?: [number, number, number, number];
    rotation?: number;
    parsed?: OCRText["parsed"];
  }[];
}
export interface Component {
  id: string;
  type: string;
  label: string | null;
  bbox: [number, number, number, number];
  orientation_deg: number;
  terminals: [Terminal, Terminal];
  value: Value;
  polarity: { positive_terminal: string } | null;
  switch_closed: boolean;
  internal_resistance: number | null;
  initial_voltage: number;
  initial_current: number;
  virtual: boolean;
  confidence: number;
  disabled: boolean;
}
export interface WirePoint {
  id: string;
  xy: [number, number];
  kind: string;
  node: string;
}
export interface Segment {
  id: string;
  from: string;
  to: string;
  polyline: [number, number][];
  node: string;
  confidence: number;
}
export interface Warning {
  code: string;
  ref: string | null;
  message_key: string;
}
export interface Netlist {
  version: 1;
  image: { path: string; width: number; height: number };
  components: Component[];
  nodes: { id: string; is_ground: boolean; label: string | null }[];
  wire_graph: { points: WirePoint[]; segments: Segment[] };
  constraints: {
    type: string;
    // Component id, total, node-label pair A-B, or ratio R1/R2 (version 1).
    target: string;
    value: number;
    unit: string;
    source: string;
  }[];
  warnings: Warning[];
  meta: {
    problem_text: string | null;
    language: "en" | "bn";
    degraded: boolean;
    style: string;
    region: [number, number, number, number] | null;
    provenance: "extracted" | "partial" | "demo_fallback" | "edited";
  };
}
export interface Reading {
  v_drop: number;
  current: number;
  power: number;
  internal_power: number;
  internal_resistance: number;
  deflection: number;
}
export interface Solution {
  node_voltages: Record<string, number>;
  components: Record<string, Reading>;
  segment_currents: Record<string, number>;
  total_power_supplied: number;
  total_power_consumed: number;
  internal_power: number;
  equivalent_resistance: number | null;
  short_circuit: {
    detected: boolean;
    sources: string[];
    bypassed: string[];
    short_paths: {
      source: string;
      current: number;
      segments: string[];
      components: string[];
    }[];
    ideal_current_infinite: boolean;
  };
  state: Record<string, number>;
  warnings: Warning[];
  invariants: {
    kcl: Record<string, number>;
    max_kcl_error: number | null;
    relative_power_error: number | null;
    regularization_power: number;
  };
}
