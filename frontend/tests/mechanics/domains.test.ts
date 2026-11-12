import test from "node:test";
import assert from "node:assert/strict";
import { createRegistry, type DomainModule } from "../../src/domains";
import { createCircuitDomain } from "../../src/domains/circuit";
import type { ShellContext } from "../../src/shell";

const ctx: ShellContext = { t: (key) => key };
const container = {} as HTMLElement;

test("domain registries preserve insertion order and reject unknown names", () => {
  const registry = createRegistry();
  const module: DomainModule = {
    id: "mechanics",
    mount: () => ({ unmount() {}, getDocument: () => null }),
  };
  registry.register(module);
  assert.deepEqual(registry.names(), ["mechanics"]);
  assert.equal(registry.get("mechanics"), module);
  assert.throws(() => registry.get("auto"), /Unknown domain/);
  assert.throws(() => registry.register(module), /Duplicate domain/);
  assert.deepEqual(createRegistry().names(), []);
});

test("circuit unmount preserves the document and restores hidden controls on remount", () => {
  const elements = [
    { hidden: false, inert: false },
    { hidden: true, inert: false },
  ] as HTMLElement[];
  const document = { components: [{ id: "R1", value: 42 }], history: [1, 2] };
  const activity: boolean[] = [];
  const circuit = createCircuitDomain({
    elements,
    setActive: (active) => activity.push(active),
    getDocument: () => document,
  });
  const first = circuit.mount(container, undefined, ctx);
  first.unmount();
  first.unmount();
  assert.deepEqual(activity, [true, false]);
  assert.ok(elements.every((el) => el.hidden && el.inert));
  assert.equal(first.getDocument(), document);
  const second = circuit.mount(container, undefined, ctx);
  assert.deepEqual(
    elements.map((el) => [el.hidden, el.inert]),
    [
      [false, false],
      [true, false],
    ],
  );
  assert.equal(second.getDocument(), document);
  assert.deepEqual(activity, [true, false, true]);
});
