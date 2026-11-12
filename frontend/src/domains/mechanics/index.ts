import type { DomainModule } from "../../shell";
import { MechanicsWorkspace } from "./workspace";

let workspace: MechanicsWorkspace | undefined;
Object.defineProperty(window, "mechanicsWorkspace", {
  get: () => workspace?.inspect(),
});
export const mechanicsDomain: DomainModule = {
  id: "mechanics",
  mount(container) {
    workspace ??= new MechanicsWorkspace();
    return workspace.mount(container);
  },
};
