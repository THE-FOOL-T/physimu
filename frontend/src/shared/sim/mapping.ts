export interface ViewMapping {
  x: number;
  y: number;
  zoom: number;
}
export function nativeToCss(
  point: readonly number[],
  view: ViewMapping,
): [number, number] {
  return [(point[0] + view.x) * view.zoom, (point[1] + view.y) * view.zoom];
}
export function cssToNative(
  point: readonly number[],
  view: ViewMapping,
): [number, number] {
  if (!(view.zoom > 0)) throw new Error("Invalid zoom");
  return [point[0] / view.zoom - view.x, point[1] / view.zoom - view.y];
}
export function canvasDpr(value: number) {
  return Math.max(1, Math.min(2, value || 1));
}
