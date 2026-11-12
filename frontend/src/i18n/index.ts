import en from "./en.json";
import bn from "./bn.json";
import { stored, store } from "../ui/storage";
export let language: "en" | "bn" = (
  stored("circuit-language") ||
  (typeof navigator !== "undefined" ? navigator.language : "en")
).startsWith("bn")
  ? "bn"
  : "en";
export let banglaDigits = stored("circuit-digits") === "true";
export function setLanguage(lang: "en" | "bn") {
  language = lang;
  store("circuit-language", lang);
  document.documentElement.lang = lang;
}
export function setDigits(value: boolean) {
  banglaDigits = value;
  store("circuit-digits", String(value));
}
export function t(key: string, params: Record<string, string> = {}) {
  let value = (language === "bn" ? bn : en)[key as keyof typeof en] || key;
  for (const [k, v] of Object.entries(params))
    value = value.replaceAll("{" + k + "}", v);
  return value;
}
export function digits(value: string) {
  return banglaDigits
    ? value.replace(/\d/g, (d) => "০১২৩৪৫৬৭৮৯"[Number(d)])
    : value;
}
export function format(value: number, unit = "") {
  if (!Number.isFinite(value)) return "—";
  const a = Math.abs(value),
    prefix =
      a !== 0 && a < 1e-6
        ? ["n", 1e9]
        : a !== 0 && a < 0.001
          ? ["µ", 1e6]
          : a !== 0 && a < 1
            ? ["m", 1e3]
            : a >= 1e6
              ? ["M", 1e-6]
              : a >= 1e3
                ? ["k", 1e-3]
                : ["", 1];
  return digits(
    `${Number((value * Number(prefix[1])).toPrecision(4))} ${prefix[0]}${unit}`,
  );
}
