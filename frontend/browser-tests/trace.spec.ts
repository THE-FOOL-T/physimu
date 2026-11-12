import { test, expect } from "@playwright/test";
import { readFileSync, mkdirSync } from "node:fs";

for (const lang of ["en", "bn"])
  test(`trace issue opens a visible correction location ${lang}`, async ({
    page,
  }) => {
    const net = JSON.parse(
      readFileSync("public/demos/mixed-network.json", "utf8"),
    );
    net.wire_graph.points.push({
      id: "loose",
      node: net.nodes[0].id,
      xy: [80, 90],
      kind: "bend",
    });
    net.warnings.push({
      code: "dangling_wire",
      ref: "loose",
      message_key: "warn.dangling_wire",
    });
    const anchor = net.wire_graph.points.find(
      (p: { node: string }) => p.node === net.nodes[0].id,
    );
    net.wire_graph.segments.push({
      id: "loose-wire",
      from: anchor.id,
      to: "loose",
      node: net.nodes[0].id,
      polyline: [anchor.xy, [80, 90]],
      confidence: 1,
    });
    await page.addInitScript(
      (lang) => localStorage.setItem("circuit-language", lang),
      lang,
    );
    await page.goto("/");
    await expect(page.locator("#readout tr")).toHaveCount(7);
    await page.locator("#json-upload").setInputFiles({
      name: "loose.json",
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify(net)),
    });
    await page.locator("[data-tab=warnings]").click();
    await page.locator("[data-check=loose]").click();
    await expect(page.locator(".editing-badge")).toBeVisible();
    await expect(page.locator("#overlay")).toBeInViewport();
    mkdirSync("../.cache/round3/ui", { recursive: true });
    await page.locator(".center").screenshot({
      path: `../.cache/round3/ui/trace-${lang}.png`,
      animations: "disabled",
    });
  });
