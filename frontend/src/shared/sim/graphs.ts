export interface GraphSeries {
  label: string;
  unit: string;
  values: number[];
  color: string;
  dash: number[];
}
export function drawGraphs(
  canvas: HTMLCanvasElement,
  times: readonly number[],
  series: GraphSeries[],
  time: number,
) {
  const ctx = canvas.getContext("2d")!;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const w = canvas.width,
    h = canvas.height / Math.max(1, series.length);
  series.forEach((line, index) => {
    const top = index * h,
      min = Math.min(0, ...line.values),
      max = Math.max(0, ...line.values, min + 1e-8),
      span = max - min || 1;
    ctx.fillStyle = "#102b44";
    ctx.font = "14px sans-serif";
    ctx.fillText(`${line.label} (${line.unit})`, 8, top + 17);
    ctx.strokeStyle = "#718096";
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(48, top + 25);
    ctx.lineTo(48, top + h - 20);
    ctx.lineTo(w - 12, top + h - 20);
    ctx.stroke();
    ctx.fillText(max.toFixed(2), 2, top + 34);
    ctx.fillText(min.toFixed(2), 2, top + h - 22);
    const duration = times.at(-1) || 1;
    ctx.strokeStyle = line.color;
    ctx.setLineDash(line.dash);
    ctx.beginPath();
    line.values.forEach((value, i) => {
      const x = 48 + ((w - 64) * times[i]) / duration,
        y = top + h - 20 - ((h - 50) * (value - min)) / span;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.setLineDash([2, 3]);
    ctx.strokeStyle = "#102b44";
    ctx.beginPath();
    const x = 48 + ((w - 64) * time) / duration;
    ctx.moveTo(x, top + 25);
    ctx.lineTo(x, top + h - 20);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#102b44";
    ctx.fillText(`${duration.toFixed(2)} s`, w - 70, top + h - 3);
  });
}
