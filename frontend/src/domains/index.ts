import type { ShellContext } from "../shell/index";

export type DomainId = "circuit" | "mechanics";
export interface DomainHandle {
  unmount(): void;
  getDocument(): unknown;
}
export interface DomainModule {
  id: DomainId;
  mount(
    container: HTMLElement,
    result: unknown,
    ctx: ShellContext,
  ): DomainHandle;
}

export function createRegistry() {
  const modules = new Map<DomainId, DomainModule>();
  return {
    register(module: DomainModule) {
      if (modules.has(module.id)) throw Error(`Duplicate domain: ${module.id}`);
      modules.set(module.id, module);
    },
    get(id: string): DomainModule {
      const module = modules.get(id as DomainId);
      if (!module) throw Error(`Unknown domain: ${id}`);
      return module;
    },
    names(): DomainId[] {
      return [...modules.keys()];
    },
  };
}

export const { register, get, names } = createRegistry();
