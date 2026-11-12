import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

test("blocked storage still loads, translates and edits a circuit", async ({
  page,
}) => {
  await page.addInitScript(() =>
    Object.defineProperty(window, "localStorage", {
      get() {
        throw Error("blocked storage");
      },
    }),
  );
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("#language").click();
  await page.locator("#digits").check();
  await page.locator("#theme").click();
  await page.getByTestId("source-slider").fill("6");
  await expect(page.locator("#source-chip input[type=number]")).toHaveValue(
    "6",
  );
});

test("embedded uploads export a self contained image and support replacement", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  const net = JSON.parse(
    readFileSync("../fixtures/editor_loop.json", "utf8"),
  ).netlist;
  net.image.path =
    "data:image/png;base64," +
    readFileSync("public/demos/mixed-network.png").toString("base64");
  await page.locator("#json-upload").setInputFiles({
    name: "Embedded.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(net)),
  });
  await expect(page.locator("#readout tr")).toHaveCount(2);
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.locator("#save").click(),
  ]);
  const exported = JSON.parse(readFileSync((await download.path())!, "utf8"));
  expect(exported.image.path).toMatch(/^data:image\/png;base64,/);
  await page.locator("#image-upload").setInputFiles({
    name: "replacement.png",
    mimeType: "image/png",
    buffer: readFileSync("public/demos/mixed-network.png"),
  });
  await expect(page.locator("#overlay")).toHaveAttribute(
    "data-image-ready",
    "true",
  );
});
