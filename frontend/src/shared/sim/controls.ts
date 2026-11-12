export interface TransportActions {
  play(): void;
  pause(): void;
  reset(): void;
  step(): void;
  seek(t: number): void;
  speed(v: number): void;
  toggle(key: string, value: boolean): void;
}
export function simulationControls(
  container: HTMLElement,
  actions: TransportActions,
) {
  const buttons: HTMLButtonElement[] = [];
  for (const key of ["Play", "Pause", "Reset", "Step"] as const) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = key;
    button.dataset.action = key.toLowerCase();
    button.addEventListener("click", () =>
      actions[key.toLowerCase() as "play"](),
    );
    container.append(button);
    buttons.push(button);
  }
  const speedLabel = document.createElement("label");
  speedLabel.textContent = "Speed ";
  const speed = document.createElement("select");
  speed.setAttribute("aria-label", "Speed");
  for (const n of [0.25, 0.5, 1, 2, 4]) {
    const option = new Option(`${n}×`, String(n));
    option.selected = n === 1;
    speed.add(option);
  }
  speed.addEventListener("change", () => actions.speed(Number(speed.value)));
  speedLabel.append(speed);
  container.append(speedLabel);
  const scrubLabel = document.createElement("label");
  scrubLabel.textContent = "Time ";
  const scrub = document.createElement("input");
  scrub.type = "range";
  scrub.min = "0";
  // Terminal contact times need not be multiples of the integration timestep.
  scrub.step = "any";
  scrub.value = "0";
  scrub.setAttribute("aria-label", "Time");
  scrub.addEventListener("input", () => actions.seek(Number(scrub.value)));
  const output = document.createElement("output");
  scrubLabel.append(scrub, output);
  container.append(scrubLabel);
  for (const [key, title, checked] of [
    ["forces", "Forces", true],
    ["components", "Components", false],
    ["trail", "Trail / predicted path", true],
    ["graphs", "Graphs", true],
    ["original", "Original image", false],
    ["marker", "Pulley rotation marker", false],
  ] as const) {
    const label = document.createElement("label"),
      input = document.createElement("input");
    input.type = "checkbox";
    input.checked = checked;
    input.dataset.toggle = key;
    input.addEventListener("change", () => actions.toggle(key, input.checked));
    label.append(input, document.createTextNode(title));
    container.append(label);
  }
  return {
    update(time: number, duration: number, playing: boolean) {
      scrub.max = String(duration);
      scrub.value = String(time);
      output.value = `${time.toFixed(3)} / ${duration.toFixed(3)} s`;
      buttons[0].disabled = playing || duration <= 0;
      buttons[1].disabled = !playing;
    },
  };
}
