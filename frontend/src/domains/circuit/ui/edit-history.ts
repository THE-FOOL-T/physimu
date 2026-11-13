import type { Netlist } from "../types";

type Path = (string | number)[];
type Change = { path: Path; before: unknown; after: unknown };
type Snapshot = Omit<Netlist, "image"> & {
  image: Omit<Netlist["image"], "path">;
};
type Entry = { changes: Change[]; pending?: Snapshot };
function capture(net: Netlist): Snapshot {
  const { image, ...editable } = net;
  return structuredClone({
    ...editable,
    image: { width: image.width, height: image.height },
  });
}
export function cloneForEdit(net: Netlist): Netlist {
  return { ...capture(net), image: { ...net.image } };
}
function differences(
  before: unknown,
  after: unknown,
  path: Path = [],
): Change[] {
  if (Object.is(before, after)) return [];
  if (Array.isArray(before) && Array.isArray(after)) {
    const changes: Change[] = [];
    for (let i = 0; i < Math.min(before.length, after.length); i++)
      changes.push(...differences(before[i], after[i], [...path, i]));
    for (let i = before.length - 1; i >= after.length; i--)
      changes.push({ path: [...path, i], before: before[i], after: undefined });
    for (let i = before.length; i < after.length; i++)
      changes.push({ path: [...path, i], before: undefined, after: after[i] });
    return changes;
  }
  if (
    before &&
    after &&
    typeof before === "object" &&
    typeof after === "object"
  ) {
    const a = before as Record<string, unknown>,
      b = after as Record<string, unknown>;
    return [...new Set([...Object.keys(a), ...Object.keys(b)])].flatMap((k) =>
      differences(a[k], b[k], [...path, k]),
    );
  }
  return [{ path, before, after }];
}
function apply(net: Netlist, changes: Change[], reverse: boolean): Netlist {
  const result = { ...net, ...capture(net), image: { ...net.image } };
  for (const change of reverse ? [...changes].reverse() : changes) {
    let target: unknown = result;
    for (const key of change.path.slice(0, -1))
      target = (target as Record<string | number, unknown>)[key];
    const key = change.path.at(-1)!;
    const value = reverse ? change.before : change.after;
    if (value === undefined) {
      if (Array.isArray(target)) target.splice(Number(key), 1);
      else delete (target as Record<string | number, unknown>)[key];
    } else
      (target as Record<string | number, unknown>)[key] =
        structuredClone(value);
  }
  return result;
}
export class History {
  undoStack: Entry[] = [];
  redoStack: Entry[] = [];
  push(before: Netlist, after?: Netlist) {
    const entry: Entry = after
      ? { changes: differences(capture(before), capture(after)) }
      : { changes: [], pending: capture(before) };
    if (after && !entry.changes.length) return;
    this.undoStack.push(entry);
    if (this.undoStack.length > 80) this.undoStack.shift();
    this.redoStack = [];
  }
  undo(net: Netlist) {
    const entry = this.undoStack.pop();
    if (!entry) return;
    if (entry.pending) {
      entry.changes = differences(entry.pending, capture(net));
      delete entry.pending;
    }
    this.redoStack.push(entry);
    return apply(net, entry.changes, true);
  }
  redo(net: Netlist) {
    const entry = this.redoStack.pop();
    if (!entry) return;
    this.undoStack.push(entry);
    return apply(net, entry.changes, false);
  }
}
