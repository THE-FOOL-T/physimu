export const SIM_DT = 1 / 240;
export class SimulationClock {
  time = 0;
  accumulator = 0;
  playing = false;
  speed = 1;
  private previous: number | null = null;
  constructor(public duration = 0) {}
  get displayTime() {
    return Math.min(this.duration, this.time + this.accumulator);
  }
  get alpha() {
    return this.accumulator / SIM_DT;
  }
  setSpeed(speed: number) {
    if (!Number.isFinite(speed) || speed < 0.25 || speed > 4)
      throw new Error("Speed must be 0.25–4");
    this.speed = speed;
  }
  play() {
    if (this.displayTime >= this.duration) this.seek(0);
    this.playing = true;
    this.previous = null;
  }
  pause() {
    this.playing = false;
    this.previous = null;
  }
  seek(time: number) {
    if (!Number.isFinite(time)) throw new Error("Invalid time");
    const t = Math.max(0, Math.min(time, this.duration));
    this.time = Math.floor(t / SIM_DT) * SIM_DT;
    this.accumulator = t - this.time;
    this.previous = null;
  }
  reset() {
    this.pause();
    this.seek(0);
  }
  step() {
    this.pause();
    this.seek(this.displayTime + SIM_DT);
  }
  tick(timestampMs: number) {
    if (!this.playing) {
      this.previous = null;
      return this.displayTime;
    }
    if (this.previous === null) {
      this.previous = timestampMs;
      return this.displayTime;
    }
    const elapsed = Math.max(
      0,
      Math.min(0.1, (timestampMs - this.previous) / 1000),
    );
    this.previous = timestampMs;
    this.accumulator += elapsed * this.speed;
    while (this.accumulator + 1e-12 >= SIM_DT) {
      this.time += SIM_DT;
      this.accumulator -= SIM_DT;
    }
    this.accumulator = Math.max(0, this.accumulator);
    if (this.displayTime >= this.duration) {
      this.seek(this.duration);
      this.pause();
    }
    return this.displayTime;
  }
}
/** Right-hand sample at discontinuities. Interpolation is never allowed to cross an event. */
export function bracket(
  times: readonly number[],
  time: number,
  events: readonly number[] = [],
) {
  let low = 0,
    high = times.length - 1;
  while (low < high) {
    const mid = Math.ceil((low + high) / 2);
    if (times[mid] <= time) low = mid;
    else high = mid - 1;
  }
  const a = low,
    b = Math.min(a + 1, times.length - 1);
  const width = times[b] - times[a];
  const event = events.find((e) => e > times[a] && e <= times[b]);
  return {
    a,
    b: event !== undefined && time < event ? a : b,
    alpha: width > 0 ? Math.max(0, Math.min(1, (time - times[a]) / width)) : 0,
  };
}
