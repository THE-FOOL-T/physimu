import { test, expect } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { imagePoint } from "./coordinates";
for (const width of [1440, 1024, 390])
  for (const lang of ["en", "bn"])
    test(`part slider runs immediately and stays frozen in a draft ${width} ${lang}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.addInitScript(
        (lang) => localStorage.setItem("circuit-language", lang),
        lang,
      );
      await page.goto("/");
      await expect(page.locator("#controls .control")).toHaveCount(7);
      let p = await imagePoint(page, 180, 46);
      await page.mouse.click(p.x, p.y);
      const slider = page.getByTestId("part-slider"),
        before = await page.locator("#supplied").textContent();
      await slider.fill("7000");
      await expect(page.locator("#part-value")).toHaveValue("7000");
      await expect(page.locator("#supplied")).not.toHaveText(before!);
      await page.locator(".part-popover button").first().click();
      await page.locator("#edit").click();
      p = await imagePoint(page, 180, 46);
      await page.mouse.click(p.x, p.y);
      const frozen = await page.locator("#supplied").textContent();
      await slider.fill("8000");
      await expect(page.locator("#supplied")).toHaveText(frozen!);
      await expect(page.locator("#part-value")).toHaveValue("8000");
      await page.locator("#undo").click();
      await expect(slider).toHaveValue("7000");
      await expect(page.locator("#part-value")).toHaveValue("7000");
      mkdirSync("../.cache/round3/ui/quick", { recursive: true });
      await page.screenshot({
        path: `../.cache/round3/ui/quick/${width}-${lang}.png`,
        fullPage: true,
        animations: "disabled",
      });
    });
