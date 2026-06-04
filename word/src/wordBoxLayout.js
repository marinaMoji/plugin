/**
 * Shared sizing for inline kaeriten boxes (OOXML + insertTextBox).
 * Mirrors LibreOffice: width and spacing scale with host (surrounding) font size.
 */

const PT_PER_MM = 72 / 25.4;

/** LO Width/Height use 1/100 mm (same as mapping frame_width_hmm). */
export function hmmToPt(hmm) {
  return (hmm / 100) * PT_PER_MM;
}

/** Parse mapping ratio: number, or "12:5" (host:mark → mark/host). */
export function parseFontSizeRatio(value) {
  if (value == null || value === "") return 5 / 12;
  if (typeof value === "string" && value.includes(":")) {
    const parts = value.split(":").map((s) => Number(s.trim()));
    if (parts.length === 2 && parts[0] > 0 && parts[1] > 0) {
      return parts[1] / parts[0];
    }
  }
  const n = Number(value);
  return Number.isFinite(n) && n > 0 ? n : 5 / 12;
}

export function hostReferencePt(opts) {
  return Number(opts?.frameWidthReferencePt ?? opts?.hostReferencePt ?? 12);
}

/** LO effective_frame_width_hmm: max(80, frame_width_hmm * host / 12). */
export function effectiveFrameWidthHmm(hostPt, opts) {
  const ref = hostReferencePt(opts);
  const host = hostPt > 0 ? hostPt : ref;
  const base = Number(opts?.frameWidthHmm ?? 180);
  return Math.max(80, Math.round((base * host) / ref));
}

/** Extra inline width (pt) after marks; scales with host (reference 12 pt). */
export function boxExtraWidthRightPt(hostPt, opts) {
  const v = opts?.boxExtraWidthRightPt;
  if (v == null || v === "" || Number(v) <= 0) return 0;
  return scaleWithHost(Number(v), hostPt, opts);
}

/** Box width in pt from host kanji size (optional fixed overrides). */
export function effectiveFrameWidthPt(hostPt, opts) {
  let w;
  if (opts?.boxWidthPt != null && opts.boxWidthPt > 0) {
    w = Number(opts.boxWidthPt);
  } else if (opts?.boxWidthEm != null && opts.boxWidthEm > 0) {
    const fontPt = markFontPt(hostPt, opts);
    w = Math.max(4, Math.ceil(fontPt * opts.boxWidthEm));
  } else {
    w = hmmToPt(effectiveFrameWidthHmm(hostPt, opts));
  }
  return w + boxExtraWidthRightPt(hostPt, opts);
}

/** Scale a pt value designed at hostReferencePt (e.g. 4 pt gap at 12 pt host). */
export function scaleWithHost(valuePt, hostPt, opts) {
  const ref = hostReferencePt(opts);
  const host = hostPt > 0 ? hostPt : ref;
  return (Number(valuePt) * host) / ref;
}

/** Host font pt → mark font pt (LO char_height_from_host). */
export function markFontPt(hostPt, opts) {
  const ratio = opts?.fontSizeRatio ?? 5 / 12;
  const minPt = opts?.minFontSizePt ?? 6;
  const maxPt = Number(opts?.maxFontSizePt ?? 72);
  if (!hostPt || hostPt <= 0) {
    return Math.max(minPt, Number(opts?.fontSizePt ?? minPt));
  }
  return Math.max(minPt, Math.min(maxPt, hostPt * ratio));
}

/** Line spacing between stacked marks (pt), scaled with host when fixed in mapping. */
export function compoundLineSpacingPt(fontPt, hostPt, opts) {
  const fixed = opts?.compoundLineSpacingPt;
  if (fixed != null && fixed !== "" && Number(fixed) > 0) {
    return scaleWithHost(Number(fixed), hostPt, opts);
  }
  const mult = Number(opts?.compoundLineSpacingMultiple ?? 0.82);
  return Math.max(4, fontPt * mult);
}

/** LO _frame_min_height_hmm: per_line = char_pt * 42, + 80 hmm padding. */
export function loStyleBoxHeightHmm(fontPt, glyphCount, opts) {
  const perLine = Math.round(fontPt * 42);
  const pad = Number(opts?.frameHeightPaddingHmm ?? 80);
  return perLine * Math.max(1, glyphCount) + pad;
}

/** Inline box height (pt) from host + mark metrics. */
export function compoundBoxHeightPt(hostPt, fontPt, glyphCount, opts) {
  const host = hostPt > 0 ? hostPt : hostReferencePt(opts);
  if (glyphCount <= 1) {
    const padPt = hmmToPt(40) * (host / hostReferencePt(opts));
    return Math.max(6, Math.ceil(fontPt * 1.12 + padPt));
  }
  if (opts?.compoundLineSpacingPt != null && opts.compoundLineSpacingPt !== "") {
    const gap = compoundLineSpacingPt(fontPt, hostPt, opts);
    const padPt = hmmToPt(Number(opts?.frameHeightPaddingHmm ?? 80));
    return Math.max(8, Math.ceil(fontPt + gap * (glyphCount - 1) + padPt));
  }
  return Math.max(8, Math.ceil(hmmToPt(loStyleBoxHeightHmm(fontPt, glyphCount, opts))));
}

/** @deprecated Use effectiveFrameWidthPt(hostPt, opts). */
export function compoundBoxWidthPt(hostPt, fontPt, opts) {
  return effectiveFrameWidthPt(hostPt, opts);
}

/**
 * All geometry for one cluster from surrounding (host) font size.
 */
export function boxMetricsFromHost(hostPt, glyphCount, opts) {
  const ref = hostReferencePt(opts);
  const host = hostPt > 0 ? hostPt : ref;
  const fontPt = markFontPt(host, opts);
  const baselineShiftPt = scaleWithHost(
    Number(opts?.baselineShiftPt ?? 0),
    host,
    opts
  );
  return {
    hostPt: host,
    fontPt,
    widthPt: effectiveFrameWidthPt(host, opts),
    heightPt: compoundBoxHeightPt(host, fontPt, glyphCount, opts),
    lineSpacingPt: compoundLineSpacingPt(fontPt, host, opts),
    baselineShiftPt,
  };
}

/**
 * Vertical nudge for the inline box run (pt). Negative = lower.
 * mapping: baseline_shift_pt: -4  OR  vertical_offset_pt: 4 (positive = down).
 */
export function resolveBaselineShiftPt(inline = {}) {
  if (inline.baseline_shift_pt != null && inline.baseline_shift_pt !== "") {
    return Number(inline.baseline_shift_pt);
  }
  if (inline.vertical_offset_pt != null && inline.vertical_offset_pt !== "") {
    return -Number(inline.vertical_offset_pt);
  }
  return Number(inline.baselineShiftPt ?? 0);
}

/** Half-points for w:rPr/w:position (baseline_shift_pt scaled with hostFontPt). */
export function baselineShiftHalfPoints(opts) {
  let pt = Number(opts?.baselineShiftPt ?? 0);
  if (!pt) return 0;
  if (opts?.hostFontPt > 0) {
    pt = scaleWithHost(pt, opts.hostFontPt, opts);
  }
  return Math.round(pt * 2);
}

/** wp:effectExtent padding (EMU); keep small so Word does not reserve a wide gap after the box. */
export function inlineEffectExtentEmu(opts) {
  const pt = Number(opts?.inlineEffectExtentPt ?? 0);
  return Math.max(0, Math.round(pt * 12700));
}
