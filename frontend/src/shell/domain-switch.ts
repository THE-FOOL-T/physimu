import { get, names, type DomainHandle, type DomainId } from "../domains";
import type { ShellContext } from ".";
import "./domains.css";

export function mountDomainSwitch(
  topbar: HTMLElement,
  container: HTMLElement,
  ctx: ShellContext,
) {
  const label = document.createElement("label");
  label.className = "domain-switch";
  const caption = document.createElement("span");
  caption.dataset.i18n = "mech.domain";
  caption.textContent = ctx.t("mech.domain");
  const selector = document.createElement("select");
  selector.id = "domain";
  selector.dataset.testid = "domain-switch";
  for (const id of names()) {
    const option = document.createElement("option");
    option.value = id;
    option.dataset.i18n = "mech.domain_" + id;
    option.textContent = ctx.t(option.dataset.i18n);
    selector.append(option);
  }
  label.append(caption, selector);
  topbar.prepend(label);
  let active: DomainId = "circuit";
  let handle: DomainHandle = get(active).mount(container, undefined, ctx);
  selector.value = active;
  container.dataset.domain = active;
  selector.onchange = () => {
    if (selector.value === active) return;
    const next = get(selector.value);
    handle.unmount();
    active = next.id;
    handle = next.mount(container, undefined, ctx);
    container.dataset.domain = active;
  };
  return {
    getDocument: () => handle.getDocument(),
    unmount() {
      handle.unmount();
      label.remove();
    },
  };
}
