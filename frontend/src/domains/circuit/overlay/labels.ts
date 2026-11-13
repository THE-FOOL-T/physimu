export type Rect = [number, number, number, number];
export function overlap(a: Rect, b: Rect) {
  return a[0] < b[2] && a[2] > b[0] && a[1] < b[3] && a[3] > b[1];
}
/** Nudge along the lead normal, preferring collision-free, in-bounds labels. */
export function placeBadge(
  rect: Rect,
  normal: [number, number],
  obstacles: Rect[],
  width: number,
  height: number,
): Rect {
  let best = rect,
    bestScore = Infinity;
  for (const shift of [0, 16, -16, 32, -32, 48, -48, 64, -64, 80, -80]) {
    const w = rect[2] - rect[0],
      h = rect[3] - rect[1];
    const x = Math.max(1, Math.min(width - w - 1, rect[0] + normal[0] * shift));
    const y = Math.max(
      1,
      Math.min(height - h - 1, rect[1] + normal[1] * shift),
    );
    const candidate: Rect = [x, y, x + w, y + h];
    const score =
      obstacles.filter((o) => overlap(candidate, o)).length * 1000 +
      Math.abs(shift);
    if (score < bestScore) {
      best = candidate;
      bestScore = score;
    }
  }
  return best;
}

/** Try all four sides before accepting overlap; reserve a small paper margin. */
export function placePartBadge(
  body: Rect,
  sizes: [number, number][],
  obstacles: Rect[],
  width: number,
  height: number,
): { rect: Rect; compact: boolean } {
  let best: { rect: Rect; compact: boolean } = { rect: body, compact: false },
    score = Infinity;
  for (const [index, [w, h]] of sizes.entries())
    for (const gap of [9, 25, 41, 65]) {
      const cx = (body[0] + body[2]) / 2,
        cy = (body[1] + body[3]) / 2;
      const horizontal = body[2] - body[0] >= body[3] - body[1];
      const sides: [
        [number, number],
        [number, number],
        [number, number],
        [number, number],
      ] = [
        [cx - w / 2, body[3] + gap],
        [body[2] + gap, cy - h / 2],
        [cx - w / 2, body[1] - gap - h],
        [body[0] - gap - w, cy - h / 2],
      ];
      if (!horizontal) sides.push(sides.shift()!);
      for (const [side, [rawX, rawY]] of sides.entries()) {
        const x = Math.max(-12, Math.min(width + 12 - w, rawX)),
          y = Math.max(-12, Math.min(height + 12 - h, rawY));
        const rect: Rect = [x, y, x + w, y + h],
          hits = obstacles.filter((o) => overlap(rect, o)).length;
        const cost = hits * 10000 + index * 200 + gap + side;
        if (cost < score) {
          best = { rect, compact: index > 0 };
          score = cost;
        }
        if (!hits) return { rect, compact: index > 0 };
      }
    }
  return best;
}
