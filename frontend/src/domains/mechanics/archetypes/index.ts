import type { ArchetypeModule, ArchetypeId } from "../types";
import { projectile } from "./projectile";
import { inclineBlock } from "./incline_block";
import { pendulum } from "./pendulum";
import { springMass } from "./spring_mass";
import { atwood } from "./atwood";
import { tablePulley } from "./table_pulley";
import { inclinePulley } from "./incline_pulley";
import { collision1d } from "./collision_1d";
import { unsupported } from "./common";
import { layout } from "../layout";

export const archetypes: Record<ArchetypeId, ArchetypeModule> =
  Object.fromEntries(
    [
      projectile,
      inclineBlock,
      pendulum,
      springMass,
      atwood,
      tablePulley,
      inclinePulley,
      collision1d,
    ].map((module) => [module.id, module]),
  ) as Record<ArchetypeId, ArchetypeModule>;
archetypes.unsupported = {
  id: "unsupported",
  defaultBindings: (s) => s.bindings,
  layout,
  solve: () => unsupported("unsupported_archetype"),
  forces: () => [],
  regime: () => ({
    code: "unsupported",
    message: "This scene is unsupported.",
    warnings: [],
  }),
};
