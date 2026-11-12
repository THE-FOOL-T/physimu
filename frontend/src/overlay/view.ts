export function fitView(
  width: number,
  imageWidth: number,
  imageHeight: number,
  minHeight = 400,
  maxHeight = 720,
  margin = 24,
) {
  width = Math.max(2 * margin + 1, width);
  const height = Math.max(
    minHeight,
    Math.min(maxHeight, (width * imageHeight) / imageWidth + margin * 2),
  );
  const scale = Math.max(
    0.001,
    Math.min(
      (width - 2 * margin) / imageWidth,
      (height - 2 * margin) / imageHeight,
    ),
  );
  return {
    width,
    height,
    scale,
    x: (width - imageWidth * scale) / 2,
    y: (height - imageHeight * scale) / 2,
  };
}
