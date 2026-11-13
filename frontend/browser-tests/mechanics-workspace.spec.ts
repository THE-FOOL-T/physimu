import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
const root = path.resolve(process.cwd(), "..");
const state = (page: Page) =>
  page.evaluate(() => (window as any).mechanicsWorkspace);
async function open(page: Page, name = "pendulum") {
  await page.goto("/");
  await page.getByTestId("domain-switch").selectOption("mechanics");
  await expect(page.getByTestId("mechanics-workspace")).toBeVisible();
  await page.getByTestId("mechanics-fixture").selectOption(name);
  await expect(page.getByTestId("mechanics-workspace")).toHaveAttribute(
    "data-ready",
    "true",
  );
  await expect(
    page.locator('.mechanics-workspace [data-action="play"]'),
  ).toBeEnabled();
}
const action = (page: Page, name: string) =>
  page.locator(`.mechanics-workspace [data-action="${name}"]`);
async function field(page: Page, name: string, value: string) {
  const node = page.locator(`.mechanics-workspace [data-field="${name}"]`);
  await node.fill(value);
  await node.press("Tab");
}

test("mounted workspace loads, plays, pauses, steps, switches and retains both documents", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await open(page);
  await action(page, "play").click();
  await expect.poll(async () => (await state(page)).time).toBeGreaterThan(0.05);
  await action(page, "pause").click();
  const stopped = (await state(page)).time;
  await page.getByTestId("domain-switch").selectOption("circuit");
  await expect(page.getByTestId("mechanics-workspace")).toHaveCount(0);
  await page.getByTestId("domain-switch").selectOption("mechanics");
  expect((await state(page)).time).toBe(stopped);
  await action(page, "reset").click();
  await action(page, "step").click();
  expect((await state(page)).time).toBeCloseTo(1 / 240);
  expect(errors).toEqual([]);
});
test("author edits name/type/box/mask/value with undo redo, validation and unknown handling", async ({
  page,
}) => {
  await open(page);
  await action(page, "edit_scene").click();
  await field(page, "name", "QA bob");
  expect(
    (await state(page)).project.scene.annotations.some(
      (a: any) => a.geometry.text === "QA bob",
    ),
  ).toBe(true);
  await field(page, "box", "440, 300, 490, 350");
  expect((await state(page)).project.scene.bodies[0].bbox).toEqual([
    440, 300, 490, 350,
  ]);
  await field(page, "sprite_mask", "[[442,302],[488,302],[488,348],[442,348]]");
  const mask = (await state(page)).project.scene.bodies[0].mask;
  await action(page, "undo").click();
  expect((await state(page)).project.scene.bodies[0].mask).not.toEqual(mask);
  await action(page, "redo").click();
  expect((await state(page)).project.scene.bodies[0].mask).toEqual(mask);
  await field(page, "object_type", "unknown_bob");
  expect((await state(page)).supported).toBe(false);
  await field(page, "object_type", "bob");
  expect((await state(page)).supported).toBe(true);
  const prior = (await state(page)).project.scene.bodies[0].bbox;
  await field(page, "box", "5,5,1,1");
  await expect(page.getByTestId("mechanics-notice")).toContainText("positive");
  expect((await state(page)).project.scene.bodies[0].bbox).toEqual(prior);
});
test("default mounted mechanics accessibility", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("domain-switch").selectOption("mechanics");
  expect(
    (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
      .violations,
  ).toEqual([]);
  await open(page);
  expect(
    (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
      .violations,
  ).toEqual([]);
});

for (const name of [
  "projectile_ground",
  "projectile_cliff",
  "incline",
  "pendulum",
  "spring_horizontal",
  "spring_vertical",
  "atwood",
  "table_pulley",
  "incline_pulley",
  "collision",
]) {
  test(`mounted fixture ${name}: frame zero, play and reset`, async ({
    page,
  }) => {
    await open(page, name);
    const before = await state(page);
    expect(before.supported).toBe(true);
    expect(before.frame0.passed).toBe(true);
    await action(page, "play").click();
    await expect
      .poll(async () => (await state(page)).time)
      .toBeGreaterThan(0.01);
    await action(page, "pause").click();
    await action(page, "reset").click();
    expect((await state(page)).time).toBe(0);
    expect((await state(page)).project.scene).toEqual(before.project.scene);
  });
}
test("all binding classes preserve source, locks and original reset", async ({
  page,
}) => {
  await open(page, "incline");
  const before = await state(page);
  const row = (id: string) =>
    page.locator(`.mechanics-workspace [data-parameter="${id}"]`);
  await row("mass_B1").locator('input[type="number"]').fill("3");
  await row("mass_B1").locator('input[type="number"]').press("Tab");
  expect(
    (await state(page)).project.current_scene.bodies[0].mass,
  ).toMatchObject({ number: 3, status: "user", source: "user", confidence: 1 });
  expect((await state(page)).background).toBe(before.background);
  await row("position").locator('input[type="number"]').fill("1.5");
  await row("position").locator('input[type="number"]').press("Tab");
  expect((await state(page)).background).toBe(before.background);
  await expect(row("theta")).toHaveCount(0);
  await action(page, "edit_scene").click();
  await expect(row("theta").locator('input[type="range"]')).toBeDisabled();
  await row("theta").locator("button").click();
  await row("theta").locator('input[type="number"]').fill("35");
  await row("theta").locator('input[type="number"]').press("Tab");
  await expect(page.getByTestId("mechanics-modified")).toHaveText("Modified");
  expect((await state(page)).project.scene).toEqual(before.project.scene);
  await row("theta").locator("button").click();
  await expect(row("theta").locator('input[type="number"]')).toBeDisabled();
  await action(page, "back_original").click();
  expect((await state(page)).project.current_scene).toEqual(
    before.project.scene,
  );
  expect((await state(page)).project.parameter_overrides).toEqual({});
});
test("draw every missing line, attach rope/spring ends, edit repairs and assign Values", async ({
  page,
}) => {
  await open(page, "atwood");
  await action(page, "edit_scene").click();
  for (const type of ["rope", "spring", "incline", "floor"]) {
    await page.getByTestId("mechanics-tool").selectOption(type);
    const canvas = page.getByTestId("mechanics-canvas");
    await canvas.click({ position: { x: 60, y: 140 } });
    await canvas.click({ position: { x: 180, y: 210 } });
  }
  let s = (await state(page)).project.scene;
  expect(s.links.some((v: any) => v.type === "spring")).toBe(true);
  expect(s.surfaces.some((v: any) => v.type === "incline")).toBe(true);
  const spring = s.links.find((v: any) => v.type === "spring");
  await page
    .locator('.mechanics-workspace [data-field="object"]')
    .selectOption(spring.id);
  await page
    .locator('.mechanics-workspace [data-field="attach_a"]')
    .selectOption("B1");
  await page
    .locator('.mechanics-workspace [data-field="attach_b"]')
    .selectOption("B2");
  await field(page, "end_a", "250, 210");
  await field(page, "end_b", "470, 260");
  await field(page, "repair_segments", "[[[200,200],[220,220]]]");
  s = (await state(page)).project.scene;
  expect(s.links.find((v: any) => v.id === spring.id).a.ref).toBe("B1");
  expect(s.repairs.at(-1).segments).toEqual([
    [
      [200, 200],
      [220, 220],
    ],
  ]);
  await action(page, "add_value").click();
  await field(page, "value", "4");
  await page
    .locator('.mechanics-workspace [data-field="assign_to"]')
    .selectOption("bodies.B1.mass");
  await action(page, "assign_value").click();
  expect((await state(page)).project.scene.bodies[0].mass.number).toBe(4);
  await expect(page.locator('[data-chip="unplaced_1"]')).toHaveCount(0);
  const pulley = (await state(page)).project.scene.pulleys[0];
  await page
    .locator('.mechanics-workspace [data-field="object"]')
    .selectOption(pulley.id);
  await field(page, "centre", "400, 140");
  expect((await state(page)).project.scene.pulleys[0].center).toEqual([
    400, 140,
  ]);
  await action(page, "add_body").click();
  expect((await state(page)).project.scene.bodies).toHaveLength(3);
  expect((await state(page)).project.scene.bodies.at(-1).mass.status).toBe(
    "assumed",
  );
  await action(page, "undo").click();
  expect((await state(page)).project.scene.bodies).toHaveLength(2);
});
test("native handles, keyboard movement, masks and incline geometry edits", async ({
  page,
}) => {
  await open(page, "incline");
  await action(page, "edit_scene").click();
  await page
    .locator('.mechanics-workspace [data-field="object"]')
    .selectOption("S1");
  await field(page, "tip", "640, 140");
  expect((await state(page)).project.scene.surfaces[0].polyline.at(-1)).toEqual(
    [640, 140],
  );
  await page
    .locator('.mechanics-workspace [data-field="object"]')
    .selectOption("B1");
  const old = (await state(page)).project.scene.bodies[0].anchor;
  await page.getByTestId("mechanics-canvas").press("ArrowRight");
  expect((await state(page)).project.scene.bodies[0].anchor[0]).toBeCloseTo(
    old[0] + 2,
  );
  await page.getByTestId("mechanics-tool").selectOption("mask");
  for (const p of [
    { x: 210, y: 110 },
    { x: 250, y: 110 },
    { x: 250, y: 140 },
    { x: 210, y: 140 },
  ])
    await page.getByTestId("mechanics-canvas").click({ position: p });
  await action(page, "finish_shape").click();
  expect((await state(page)).project.scene.bodies[0].mask).toHaveLength(4);
});
test("JSON/image roundtrip, rejected import and actual PNG download", async ({
  page,
}, testInfo) => {
  await open(page, "incline");
  await page
    .locator('[data-parameter="mass_B1"] input[type="number"]')
    .fill("4");
  await page
    .locator('[data-parameter="mass_B1"] input[type="number"]')
    .press("Tab");
  const before = (await state(page)).project;
  const promise = page.waitForEvent("download");
  await action(page, "export_project").click();
  const file = await (await promise).path();
  const bytes = readFileSync(file!);
  expect(JSON.parse(bytes.toString())).toEqual(before);
  await page.reload();
  await page.getByTestId("domain-switch").selectOption("mechanics");
  await page.getByTestId("mechanics-import").setInputFiles({
    name: "project.json",
    mimeType: "application/json",
    buffer: bytes,
  });
  await expect(page.getByTestId("mechanics-workspace")).toHaveAttribute(
    "data-ready",
    "true",
  );
  expect((await state(page)).project).toEqual(before);
  const bad = structuredClone(before);
  bad.current_scene.bodies[0].mass.number = 999;
  await page.getByTestId("mechanics-import").setInputFiles({
    name: "bad.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(bad)),
  });
  await expect(page.getByTestId("mechanics-notice")).toContainText("disagrees");
  expect((await state(page)).project).toEqual(before);
  const pngPromise = page.waitForEvent("download");
  await action(page, "export_png").click();
  const png = readFileSync((await (await pngPromise).path())!);
  expect(png.subarray(1, 4).toString()).toBe("PNG");
  expect(png.readUInt32BE(16)).toBe(
    await page
      .getByTestId("mechanics-canvas")
      .evaluate((c: HTMLCanvasElement) => c.width),
  );
  await testInfo.attach("overlay", { body: png, contentType: "image/png" });
});
for (const lang of ["en", "bn"]) {
  test(`blank-image authoring, unsupported editing and language ${lang}`, async ({
    page,
  }) => {
    await page.addInitScript(
      (lang) => localStorage.setItem("circuit-language", lang),
      lang,
    );
    await page.goto("/");
    await page.getByTestId("domain-switch").selectOption("mechanics");
    await page
      .getByTestId("mechanics-image")
      .setInputFiles(path.join(root, "fixtures/mechanics/pendulum.png"));
    await expect(page.getByTestId("mechanics-workspace")).toHaveAttribute(
      "data-ready",
      "true",
    );
    expect((await state(page)).project.scene.archetype).toBe("unsupported");
    await page
      .locator('.mechanics-workspace [data-field="archetype"]')
      .selectOption("pendulum");
    await action(page, "edit_scene").click();
    await action(page, "place_template").click();
    await field(page, "anchor", "470, 320");
    await action(page, "run").click();
    await expect(action(page, "play")).toBeEnabled();
    await action(page, "play").click();
    await expect
      .poll(async () => (await state(page)).time)
      .toBeGreaterThan(0.01);
    await action(page, "pause").click();
    await action(page, "fix_interpretation").click();
    await page
      .locator('.mechanics-workspace [data-field="archetype"]')
      .selectOption("unsupported");
    expect((await state(page)).project.scene.bodies).toHaveLength(1);
    await expect(action(page, "play")).toBeDisabled();
    await page.locator("#language").click();
    await expect(
      page.getByTestId("mechanics-workspace").locator("h1"),
    ).toHaveText(lang === "en" ? "বলবিদ্যা" : "Mechanics");
    expect(
      (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
        .violations,
    ).toEqual([]);
  });
}
test("Bangla digits and reduced motion are retained without autoplay", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.addInitScript(() => {
    localStorage.setItem("circuit-language", "bn");
    localStorage.setItem("circuit-digits", "true");
  });
  await open(page);
  expect((await state(page)).playing).toBe(false);
  await page.locator("#mech-tab-readouts").click();
  await expect(page.getByTestId("mechanics-readouts")).toContainText("০");
  await page.locator("#mech-tab-warnings").click();
  await expect(page.getByTestId("mechanics-warnings")).toContainText("কম গতির");
  await page.locator("#mech-tab-graphs").click();
  await expect(page.getByTestId("mechanics-graphs")).toBeVisible();
});
test("optional downloaded real diagram: author, validate, simulate and export", async ({
  page,
}) => {
  const real =
    process.env.MECHANICS_REAL_IMAGE ||
    path.join(root, ".cache/m3-real/simple-pendulum.png");
  test.skip(
    !existsSync(real),
    "Optional owner/downloaded real mechanics image is absent",
  );
  await page.goto("/");
  await page.getByTestId("domain-switch").selectOption("mechanics");
  await page.getByTestId("mechanics-image").setInputFiles(real);
  await expect(page.getByTestId("mechanics-workspace")).toHaveAttribute(
    "data-ready",
    "true",
  );
  await page
    .locator('.mechanics-workspace [data-field="archetype"]')
    .selectOption("pendulum");
  await action(page, "edit_scene").click();
  await action(page, "place_template").click();
  await page
    .locator('.mechanics-workspace [data-field="object"]')
    .selectOption("S1");
  await action(page, "delete_object").click();
  await page
    .locator('.mechanics-workspace [data-field="object"]')
    .selectOption("pivot");
  await field(page, "centre", "354, 94");
  await page
    .locator('.mechanics-workspace [data-field="object"]')
    .selectOption("B1");
  await field(page, "box", "478, 516, 536, 574");
  const mask = Array.from({ length: 24 }, (_, i) => [
    507 + 29 * Math.cos((i * Math.PI) / 12),
    545 + 29 * Math.sin((i * Math.PI) / 12),
  ]);
  await field(page, "sprite_mask", JSON.stringify(mask));
  await field(page, "paper_color", "#ffffff");
  await field(page, "ink_color", "#000000");
  await field(page, "stroke_px", "5");
  await page.locator('[data-value-path="bodies.B1.mass"]').fill("1");
  await page.locator('[data-value-path="bodies.B1.mass"]').press("Tab");
  await action(page, "run").click();
  await expect(action(page, "play")).toBeEnabled();
  await action(page, "play").click();
  await expect.poll(async () => (await state(page)).time).toBeGreaterThan(0.05);
  await action(page, "pause").click();
  expect((await state(page)).project.scene.meta.provenance).toBe("authored");
  const out = path.join(root, ".cache/m3-real");
  mkdirSync(out, { recursive: true });
  writeFileSync(
    path.join(out, "authored-qa-project.json"),
    JSON.stringify((await state(page)).project, null, 2),
  );
  await page
    .getByTestId("mechanics-canvas")
    .screenshot({ path: path.join(out, "authored-playback.png") });
  writeFileSync(
    path.join(out, "authoring-evidence.json"),
    JSON.stringify(await state(page), null, 2),
  );
});

test("pointer drag is one undo transaction; schema and image-dimension failures preserve the project", async ({
  page,
}) => {
  await open(page);
  await action(page, "edit_scene").click();
  const initial = await state(page),
    anchor = initial.project.scene.bodies[0].anchor;
  const canvas = page.getByTestId("mechanics-canvas"),
    rect = (await canvas.boundingBox())!,
    scale = rect.width / initial.project.scene.image.width;
  await page.mouse.move(rect.x + anchor[0] * scale, rect.y + anchor[1] * scale);
  await page.mouse.down();
  await page.mouse.move(
    rect.x + (anchor[0] + 20) * scale,
    rect.y + (anchor[1] + 10) * scale,
    { steps: 4 },
  );
  await page.mouse.up();
  expect((await state(page)).project.scene.bodies[0].anchor[0]).toBeCloseTo(
    anchor[0] + 20,
    1,
  );
  await action(page, "undo").click();
  expect((await state(page)).project.scene).toEqual(initial.project.scene);
  const before = (await state(page)).project,
    bad = structuredClone(before);
  bad.scene.image.width += 1;
  bad.current_scene.image.width += 1;
  await page.getByTestId("mechanics-import").setInputFiles({
    name: "wrong-size.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(bad)),
  });
  await expect(page.getByTestId("mechanics-notice")).toContainText(
    "dimensions differ",
  );
  expect((await state(page)).project).toEqual(before);
});
for (const width of [1440, 390])
  test(`mechanics visual/accessibility capture ${width} BN`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.addInitScript(() => {
      localStorage.setItem("circuit-language", "bn");
      localStorage.setItem("circuit-digits", "true");
    });
    await open(page, "incline");
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect(
      (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
        .violations,
    ).toEqual([]);
    const out = path.join(root, ".cache/m3-visual");
    mkdirSync(out, { recursive: true });
    await page.screenshot({
      path: path.join(out, `${width}-bn.png`),
      fullPage: true,
    });
  });
