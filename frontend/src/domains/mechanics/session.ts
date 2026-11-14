import { t, language } from "../../shell";
import type { Scene, BBox } from "./types";
import type { BindingEngine } from "./bindings";
import { emptyScene, SceneHistory, type EditState } from "./authoring";
import { fixture } from "./catalog";
import { readFile, checkImage, parseProject } from "./project";
import {
  MechanicsAnalysis,
  type MechanicsAnalysisOptions,
  type AnalysisProgress,
  type DetectionBox,
  type MechanicsResult,
} from "./analysis";
import { preserveCorrections } from "./reanalysis";
import { el } from "./workspace-dom";
import type { MechanicsUploadPanel } from "./upload-panel";

export interface SessionView {
  analysisStatus: HTMLElement;
  analysisProgress: HTMLProgressElement;
  cancelAnalysis: HTMLButtonElement;
  labelConsent: HTMLInputElement;
  analysisStyle: HTMLSelectElement;
  correctionConsent: HTMLInputElement;
  figureSelect: HTMLSelectElement;
  interpretationSelect: HTMLSelectElement;
  notice: HTMLElement;
  uploadPanel: MechanicsUploadPanel;
  fixtureSelect: HTMLSelectElement;
}
interface SessionHost {
  engine(): BindingEngine | null;
  image(): string;
  active(): boolean;
  version(): number;
  setVersion(n: number): void;
  editing(): boolean;
  setEditing(editing: boolean): void;
  history(): SceneHistory;
  setHistory(history: SceneHistory): void;
  install(
    scene: Scene,
    image: string,
    editing: boolean,
    state?: EditState,
  ): void;
  snapshot(): EditState;
  refresh(): void;
  render(): void;
  report(error: unknown): void;
  number(n: number, places?: number): string;
  resetSource(): void;
}

/** Owns image/project IO and one cancellable analysis generation. It cannot solve
 * physics or mutate source geometry; installation and history remain explicit. */
export class MechanicsSession {
  private analysis = new MechanicsAnalysis();
  private analysisEpoch = 0;
  analyzing = false;
  private file?: File;
  analysisBoxes: DetectionBox[] = [];
  figureRegions: BBox[] = [];
  interpretations: NonNullable<
    NonNullable<MechanicsResult["diagnostics"]>["alternatives"]
  > = [];
  constructor(
    private host: SessionHost,
    private view: SessionView,
  ) {}
  private get engine() {
    return this.host.engine();
  }
  private get image() {
    return this.host.image();
  }
  private get active() {
    return this.host.active();
  }
  private get generation() {
    return this.host.version();
  }
  private set generation(n: number) {
    this.host.setVersion(n);
  }
  private get editing() {
    return this.host.editing();
  }
  private set editing(value: boolean) {
    this.host.setEditing(value);
  }
  private get history() {
    return this.host.history();
  }
  private set history(value: SceneHistory) {
    this.host.setHistory(value);
  }
  private install(
    s: Scene,
    image: string,
    editing: boolean,
    state?: EditState,
  ) {
    this.host.install(s, image, editing, state);
  }
  private snapshot() {
    return this.host.snapshot();
  }
  private refresh() {
    this.host.refresh();
  }
  private render() {
    this.host.render();
  }
  private report(error: unknown) {
    this.host.report(error);
  }
  cancel() {
    const wasAnalyzing = this.analyzing;
    this.analysisEpoch++;
    this.analysis.cancel();
    this.analyzing = false;
    this.analysisBoxes = [];
    this.view.analysisProgress.hidden = true;
    this.view.cancelAnalysis.hidden = true;
    this.view.analysisStatus.textContent = "";
    if (wasAnalyzing) this.view.uploadPanel.failed();
  }
  confirmCandidate(index: number) {
    if (this.file) return this.analyze(this.file, false, index);
  }
  private async analyze(file: File, preserve = false, candidate?: number) {
    this.cancel();
    const previous = preserve ? this.engine : null;
    const analysisOptions: MechanicsAnalysisOptions = {
      pendulumCandidate: candidate,
      style: this.view.analysisStyle.value as MechanicsAnalysisOptions["style"],
      useLabelReader: this.view.labelConsent.checked,
      figureRegion:
        preserve && this.view.figureSelect.value !== "auto"
          ? this.figureRegions[Number(this.view.figureSelect.value)]
          : undefined,
    };
    this.view.labelConsent.checked = false;
    const epoch = this.analysisEpoch;
    this.analyzing = true;
    this.view.uploadPanel.start(preserve);
    this.view.analysisProgress.value = 0;
    this.view.analysisProgress.hidden = false;
    this.view.cancelAnalysis.hidden = false;
    this.view.analysisStatus.textContent = t("mech.stage_queued");
    try {
      let canonicalImage = "";
      const result = await this.analysis.start(
        file,
        language,
        async (job: AnalysisProgress) => {
          if (epoch !== this.analysisEpoch || !this.active) return;
          const p = job.partial;
          if (
            p?.source_image &&
            p.width &&
            p.height &&
            canonicalImage !== p.source_image
          ) {
            await checkImage(p.source_image, p.width, p.height);
            if (epoch !== this.analysisEpoch || !this.active) return;
            canonicalImage = p.source_image;
            if (!preserve)
              this.install(
                emptyScene({
                  path: file.name,
                  width: p.width,
                  height: p.height,
                }),
                canonicalImage,
                false,
              );
            void this.view.uploadPanel.source(
              canonicalImage,
              p.width,
              p.height,
              file,
            );
          }
          this.view.analysisProgress.value = job.percent;
          this.view.uploadPanel.progress(job);
          const text = (p?.texts ?? [])
            .slice(0, 12)
            .map((r) => r.text)
            .join(" · ");
          this.view.analysisStatus.textContent = `${t(`mech.stage_${job.stage}`)} · ${this.host.number(job.percent, 0)}% · ${this.host.number(job.elapsed_seconds)} s${text ? ` · ${text}` : ""}`;
          if (job.partial?.detections)
            this.analysisBoxes = job.partial.detections.filter(
              (d) =>
                Array.isArray(d.bbox) &&
                d.bbox.length === 4 &&
                d.bbox.every(Number.isFinite),
            );
          this.render();
        },
        analysisOptions,
      );
      if (!result || epoch !== this.analysisEpoch || !this.active) return;
      await checkImage(
        result.source_image,
        result.scene.image.width,
        result.scene.image.height,
      );
      if (epoch !== this.analysisEpoch || !this.active) return;
      this.analyzing = false;
      this.analysisBoxes = [];
      this.view.uploadPanel.compiled(result);
      void this.view.uploadPanel.source(
        result.source_image,
        result.scene.image.width,
        result.scene.image.height,
        file,
      );
      const authored = previous?.original.meta.provenance === "authored";
      const savedHistory = this.history,
        before = previous ? this.snapshot() : null;
      const merged =
        previous && !authored
          ? preserveCorrections(previous.document, result.scene)
          : null;
      this.install(
        authored ? previous!.original : (merged?.scene ?? result.scene),
        result.source_image,
        authored
          ? this.editing
          : result.scene.archetype === "unsupported" ||
              result.provenance === "unsupported",
        authored
          ? {
              scene: previous!.original,
              overrides: previous!.params,
              unlocked: [...previous!.unlocked],
              recognition: previous!.recognition,
            }
          : previous && merged
            ? {
                scene: merged.scene,
                overrides: merged.overrides,
                unlocked: [],
                recognition: previous.recognition,
              }
            : undefined,
      );
      if (before) {
        this.history = savedHistory;
        this.history.push(before, this.snapshot());
        this.refresh();
      }
      this.figureRegions =
        result.diagnostics?.figure_regions?.filter(
          (r) => r.length === 4 && r.every(Number.isFinite),
        ) ?? [];
      this.view.figureSelect.replaceChildren();
      for (const [i, region] of this.figureRegions.entries()) {
        const option = el("option", this.view.figureSelect);
        option.value = String(i);
        option.textContent = `${t("mech.figure_region")} ${i + 1}`;
        if (JSON.stringify(region) === JSON.stringify(result.scene.meta.region))
          option.selected = true;
      }
      this.view.figureSelect.parentElement!.hidden =
        this.figureRegions.length <= 1;
      const seen = new Set<string>();
      this.interpretations = (result.diagnostics?.alternatives ?? []).filter(
        (candidate) => {
          const key = JSON.stringify([
            candidate.archetype,
            candidate.surfaces,
            candidate.attachments,
          ]);
          if (
            candidate.archetype === "unsupported" ||
            candidate.violations.length ||
            seen.has(key)
          )
            return false;
          seen.add(key);
          return true;
        },
      );
      this.view.interpretationSelect.replaceChildren();
      for (const [i, candidate] of this.interpretations.entries()) {
        const option = el("option", this.view.interpretationSelect);
        option.value = String(i);
        option.textContent = `${t(`mech.${candidate.archetype}`)} · ${i + 1}`;
      }
      this.view.interpretationSelect.parentElement!.hidden =
        this.interpretations.length <= 1;
      this.view.analysisStatus.textContent = t("mech.analysis_compiled");
      this.view.notice.textContent = t(
        result.diagnostics?.recognition?.method.includes("classical")
          ? "mech.classical_method"
          : result.warnings.some((w) => w.code === "weights_unavailable")
            ? "mech.weights_unavailable"
            : result.provenance === "unsupported"
              ? "mech.unsupported_analysis"
              : result.provenance === "partial"
                ? "mech.partial_analysis"
                : "mech.extracted_analysis",
      );
      if (authored)
        this.view.notice.textContent += ` ${t("mech.authored_reanalysis_retained")}`;
    } catch (error) {
      if (epoch === this.analysisEpoch && this.active) {
        this.report(error);
        this.editing = true;
        this.view.uploadPanel.failed();
      }
    } finally {
      if (epoch === this.analysisEpoch) {
        this.analyzing = false;
        this.view.analysisProgress.hidden = true;
        this.view.cancelAnalysis.hidden = true;
        this.refresh();
      }
    }
  }
  async reanalyze() {
    if (!this.engine || this.analyzing) return;
    const generation = this.generation,
      image = this.image;
    const data = await (await fetch(this.image)).blob();
    if (!this.active || generation !== this.generation || image !== this.image)
      return;
    await this.analyze(
      new File([data], "mechanics-reanalysis.png", { type: data.type }),
      true,
    );
  }
  async saveCorrection() {
    if (!this.view.correctionConsent.checked || !this.engine) {
      this.view.notice.textContent = t("mech.correction_opt_in");
      return;
    }
    const epoch = this.generation;
    try {
      const form = new FormData();
      form.append(
        "image",
        new File(
          [await (await fetch(this.image)).blob()],
          "mechanics-correction.png",
          { type: "image/png" },
        ),
      );
      form.append("domain", "mechanics");
      form.append("scene", JSON.stringify(this.engine.document));
      form.append("opt_in", "true");
      const response = await fetch("/api/corrections", {
        method: "POST",
        body: form,
      });
      if (!response.ok) throw new Error("mech.correction_failed");
      if (epoch === this.generation && this.active) {
        this.view.notice.textContent = t("mech.correction_saved");
        this.view.correctionConsent.checked = false;
      }
    } catch (error) {
      if (epoch === this.generation && this.active) this.report(error);
    }
  }
  async upload(file: File) {
    this.clearChoices();
    this.cancel();
    const token = ++this.generation;
    this.file = file;
    this.view.fixtureSelect.value = "choose_fixture";
    const epoch = this.analysisEpoch;
    this.analyzing = true;
    this.view.uploadPanel.reset("upload", file.name, file);
    this.host.resetSource();
    try {
      if (!["image/png", "image/jpeg", "image/webp"].includes(file.type))
        throw new Error("mech.invalid_image");
      const data = await readFile(file),
        img = await checkImage(data);
      if (token !== this.generation || epoch !== this.analysisEpoch) return;
      this.install(
        emptyScene({
          path: file.name,
          width: img.naturalWidth,
          height: img.naturalHeight,
        }),
        data,
        false,
      );
      void this.view.uploadPanel.source(
        data,
        img.naturalWidth,
        img.naturalHeight,
        file,
      );
      void this.analyze(file);
    } catch (e) {
      if (token === this.generation) {
        this.analyzing = false;
        this.view.uploadPanel.failed();
        this.report(e);
      }
    }
  }
  async import(file: File) {
    this.clearChoices();
    this.cancel();
    const token = ++this.generation;
    try {
      if (file.size > 44000000) throw new Error("mech.image_size");
      const p = parseProject(JSON.parse(await file.text()));
      await checkImage(
        p.source_image,
        p.scene.image.width,
        p.scene.image.height,
      );
      if (token !== this.generation) return;
      this.view.fixtureSelect.value = "choose_fixture";
      this.file = undefined;
      this.view.uploadPanel.reset("project", file.name);
      void this.view.uploadPanel.source(
        p.source_image,
        p.scene.image.width,
        p.scene.image.height,
      );
      this.install(p.scene, p.source_image, false, {
        scene: p.scene,
        overrides: p.parameter_overrides,
        unlocked: p.unlocked_geometry,
        recognition: p.recognition_scene,
      });
      this.view.notice.textContent = t("mech.import_valid");
    } catch (e) {
      if (token === this.generation) this.report(e);
    }
  }
  async loadFixture(name: string) {
    this.clearChoices();
    this.cancel();
    const token = ++this.generation;
    try {
      const f = fixture(name),
        res = await fetch(f.url),
        data = await readFile(
          new File([await res.blob()], `${name}.png`, { type: "image/png" }),
        );
      if (token !== this.generation) return;
      this.view.uploadPanel.reset("sample", name);
      this.file = undefined;
      this.view.fixtureSelect.value = name;
      void this.view.uploadPanel.source(
        data,
        f.scene.image.width,
        f.scene.image.height,
      );
      this.install(f.scene, data, false);
    } catch (e) {
      if (token === this.generation) this.report(e);
    }
  }
  async retry() {
    if (this.file) await this.upload(this.file);
    else await this.reanalyze();
  }
  private clearChoices() {
    this.figureRegions = [];
    this.interpretations = [];
    this.view.figureSelect.parentElement!.hidden = true;
    this.view.interpretationSelect.parentElement!.hidden = true;
  }
}
