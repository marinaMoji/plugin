/**
 * Pure helpers for jidori → Word `w:fitText` width (twips).
 * Target = N fullwidth cells ≈ N × em; em from Asian/Western font size in pt.
 */

export function countGraphemes(text) {
  if (!text) return 0;
  if (typeof Intl !== "undefined" && Intl.Segmenter) {
    const seg = new Intl.Segmenter(undefined, { granularity: "grapheme" });
    return [...seg.segment(text)].length;
  }
  return [...text].length;
}

/** Points → twips (1 pt = 20 twips). */
export function ptToTwips(pt) {
  return Math.max(0, Math.round(Number(pt) * 20));
}

/**
 * Fit-text width in twips for N cells at fontSizePt.
 * Word caps around 31680 twips (~22").
 */
export function fitTextTwipsForCells(nCells, fontSizePt) {
  const n = Math.max(1, Math.floor(Number(nCells) || 0));
  const pt = Number(fontSizePt) > 0 ? Number(fontSizePt) : 12;
  const twips = ptToTwips(n * pt);
  return Math.min(31680, Math.max(1, twips));
}

export function initialN(graphemeCount, lastN = null) {
  const g = Math.max(1, graphemeCount | 0);
  if (lastN != null && lastN >= 1) return lastN;
  return Math.max(g, 2);
}
