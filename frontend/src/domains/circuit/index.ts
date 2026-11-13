import type { DomainModule } from "../index";

interface CircuitWorkspace {
  elements: HTMLElement[];
  setActive(active: boolean): void;
  getDocument(): unknown;
}

// Retain the existing document, image URLs, handlers and edit history on switch.
export function createCircuitDomain(workspace: CircuitWorkspace): DomainModule {
  let saved: { element: HTMLElement; hidden: boolean; inert: boolean }[] = [];
  return {
    id: "circuit",
    mount() {
      for (const { element, hidden, inert } of saved) {
        element.hidden = hidden;
        element.inert = inert;
      }
      saved = [];
      workspace.setActive(true);
      let mounted = true;
      return {
        getDocument: () => workspace.getDocument(),
        unmount() {
          if (!mounted) return;
          mounted = false;
          workspace.setActive(false);
          saved = workspace.elements.map((element) => ({
            element,
            hidden: element.hidden,
            inert: element.inert,
          }));
          for (const { element } of saved) {
            element.hidden = true;
            element.inert = true;
          }
        },
      };
    },
  };
}
