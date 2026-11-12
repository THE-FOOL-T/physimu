import type { DomainModule } from "../../shell";

export const mechanicsDomain: DomainModule = {
  id: "mechanics",
  mount(container, _result, ctx) {
    const panel = document.createElement("main");
    panel.className = "mechanics-placeholder panel";
    panel.dataset.testid = "mechanics-placeholder";
    const title = document.createElement("h1");
    title.dataset.i18n = "mech.title";
    title.textContent = ctx.t("mech.title");
    const message = document.createElement("p");
    message.dataset.i18n = "mech.pending";
    message.textContent = ctx.t("mech.pending");
    const review = document.createElement("p");
    review.className = "small";
    review.dataset.i18n = "mech.review";
    review.textContent = ctx.t("mech.review");
    panel.append(title, message, review);
    container.append(panel);
    return {
      getDocument: () => null,
      unmount: () => panel.remove(),
    };
  },
};
