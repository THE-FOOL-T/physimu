import type { AppState } from "./state";
import { $ } from "../../../shell/dom";
import { explanations } from "../solver/explain";
export function renderExplanation(appState: AppState) {
  const list = $("explanations");
  if (
    !appState.net ||
    !appState.solution ||
    !list ||
    list.closest<HTMLElement>("[role=tabpanel]")?.hidden
  )
    return;
  list.replaceChildren(
    ...explanations(appState.net, appState.solution, appState.time).map(
      (text) => {
        const item = document.createElement("li");
        item.textContent = text;
        return item;
      },
    ),
  );
}
