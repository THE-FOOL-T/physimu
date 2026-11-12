import { expect, type Page } from "@playwright/test";

/** Use the same paper margin and Fit transform as the actual pointer handlers. */
export async function imagePoint(page: Page, x: number, y: number) {
  const canvas = page.locator("#overlay");
  await canvas.scrollIntoViewIfNeeded();
  await expect
    .poll(() =>
      canvas.evaluate((c) =>
        Math.abs(Number(c.dataset.viewWidth) - c.clientWidth),
      ),
    )
    .toBeLessThan(1);
  return canvas.evaluate(
    (c, { x, y }) => {
      const b = c.getBoundingClientRect(),
        s = Number(c.dataset.viewScale);
      return {
        x: b.x + Number(c.dataset.viewX) + x * s,
        y: b.y + Number(c.dataset.viewY) + y * s,
      };
    },
    { x, y },
  );
}
