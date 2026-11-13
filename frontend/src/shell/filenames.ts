import { t } from "./language";

export function friendlyFilename(filename: string): string {
  const base = filename
    .split(/[\\/]/)
    .at(-1)!
    .replace(/\.[a-z0-9]{1,6}$/i, "");
  const clean = base
    .replace(/(?:^|[ _-])[a-f0-9]{16,}(?=$|[ _-])/gi, " ")
    .replace(/\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b/gi, "")
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return clean && !/^[a-f0-9 _-]{24,}$/i.test(clean)
    ? clean
    : t("layout.uploaded");
}
