/**
 * Emphasis marks (圏点・傍点) — semantic style ids for Word.
 *
 * Same ids as LibreOffice where Word has a native match. Word OOXML `w:em`
 * values: none | dot | comma | circle | underDot.
 * LibreOffice BLACK_DOT (filled disc) has no separate Word value — omit here.
 */

export const EMPHASIS_BUILTIN_DEFAULT = "BLACK_SESAME";

export const EMPHASIS_STYLE_IDS = Object.freeze([
  "BLACK_SESAME",
  "WHITE_CIRCLE",
  "DOT",
]);

/** Semantic id → OOXML ST_Em */
const STYLE_TO_EM = Object.freeze({
  BLACK_SESAME: "comma", // sesame / 黒ゴマ
  WHITE_CIRCLE: "circle",
  DOT: "dot",
});

const EM_TO_STYLE = Object.freeze({
  comma: "BLACK_SESAME",
  circle: "WHITE_CIRCLE",
  dot: "DOT",
});

const STYLE_LABELS = Object.freeze({
  BLACK_SESAME: {
    preview: "﹅",
    en: "Black sesame",
    ja: "黒ゴマ",
    fr: "Points sésame noirs",
  },
  WHITE_CIRCLE: {
    preview: "◦",
    en: "Open circle",
    ja: "白丸",
    fr: "Cercle vide",
  },
  DOT: {
    preview: "・",
    en: "Dot",
    ja: "点",
    fr: "Point",
  },
});

const ALIASES = Object.freeze({
  ACCENT: "BLACK_SESAME",
  ACCENT_ABOVE: "BLACK_SESAME",
  SESAME: "BLACK_SESAME",
  COMMA: "BLACK_SESAME",
  CIRCLE: "WHITE_CIRCLE",
  CIRCLE_ABOVE: "WHITE_CIRCLE",
  DOT_ABOVE: "DOT",
  DISK: "DOT", // LO BLACK_DOT → closest Word mark
  DISC: "DOT",
  BLACK_DOT: "DOT",
});

export function normalizeEmphasisStyleId(value) {
  if (value == null) return null;
  const text = String(value).trim();
  if (!text) return null;
  let key = text.toUpperCase().replace(/-/g, "_").replace(/ /g, "_");
  if (ALIASES[key]) key = ALIASES[key];
  if (EMPHASIS_STYLE_IDS.includes(key)) return key;
  return null;
}

export function resolveEmphasisDefault(stored) {
  return normalizeEmphasisStyleId(stored) || EMPHASIS_BUILTIN_DEFAULT;
}

export function styleToEmVal(styleId) {
  const id = normalizeEmphasisStyleId(styleId) || EMPHASIS_BUILTIN_DEFAULT;
  return STYLE_TO_EM[id];
}

export function emValToStyle(emVal) {
  if (emVal == null) return null;
  const key = String(emVal).trim();
  if (!key || key === "none") return null;
  return EM_TO_STYLE[key] || null;
}

export function labelForStyle(styleId, lang = "en") {
  const id = normalizeEmphasisStyleId(styleId);
  const row = id && STYLE_LABELS[id];
  if (!row) return styleId || "";
  const name = lang.startsWith("ja")
    ? row.ja
    : lang.startsWith("fr")
      ? row.fr
      : row.en;
  return `${row.preview}  ${name}`;
}

export function shortName(styleId, lang = "en") {
  const id = normalizeEmphasisStyleId(styleId);
  const row = id && STYLE_LABELS[id];
  if (!row) return styleId || "";
  if (lang.startsWith("ja")) return row.ja;
  if (lang.startsWith("fr")) return row.fr;
  return row.en;
}

export function styleOptions(lang = "en") {
  return EMPHASIS_STYLE_IDS.map((id) => ({
    id,
    label: labelForStyle(id, lang),
  }));
}
