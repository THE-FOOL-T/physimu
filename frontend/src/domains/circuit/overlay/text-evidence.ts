import type { Netlist, OCRText } from "../types";

export function textAt(texts: OCRText[], x: number, y: number) {
  return [...texts]
    .reverse()
    .find(
      (item) =>
        x >= item.bbox[0] &&
        x <= item.bbox[2] &&
        y >= item.bbox[1] &&
        y <= item.bbox[3],
    );
}

export function drawTextEvidence(
  ctx: CanvasRenderingContext2D,
  net: Netlist,
  texts: OCRText[],
  scale: number,
) {
  ctx.save();
  ctx.lineWidth = 1.5 / scale;
  ctx.setLineDash([]);
  for (const item of texts) {
    const [x, y, x2, y2] = item.bbox;
    ctx.strokeStyle =
      item.outcome === "assigned"
        ? "#168149"
        : item.outcome === "ignored"
          ? "#737d88"
          : "#b76a00";
    ctx.fillStyle =
      item.outcome === "assigned"
        ? "#16814918"
        : item.outcome === "ignored"
          ? "#737d8818"
          : "#b76a0018";
    ctx.fillRect(x, y, x2 - x, y2 - y);
    ctx.strokeRect(x, y, x2 - x, y2 - y);
    const c = net.components.find((c) => c.id === item.assigned_to);
    if (c && item.outcome === "assigned") {
      ctx.beginPath();
      ctx.moveTo((x + x2) / 2, (y + y2) / 2);
      ctx.lineTo((c.bbox[0] + c.bbox[2]) / 2, (c.bbox[1] + c.bbox[3]) / 2);
      ctx.stroke();
    }
  }
  ctx.restore();
}
