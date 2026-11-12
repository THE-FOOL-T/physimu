import { test, expect } from "@playwright/test";
import { imagePoint } from "./coordinates";

test("live explanations, Bangla digits and unsupported block", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await page.locator("[data-tab=explain]").click();
  await expect(page.getByTestId("explanations")).toContainText(
    "Equivalent resistance",
  );
  const before = await page.getByTestId("explanations").innerText();
  await page.locator("[data-tab=parameters]").click();
  await page.locator("input[type=number][data-param=R1]").fill("10000");
  await page.locator("[data-tab=explain]").click();
  await expect(page.getByTestId("explanations")).not.toHaveText(before);
  await page.locator("#language").click();
  await page.locator("#digits").check();
  await expect(page.getByTestId("explanations")).toContainText("তুল্য রোধ");
  expect(await page.getByTestId("explanations").innerText()).toMatch(/[০-৯]/);
  await page.locator("#edit").click();
  const p = await imagePoint(page, 180, 46);
  await page.mouse.click(p.x, p.y);
  await page.locator("[data-part-type=diode]").click();
  await expect(page.locator("#inspector")).toContainText("অজানা অংশ");
  await expect(page.locator("#readout tr")).toHaveCount(7);
  await expect(page.locator("#readout [data-select=R1]")).toContainText(
    "অজানা",
  );
});
