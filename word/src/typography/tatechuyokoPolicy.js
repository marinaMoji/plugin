/**
 * Selection policy for tate-chū-yoko (ported from LibreOffice tatechuyoko.py).
 * Pure logic — no Word API.
 */

export const OK = "ok";
export const CONFIRM = "confirm";
export const REFUSE = "refuse";

function isVs(ch) {
  const o = ch.codePointAt(0);
  return (0xfe00 <= o && o <= 0xfe0f) || (0xe0100 <= o && o <= 0xe01ef);
}

function graphemeList(text) {
  if (typeof Intl !== "undefined" && Intl.Segmenter) {
    const seg = new Intl.Segmenter(undefined, { granularity: "grapheme" });
    return [...seg.segment(text || "")].map((s) => s.segment);
  }
  // Fallback: code points (good enough for ASCII digits / Latin).
  return [...(text || "")];
}

function isDigitGrapheme(g) {
  if (!g) return false;
  const ch = g[0];
  const o = ch.codePointAt(0);
  return (ch >= "0" && ch <= "9") || (0xff10 <= o && o <= 0xff19);
}

function isLatinGrapheme(g) {
  if (!g) return false;
  const ch = g[0];
  const o = ch.codePointAt(0);
  if ((ch >= "A" && ch <= "Z") || (ch >= "a" && ch <= "z")) return true;
  if ((0xff21 <= o && o <= 0xff3a) || (0xff41 <= o && o <= 0xff5a)) return true;
  return false;
}

function isNumericExtra(g) {
  return g === "." || g === "%" || g === "," || g === "．" || g === "％" || g === "，";
}

function isCjkLetterGrapheme(g) {
  if (!g) return false;
  const o = g.codePointAt(0);
  if (0x3040 <= o && o <= 0x309f) return true;
  if (0x30a0 <= o && o <= 0x30ff) return true;
  if (0x3400 <= o && o <= 0x9fff) return true;
  if (0xf900 <= o && o <= 0xfaff) return true;
  return false;
}

export function classifyRun(text) {
  const raw = text || "";
  if (raw.includes("\n") || raw.includes("\r")) {
    return { kind: "unsafe", length: graphemeList(raw).length };
  }
  const clusters = graphemeList(raw);
  const n = clusters.length;
  if (n === 0) return { kind: "empty", length: 0 };
  if (clusters.some(isCjkLetterGrapheme)) return { kind: "japanese", length: n };
  if (clusters.every(isDigitGrapheme)) return { kind: "digits", length: n };
  if (clusters.every(isLatinGrapheme)) return { kind: "latin", length: n };
  if (clusters.every((g) => isDigitGrapheme(g) || isLatinGrapheme(g))) {
    return { kind: "alnum", length: n };
  }
  if (
    clusters.every(
      (g) => isDigitGrapheme(g) || isLatinGrapheme(g) || isNumericExtra(g)
    )
  ) {
    if (clusters.some(isDigitGrapheme)) return { kind: "numeric", length: n };
    return { kind: "mixed", length: n };
  }
  return { kind: "other", length: n };
}

function verdict(v, reasonKey, kind, length, messageEn) {
  return {
    verdict: v,
    reason_key: reasonKey,
    kind,
    length,
    message_en: messageEn,
  };
}

/** marinaMoji policy for an explicit selection. */
export function classifySelection(text) {
  const { kind, length: n } = classifyRun(text);
  if (kind === "empty") {
    return verdict(
      REFUSE,
      "empty",
      kind,
      n,
      "Select a short number or letter sequence for tate-chū-yoko."
    );
  }
  if (kind === "unsafe") {
    return verdict(
      REFUSE,
      "unsafe",
      kind,
      n,
      "This selection crosses a line or paragraph break."
    );
  }
  if (kind === "japanese") {
    return verdict(
      REFUSE,
      "japanese",
      kind,
      n,
      "Tate-chū-yoko is for short digits or letters in vertical text " +
        "(for example `12` in `令和12年`), not the surrounding Japanese."
    );
  }
  if (kind === "other" || kind === "mixed") {
    return verdict(
      REFUSE,
      "inappropriate",
      kind,
      n,
      "Tate-chū-yoko is for short horizontal digit or letter sequences."
    );
  }
  if (n === 1) {
    return verdict(
      REFUSE,
      "too_short",
      kind,
      n,
      "A single character is not conventional tate-chū-yoko. Select two digits or letters."
    );
  }
  if (n === 2 && (kind === "digits" || kind === "latin" || kind === "alnum")) {
    return verdict(OK, "recommended", kind, n, "");
  }
  if (
    n >= 3 &&
    n <= 4 &&
    (kind === "digits" ||
      kind === "latin" ||
      kind === "alnum" ||
      kind === "numeric")
  ) {
    return verdict(
      CONFIRM,
      "extended",
      kind,
      n,
      "This selection is longer than a conventional two-character tate-chū-yoko. " +
        "Characters may look compressed. Apply anyway?"
    );
  }
  if (n >= 5) {
    return verdict(
      REFUSE,
      "too_long",
      kind,
      n,
      "This selection is too long for conventional tate-chū-yoko."
    );
  }
  return verdict(
    REFUSE,
    "inappropriate",
    kind,
    n,
    "Tate-chū-yoko is for short horizontal digit or letter sequences."
  );
}

/** Pure helper reused by warichū. */
export function selectionCoversWholeParagraphText(selText, paraText) {
  if (!selText || !paraText) return false;
  if (selText === paraText) return true;
  const selS = String(selText).replace(/^[\r\n]+|[\r\n]+$/g, "");
  const paraS = String(paraText).replace(/^[\r\n]+|[\r\n]+$/g, "");
  return Boolean(selS) && selS === paraS;
}

// silence unused in some bundlers
void isVs;
