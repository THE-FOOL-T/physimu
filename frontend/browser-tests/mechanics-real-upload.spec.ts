import { test, expect, type Page } from "@playwright/test";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

const source = path.resolve(
  "../backend/tests/mechanics/assets/user-pendulum.png",
);
const output = path.resolve("../.cache/real-mechanics-v2/visual");
const state = (page: Page) =>
  page.evaluate(() => (window as any).mechanicsWorkspace);
const action = (page: Page, name: string) =>
  page.locator(`.mechanics-workspace [data-action="${name}"]`);

test("actual user pendulum upload: genuine stages, evidence, physics, inspector, drag and portable replay", async ({
  page,
}) => {
  test.setTimeout(120000);
  mkdirSync(output, { recursive: true });
  const jobs: any[] = [];
  page.on("response", (response) => {
    if (/\/api\/analyze\/[a-f0-9]{32}(?:\?|$)/.test(response.url()))
      void response
        .json()
        .then((job) => jobs.push(job))
        .catch(() => {});
  });
  await page.goto("/");
  await page.getByTestId("domain-switch").selectOption("mechanics");
  await page.getByTestId("mechanics-fixture").selectOption("projectile_cliff");
  await expect(action(page, "play")).toBeEnabled();
  await page.getByTestId("mechanics-image").setInputFiles(source);
  await expect(page.getByTestId("mechanics-fixture")).toHaveValue(
    "choose_fixture",
  );
  await expect(page.getByTestId("mechanics-upload-receipt")).toContainText(
    "user pendulum",
  );
  await expect(page.getByTestId("mechanics-upload-receipt")).toHaveAttribute(
    "title",
    "user-pendulum.png",
  );
  await expect(page.getByTestId("mechanics-source-preview")).toBeVisible();
  await expect(
    page.locator(
      '[data-testid="mechanics-analysis-stepper"] [data-stage="text"]',
    ),
  ).toHaveAttribute("data-status", "running", { timeout: 30000 });
  await expect(page.getByTestId("mechanics-source-identity")).toContainText(
    "Analyzing this uploaded image",
  );
  await expect(action(page, "play")).toBeDisabled();
  expect(
    (await state(page)).analysis.detections.some(
      (d: any) => d.type === "bob" && d.source === "classical_vision",
    ),
  ).toBe(true);
  await page.screenshot({
    path: path.join(output, "pendulum-reading.png"),
    fullPage: true,
  });
  await expect(action(page, "play")).toBeEnabled({ timeout: 90000 });
  await expect(
    page.locator(
      '[data-testid="mechanics-analysis-stepper"] [data-stage="done"]',
    ),
  ).toHaveAttribute("data-status", "completed");
  await expect(page.getByTestId("mechanics-source-identity")).toContainText(
    "Recognized system: Simple Pendulum",
  );
  const ready = await state(page),
    scene = ready.project.scene;
  expect(
    await page.evaluate(
      async ({ original, analyzed }) => {
        const pixels = async (url: string) => {
          const image = await createImageBitmap(
            await (await fetch(url)).blob(),
          );
          const canvas = document.createElement("canvas");
          canvas.width = image.width;
          canvas.height = image.height;
          const ctx = canvas.getContext("2d")!;
          ctx.drawImage(image, 0, 0);
          return ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        };
        const a = await pixels(original),
          b = await pixels(analyzed);
        return (
          a.length === b.length && a.every((value, index) => value === b[index])
        );
      },
      {
        original: `data:image/png;base64,${readFileSync(source).toString("base64")}`,
        analyzed: ready.project.source_image,
      },
    ),
  ).toBe(true);
  expect(scene.image).toMatchObject({ width: 1024, height: 765 });
  expect(scene.archetype).toBe("pendulum");
  expect(scene.bodies).toHaveLength(1);
  expect(scene.links).toHaveLength(1);
  expect(scene.bodies[0].mass.number).toBe(0.5);
  expect(scene.links[0].length_m.number).toBe(1.2);
  expect(scene.params.release_angle.number).toBe(15);
  expect(
    scene.annotations.filter((a: any) => a.id.startsWith("alternate_state_")),
  ).toHaveLength(2);
  expect(ready.analysis.sourceKind).toBe("upload");
  expect(ready.analysis.method).toBe("classical_vision");
  expect(ready.editing).toBe(false);
  expect(ready.supported).toBe(true);
  expect(
    Math.hypot(
      ready.initialState.positions.B1.x,
      ready.initialState.positions.B1.y,
    ),
  ).toBeCloseTo(1.2, 5);
  expect(ready.metrics.small_angle_period).toBeCloseTo(
    2 * Math.PI * Math.sqrt(1.2 / 9.81),
    8,
  );
  const actual = jobs.findLast((job) => job.result)?.result;
  expect(actual?.domain).toBe("mechanics");
  expect(actual.scene).toEqual(scene);
  expect(actual.source_image).toBe(ready.project.source_image);
  expect(
    jobs.some((job) => job.partial?.detections?.length > 0 && !job.result),
  ).toBe(true);
  expect(
    jobs.some(
      (job) =>
        job.partial?.texts?.length > 0 ||
        job.result?.diagnostics?.texts?.length > 0,
    ),
  ).toBe(true);
  writeFileSync(
    path.join(output, "pendulum-analysis.json"),
    JSON.stringify(actual, null, 2),
  );
  await page.screenshot({
    path: path.join(output, "pendulum-ready.png"),
    fullPage: true,
  });
  await action(page, "play").click();
  await expect.poll(async () => (await state(page)).time).toBeGreaterThan(0.3);
  const playing = await state(page);
  expect(playing.currentState.positions.B1).not.toEqual(
    ready.initialState.positions.B1,
  );
  expect(
    Math.hypot(
      playing.currentState.positions.B1.x,
      playing.currentState.positions.B1.y,
    ),
  ).toBeCloseTo(1.2, 5);
  await page.screenshot({
    path: path.join(output, "pendulum-playing.png"),
    fullPage: true,
  });
  await action(page, "reset").click();
  const before = await state(page),
    handle = before.physicsHandles.find((h: any) => h.id === "bob");
  const canvas = page.getByTestId("mechanics-canvas");
  await canvas.scrollIntoViewIfNeeded();
  const box = (await canvas.boundingBox())!;
  const dimensions = await canvas.evaluate((c: HTMLCanvasElement) => ({
    w: c.width,
    h: c.height,
  }));
  const point = (x: number, y: number) => ({
    x:
      box.x +
      ((x + before.padding.left) * before.dpr * box.width) / dimensions.w,
    y:
      box.y +
      ((y + before.padding.top) * before.dpr * box.height) / dimensions.h,
  });
  const from = point(...(handle.point as [number, number])),
    to = point(handle.point[0] + 35, handle.point[1] - 10);
  await page.mouse.move(from.x, from.y);
  await page.mouse.down();
  await page.mouse.move(to.x, to.y, { steps: 6 });
  await page.mouse.up();
  const dragged = await state(page);
  expect(dragged.project.parameter_overrides["params.release_angle"]).not.toBe(
    15,
  );
  expect(dragged.initialState).not.toEqual(before.initialState);
  expect(dragged.project.scene).toEqual(scene);
  const mass = page.locator('[data-parameter="mass_B1"] input[type="number"]');
  await mass.fill("0.8");
  await mass.press("Tab");
  expect((await state(page)).initialState.scalars.tension).toBeGreaterThan(
    dragged.initialState.scalars.tension,
  );
  const saved = (await state(page)).project;
  await page.getByTestId("mechanics-import").setInputFiles({
    name: "real-pendulum-project.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(saved)),
  });
  await expect(action(page, "play")).toBeEnabled();
  expect((await state(page)).project).toEqual(saved);
  expect((await state(page)).analysis.sourceKind).toBe("project");
  await action(page, "reset").click();
  expect((await state(page)).time).toBe(0);
  writeFileSync(
    path.join(output, "pendulum-scene.json"),
    JSON.stringify(scene, null, 2),
  );
  writeFileSync(
    path.join(output, "pendulum-physics.json"),
    JSON.stringify(
      {
        metrics: ready.metrics,
        initial: ready.initialState,
        playing: playing.currentState,
        afterDrag: dragged.initialState,
        overrides: dragged.project.parameter_overrides,
        afterMass: saved.current_scene.bodies[0].mass,
        replay: (await state(page)).initialState,
      },
      null,
      2,
    ),
  );
});

test("actual raster with unread mass and length retains evidence and needs only parameter repair", async ({
  page,
}) => {
  test.setTimeout(120000);
  await page.goto("/");
  await page.getByTestId("domain-switch").selectOption("mechanics");
  const encoded = await page.evaluate(
    async (url) => {
      const image = await createImageBitmap(await (await fetch(url)).blob());
      const canvas = document.createElement("canvas");
      canvas.width = image.width;
      canvas.height = image.height;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(image, 0, 0);
      ctx.fillStyle = "white";
      ctx.fillRect(620, 240, 195, 65);
      ctx.fillRect(395, 600, 215, 65);
      return canvas.toDataURL("image/png").split(",")[1];
    },
    `data:image/png;base64,${readFileSync(source).toString("base64")}`,
  );
  await page.getByTestId("mechanics-image").setInputFiles({
    name: "unread-labels.png",
    mimeType: "image/png",
    buffer: Buffer.from(encoded, "base64"),
  });
  await expect
    .poll(
      async () =>
        (await state(page)).analysis.stages.find((s: any) => s.id === "build")
          ?.status,
      { timeout: 90000 },
    )
    .toBe("blocked");
  const failed = await state(page);
  expect(failed.project.scene.archetype).toBe("pendulum");
  expect(failed.project.scene.bodies[0].mass.number).toBeNull();
  expect(failed.project.scene.links[0].length_m.number).toBeNull();
  expect(failed.editing).toBe(true);
  await expect(action(page, "play")).toBeDisabled();
  await expect(page.getByTestId("mechanics-readiness")).toContainText(
    "Simulation blocked",
  );
  const length = page.getByRole("spinbutton", {
    name: "Length number",
    exact: true,
  });
  await length.fill("1.2");
  await length.press("Tab");
  const mass = page.locator('[data-parameter="mass_B1"] input[type="number"]');
  await mass.fill("0.5");
  await mass.press("Tab");
  await expect(action(page, "play")).toBeEnabled();
  await expect(
    page.locator(
      '[data-testid="mechanics-analysis-stepper"] [data-stage="done"]',
    ),
  ).toHaveAttribute("data-status", "completed");
  const fixed = await state(page);
  expect(fixed.editing).toBe(false);
  expect(
    fixed.project.current_scene.warnings.some((w: any) =>
      ["missing_mass", "missing_length"].includes(w.code),
    ),
  ).toBe(false);
  expect(fixed.project.recognition_scene.bodies[0].mass.number).toBeNull();
  expect(fixed.project.recognition_scene.links[0].length_m.number).toBeNull();
  expect(fixed.project.scene.bodies[0].anchor).toEqual(
    failed.project.scene.bodies[0].anchor,
  );
  expect(fixed.project.scene.params.release_angle.number).toBe(15);
  expect(
    Math.hypot(
      fixed.initialState.positions.B1.x,
      fixed.initialState.positions.B1.y,
    ),
  ).toBeCloseTo(1.2, 6);
});

test("ambiguous raster offers measured candidates and requires an explicit choice", async ({
  page,
}) => {
  test.setTimeout(120000);
  await page.goto("/");
  await page.getByTestId("domain-switch").selectOption("mechanics");
  const encoded = await page.evaluate(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 600;
    canvas.height = 400;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, 600, 400);
    ctx.strokeStyle = ctx.fillStyle = "black";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(100, 50);
    ctx.lineTo(500, 50);
    ctx.stroke();
    for (const x of [220, 380]) {
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(300, 50);
      ctx.lineTo(x, 250);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(x, 250, 19, 0, 2 * Math.PI);
      ctx.fill();
    }
    return canvas.toDataURL().split(",")[1];
  });
  await page.getByTestId("mechanics-image").setInputFiles({
    name: "ambiguous-pendulums.png",
    mimeType: "image/png",
    buffer: Buffer.from(encoded, "base64"),
  });
  const candidates = page.getByTestId("mechanics-pendulum-candidates");
  await expect(candidates.getByRole("button").first()).toBeVisible({
    timeout: 90000,
  });
  expect(await candidates.getByRole("button").count()).toBeGreaterThanOrEqual(
    2,
  );
  await expect(action(page, "play")).toBeDisabled();
  expect((await state(page)).project.scene.bodies).toHaveLength(0);
  const confirmed = page.waitForResponse(
    async (response) =>
      response.request().method() === "GET" &&
      response.url().includes("/api/analyze/") &&
      !!(await response.json()).result?.diagnostics?.classical
        ?.confirmed_by_user,
    { timeout: 90000 },
  );
  await candidates.getByRole("button").first().click();
  const result = (await (await confirmed).json()).result;
  expect(result.diagnostics.classical.accepted).toBe(true);
  expect(result.diagnostics.classical.confirmed_by_user).toBe(true);
  expect(result.scene.archetype).toBe("pendulum");
  expect(result.scene.bodies).toHaveLength(1);
  await expect
    .poll(async () => (await state(page)).project.scene.archetype)
    .toBe("pendulum");
});
