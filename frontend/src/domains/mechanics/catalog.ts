import type { Scene } from "./types";
import { parseScene } from "./validate";

const documents = import.meta.glob("../../../../fixtures/mechanics/*.json", {
  eager: true,
  import: "default",
});
const images = import.meta.glob("../../../../fixtures/mechanics/*.png", {
  eager: true,
  query: "?url",
  import: "default",
});
export const fixtureNames = Object.keys(documents).map((p) =>
  p.split("/").at(-1)!.replace(".json", ""),
);
export function fixture(name: string): { scene: Scene; url: string } {
  const path = `../../../../fixtures/mechanics/${name}`;
  return {
    scene: parseScene(documents[`${path}.json`]),
    url: images[`${path}.png`] as string,
  };
}
