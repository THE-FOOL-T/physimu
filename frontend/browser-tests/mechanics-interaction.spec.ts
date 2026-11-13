import { test, expect, type Page } from "@playwright/test";
import { mkdirSync } from "node:fs";
import path from "node:path";
test.use({ deviceScaleFactor: 2 });

const state = (page: Page) =>
  page.evaluate(() => (window as any).mechanicsWorkspace);
const action = (page: Page, name: string) =>
  page.locator(`.mechanics-workspace [data-action="${name}"]`);
async function open(page: Page, name: string) {
  await page.goto("/");
  await page.getByTestId("domain-switch").selectOption("mechanics");
  await page.getByTestId("mechanics-fixture").selectOption(name);
  await expect(action(page, "play")).toBeEnabled();
}
async function css(page: Page, point: number[], reveal = false) {
  const s = await state(page),
    canvas = page.getByTestId("mechanics-canvas");
  if (reveal) {
    await canvas.scrollIntoViewIfNeeded();
    await canvas.evaluate(
      (c: HTMLCanvasElement, args) => {
        const v = c.parentElement!,
          ratio = c.getBoundingClientRect().width / (c.width / args.dpr);
        v.scrollLeft =
          (args.point[0] + args.padding.left) * ratio - v.clientWidth / 2;
        v.scrollTop =
          (args.point[1] + args.padding.top) * ratio - v.clientHeight / 2;
      },
      { point, padding: s.padding, dpr: s.dpr },
    );
  }
  const box = (await canvas.boundingBox())!;
  const size = await canvas.evaluate((c: HTMLCanvasElement) => ({
    w: c.width,
    h: c.height,
  }));
  return {
    x: box.x + ((point[0] + s.padding.left) * s.dpr * box.width) / size.w,
    y: box.y + ((point[1] + s.padding.top) * s.dpr * box.height) / size.h,
  };
}
async function drag(page: Page, id: string, delta: number[]) {
  const s = await state(page),
    handle = s.physicsHandles.find((h: any) => h.id === id);
  const from = await css(page, handle.point, true),
    to = await css(page, [
      handle.point[0] + delta[0],
      handle.point[1] + delta[1],
    ]);
  await page.mouse.move(from.x, from.y);
  await page.mouse.down();
  await page.mouse.move(to.x, to.y, { steps: 6 });
  await page.mouse.up();
  await expect(action(page, "play")).toBeEnabled();
}
const cases: [string, string, string[], number[]][] = [
  [
    "projectile_ground",
    "launch",
    ["params.launch_speed", "params.launch_angle"],
    [25, -18],
  ],
  [
    "projectile_cliff",
    "launch",
    ["params.launch_speed", "params.launch_angle"],
    [22, -15],
  ],
  ["incline", "block", ["params.start_position"], [-25, 15]],
  ["pendulum", "bob", ["params.release_angle"], [-25, 6]],
  ["spring_horizontal", "spring_end", ["params.initial_stretch"], [25, 0]],
  ["spring_vertical", "spring_end", ["params.initial_stretch"], [0, 20]],
  ["atwood", "pulley_0", ["params.initial_displacement"], [0, 20]],
  ["table_pulley", "pulley_0", ["params.initial_displacement"], [20, 0]],
  ["incline_pulley", "pulley_0", ["params.initial_displacement"], [20, -10]],
  ["collision", "collision_B1", ["bodies.B1.initial.position.x"], [20, 0]],
];
for (const [name, handle, paths, delta] of cases) {
  test(`Explore pointer ${name}: ownership, constraints, transaction, replay and project`, async ({
    page,
  }) => {
    await open(page, name);
    const before = await state(page);
    expect(before.supported).toBe(true);
    expect(before.frame0.passed).toBe(true);
    expect(before.editing).toBe(false);
    await drag(page, handle, delta);
    const after = await state(page);
    expect(after.selected).toBe(
      before.physicsHandles.find((h: any) => h.id === handle).object,
    );
    expect(after.project.scene).toEqual(before.project.scene);
    for (const path of paths) {
      const n = after.project.parameter_overrides[path];
      expect(Number.isFinite(n)).toBe(true);
      expect(n).not.toBe(before.project.parameter_overrides[path]);
      const binding = after.project.scene.bindings.find(
        (b: any) => b.path === path,
      );
      await expect(
        page.locator(`[data-parameter="${binding.id}"] input[type="number"]`),
      ).toHaveValue(String(n));
    }
    expect(after.initialState).not.toEqual(before.initialState);
    expect(after.supported).toBe(true);
    if (name === "pendulum") {
      const pivot = after.project.scene.links[0].a.point;
      const length = (s: any) =>
        Math.hypot(
          s.initialLayout.bodies[0].anchor[0] - pivot[0],
          s.initialLayout.bodies[0].anchor[1] - pivot[1],
        );
      expect(length(after)).toBeCloseTo(length(before), 7);
    }
    if (["atwood", "table_pulley", "incline_pulley"].includes(name)) {
      const q =
        after.project.parameter_overrides["params.initial_displacement"];
      expect(
        after.initialState.positions.B2.y - before.initialState.positions.B2.y,
      ).toBeCloseTo(q, 7);
      if (name === "atwood")
        expect(
          after.initialState.positions.B1.y -
            before.initialState.positions.B1.y,
        ).toBeCloseTo(-q, 7);
      for (const link of after.initialLayout.links) {
        const source = after.project.scene.links.find(
          (l: any) => l.id === link.id,
        );
        for (const [end, point] of [
          [source.a, link.points[0]],
          [source.b, link.points.at(-1)],
        ]) {
          const body = after.initialLayout.bodies.find(
            (b: any) => b.id === end.ref,
          );
          const original = after.project.scene.bodies.find(
            (b: any) => b.id === end.ref,
          );
          expect(
            Math.hypot(point[0] - body.anchor[0], point[1] - body.anchor[1]),
          ).toBeCloseTo(
            Math.hypot(
              end.point[0] - original.anchor[0],
              end.point[1] - original.anchor[1],
            ),
            6,
          );
        }
      }
    }
    if (name === "collision")
      expect(after.metrics.contact_time).toBeLessThan(
        before.metrics.contact_time,
      );
    await action(page, "undo").click();
    expect((await state(page)).project).toEqual(before.project);
    await expect(action(page, "undo")).toBeDisabled();
    await action(page, "redo").click();
    expect((await state(page)).project).toEqual(after.project);
    await action(page, "play").click();
    await expect
      .poll(async () => (await state(page)).time)
      .toBeGreaterThan(0.01);
    await action(page, "reset").click();
    expect((await state(page)).time).toBe(0);
    expect((await state(page)).project).toEqual(after.project);
    await page.getByTestId("mechanics-import").setInputFiles({
      name: `${name}.json`,
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify(after.project)),
    });
    await expect(action(page, "play")).toBeEnabled();
    expect((await state(page)).project).toEqual(after.project);
    const output = path.resolve("../.cache/mechanics-reconstruction/visual");
    mkdirSync(output, { recursive: true });
    await page.screenshot({
      path: path.join(output, `${name}-explore.png`),
      fullPage: true,
    });
  });
}

test("Escape cancels a captured drag; zoom, keyboard and second pulley body remain physical", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1024, height: 900 });
  await open(page, "atwood");
  const before = await state(page),
    p = await css(page, before.physicsHandles[1].point, true);
  await page.mouse.move(p.x, p.y);
  await page.mouse.down();
  await page.mouse.move(p.x, p.y + 30, { steps: 3 });
  await page.getByTestId("mechanics-canvas").press("Escape");
  await page.mouse.up();
  expect((await state(page)).project).toEqual(before.project);
  await page
    .locator('.mechanics-workspace [data-field="zoom"]')
    .selectOption("1.5");
  await drag(page, "pulley_1", [0, 18]);
  const q = (await state(page)).project.parameter_overrides[
    "params.initial_displacement"
  ];
  await page.getByTestId("mechanics-canvas").press("ArrowDown");
  expect(
    (await state(page)).project.parameter_overrides[
      "params.initial_displacement"
    ],
  ).toBeGreaterThan(q);
});

test("a corrected blocking mass immediately enables the mounted solver and preserves original recognition", async ({
  page,
}) => {
  await open(page, "incline");
  const p = (await state(page)).project;
  p.scene.bodies[0].mass = {
    number: -1,
    unit: "kg",
    status: "given",
    source: "ocr",
    confidence: 0.8,
  };
  p.scene.meta.provenance = "unsupported";
  p.scene.warnings.push({
    code: "invalid_mass",
    ref: "B1",
    message_key: "mech.invalid_mass",
  });
  p.current_scene = structuredClone(p.scene);
  await page.getByTestId("mechanics-import").setInputFiles({
    name: "repair.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(p)),
  });
  await expect(action(page, "play")).toBeDisabled();
  const mass = page.locator('[data-parameter="mass_B1"] input[type="number"]');
  await mass.fill("2");
  await mass.press("Tab");
  await expect(action(page, "play")).toBeEnabled();
  const fixed = await state(page);
  expect(fixed.project.scene.bodies[0].mass.number).toBe(-1);
  expect(fixed.project.current_scene.bodies[0].mass.number).toBe(2);
  expect(fixed.project.current_scene.meta.provenance).toBe("authored");
  expect(fixed.project.recognition_scene).toEqual(p.recognition_scene);
  expect(fixed.frame0.passed).toBe(true);
});

test("a legacy pendulum exposes angular speed and keeps a measured linear speed when length changes", async ({
  page,
}) => {
  await open(page, "pendulum");
  const p = (await state(page)).project;
  p.version = 1;
  delete p.recognition_scene;
  p.scene.params.angular_speed = {
    number: 4,
    unit: "rad/s",
    status: "assumed",
    source: "constraint",
    confidence: 0,
  };
  p.scene.bindings = p.scene.bindings.filter(
    (b: any) => b.path !== "params.angular_speed",
  );
  p.scene.warnings.push({
    code: "pendulum_speed_converted",
    ref: "L1",
    message_key: "mech.pendulum_speed_converted",
  });
  p.current_scene = structuredClone(p.scene);
  await page.getByTestId("mechanics-import").setInputFiles({
    name: "legacy-pendulum.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(p)),
  });
  await expect(action(page, "play")).toBeEnabled();
  const before = await state(page),
    length = page.locator('[data-parameter="length"] input[type="number"]');
  await length.fill("1.2");
  await length.press("Tab");
  const after = await state(page),
    originalSpeed =
      before.project.scene.params.angular_speed.number *
      before.project.scene.links[0].length_m.number,
    velocity = after.initialState.velocities.B1;
  expect(after.project.current_scene.params.angular_speed.number).toBeCloseTo(
    originalSpeed / 1.2,
    8,
  );
  expect(Math.hypot(velocity.x, velocity.y)).toBeCloseTo(originalSpeed, 8);
  const omega = page.locator(
    '[data-parameter="angular_speed"] input[type="number"]',
  );
  await omega.fill("3");
  await omega.press("Tab");
  await length.fill("1.1");
  await length.press("Tab");
  const edited = await state(page);
  expect(edited.project.current_scene.params.angular_speed.number).toBe(3);
  expect(edited.project.recognition_scene).toEqual(p.scene);
  await page.getByTestId("mechanics-import").setInputFiles({
    name: "pendulum-replay.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(edited.project)),
  });
  expect((await state(page)).project).toEqual(edited.project);
});
