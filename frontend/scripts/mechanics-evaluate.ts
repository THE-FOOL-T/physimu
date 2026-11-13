import { readFileSync } from "node:fs";
import { parseScene } from "../src/domains/mechanics/validate";
import { compareTrajectories } from "../src/domains/mechanics/evaluation";
const rows = JSON.parse(readFileSync(0, "utf8"));
if (!Array.isArray(rows)) throw new Error("Expected evaluation pairs");
process.stdout.write(
  JSON.stringify(
    rows.map((row) =>
      compareTrajectories(
        parseScene(row.prediction),
        parseScene(row.gold),
        row.body_map,
      ),
    ),
  ),
);
