/* global Word, document */

/**
 * Renderer E: inline pictures.
 *
 * Why: every "live view object" we tried (content control, floating/inline text
 * box, OOXML wp:inline) is flattened, unwrapped, or corrupted by Word for Mac,
 * and the round-trip (Unrender) keeps failing. Inline pictures are a first-class
 * Office.js object that Word for Mac actually preserves across save/reload, flows
 * with the text, and reliably keeps its `altTextDescription`.
 *
 * Model:
 *   Render   : 問㆒㆑ → 問 + <inline PNG of stacked 一/レ>, alt = MARINAMOJI:kaeriten:id=…;source=㆒㆑
 *   Unrender : find the picture by alt text, replace it with the Unicode marks
 *   Refresh  : redraw the PNG at the current host font size
 *   Export   : read source marks from the alt text (no document mutation)
 *
 * The PNG is drawn on an off-screen canvas in the task-pane webview (which has
 * the system CJK fonts), so compound stacks like 一 over レ are trivial — we paint
 * them ourselves instead of fighting Word's layout engine.
 */

import { W } from "./wordEnums.js";
import {
  glyphsForMarks,
  encodeKaeritenSourceTag,
  parseKaeritenSourceTag,
} from "./exportCore.js";
import { scaleWithHost } from "./wordBoxLayout.js";

const PX_PER_PT = 96 / 72;
const DEFAULT_SUPERSAMPLE = 4;
const DEFAULT_FONT_FAMILY =
  '"Hiragino Mincho ProN","YuMincho","Yu Mincho","MS Mincho","Songti SC","SimSun",serif';

/** WordApi 1.2 (insertInlinePictureFromBase64) + 1.1 (body.inlinePictures, altText). */
export function wordHasInlinePictureApi() {
  try {
    return (
      typeof Office !== "undefined" &&
      Office.context?.requirements?.isSetSupported("WordApi", "1.2")
    );
  } catch {
    return false;
  }
}

/** Display glyphs in stack order (top → bottom), e.g. ㆒㆑ → ["一", "レ"]. */
export function orderedGlyphs(marks, byChar) {
  return glyphsForMarks(marks, byChar)
    .split("\n")
    .map((g) => g.trim())
    .filter((g) => g.length > 0);
}

/**
 * On-page footprint of the kaeriten image, in points, from the host font size.
 *
 * The PNG is cropped to the mark glyphs (no tall empty margins). Word often
 * scales oversized inline pictures to the line, which visually centers marks in
 * the kanji; vertical placement on the page is adjusted with run `font.position`
 * (see applyInlinePictureRunPosition).
 *
 * Single column of glyphs (stack) by default; a single row when `row` is true.
 */
export function imageMetricsFromHost(hostPt, glyphCount, opts = {}) {
  const em = hostPt > 0 ? hostPt : 12;
  const n = Math.max(1, glyphCount);
  const row = !!opts.row && n > 1;
  const isCompound = !row && n > 1;

  const glyphRatio = Number(opts.imageGlyphRatio ?? 0.42);
  const compoundRatio =
    opts.imageCompoundGlyphRatio != null && opts.imageCompoundGlyphRatio !== ""
      ? Number(opts.imageCompoundGlyphRatio)
      : glyphRatio;
  const cellPt = em * (isCompound ? compoundRatio : glyphRatio);

  const defaultGap = isCompound ? -0.15 : 0;
  const gapKey = isCompound ? "imageCompoundLineGapRatio" : "imageLineGapRatio";
  const gapPt =
    cellPt *
    Number(
      opts[gapKey] ??
        opts.imageLineGapRatio ??
        (isCompound ? defaultGap : 0)
    );

  const columns = row ? n : 1;
  const rows = row ? 1 : n;
  const widthPt = cellPt * columns + (row ? gapPt * (n - 1) : 0);
  const contentHeightPt = cellPt * rows + (row ? 0 : gapPt * (rows - 1));

  const boxHeightEm = Number(opts.imageBoxHeightEm ?? 0);
  const belowEm = Number(opts.imageBelowBaselineEm ?? 0.42);
  const anchor = String(opts.imageBaselineAnchor ?? "bottom").toLowerCase();
  const bottomPadPt = em * Number(opts.imageDescentEm ?? 0);

  let heightPt;
  let contentTopPt;

  if (boxHeightEm > 0) {
    heightPt = em * boxHeightEm;
    if (anchor === "top") {
      const belowBandPt = em * belowEm;
      contentTopPt = Math.max(0, belowBandPt - contentHeightPt);
    } else {
      const bandBottom = heightPt - bottomPadPt;
      const bandTop = bandBottom - em * belowEm;
      contentTopPt = Math.max(bandTop, bandBottom - contentHeightPt);
    }
  } else {
    heightPt = contentHeightPt + bottomPadPt;
    contentTopPt = 0;
  }

  const topPadPt = contentTopPt;

  return {
    cellPt,
    gapPt,
    widthPt,
    heightPt,
    contentHeightPt,
    contentTopPt,
    topPadPt,
    bottomPadPt,
    columns,
    rows,
  };
}

/**
 * Draw the mark cluster to a base64 PNG (no `data:` prefix — that is what
 * insertInlinePictureFromBase64 expects).
 * @returns {{ base64: string, widthPt: number, heightPt: number }}
 */
export function drawKaeritenImage(marks, byChar, hostPt, opts = {}) {
  if (typeof document === "undefined" || !document.createElement) {
    throw new Error("Canvas is unavailable; inline-picture rendering needs the task pane.");
  }
  const glyphs = orderedGlyphs(marks, byChar);
  const metrics = imageMetricsFromHost(hostPt, glyphs.length, opts);
  const supersample = Number(opts.imageSupersample ?? DEFAULT_SUPERSAMPLE);
  const scale = PX_PER_PT * supersample;

  const widthPx = Math.max(1, Math.round(metrics.widthPt * scale));
  const heightPx = Math.max(1, Math.round(metrics.heightPt * scale));
  const cellPx = metrics.cellPt * scale;
  const gapPx = metrics.gapPt * scale;
  const nudgePx = metrics.cellPt * scale * Number(opts.imageGlyphNudgeEm ?? 0.02);

  const canvas = document.createElement("canvas");
  canvas.width = widthPx;
  canvas.height = heightPx;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, widthPx, heightPx);

  if (opts.imageBackground) {
    ctx.fillStyle = opts.imageBackground;
    ctx.fillRect(0, 0, widthPx, heightPx);
  }

  ctx.fillStyle = opts.imageColor ?? "#000000";
  ctx.textAlign = "center";
  ctx.textBaseline = "bottom";
  const fontPx = cellPx * Number(opts.imageGlyphFill ?? 0.94);
  ctx.font = `${fontPx}px ${opts.imageFontFamily || DEFAULT_FONT_FAMILY}`;

  const bandBottomPx =
    metrics.heightPt * scale - metrics.bottomPadPt * scale - nudgePx;

  glyphs.forEach((glyph, i) => {
    const col = metrics.rows === 1 ? i : 0;
    const stackFromBottom =
      metrics.rows === 1 ? 0 : glyphs.length - 1 - i;
    const cx = (cellPx + (metrics.rows === 1 ? gapPx : 0)) * col + cellPx / 2;
    const cy =
      bandBottomPx - (cellPx + gapPx) * stackFromBottom;
    ctx.fillText(glyph, cx, cy);
  });

  const base64 = canvas.toDataURL("image/png").split(",")[1] || "";
  return { base64, widthPt: metrics.widthPt, heightPt: metrics.heightPt };
}

function applyPictureGeometry(pic, widthPt, heightPt) {
  try {
    pic.lockAspectRatio = false;
  } catch {
    /* optional */
  }
  pic.width = widthPt;
  pic.height = heightPt;
}

/** Run position (pt) for the inline picture; negative = lower on the line. */
export function inlinePictureBaselineShiftPt(hostPt, opts = {}) {
  let pt = Number(opts.imageBaselineShiftPt ?? opts.baselineShiftPt ?? -5);
  if (!pt) return 0;
  return scaleWithHost(pt, hostPt, opts);
}

/**
 * Word treats inline pictures like characters: Font.position lowers or raises the
 * whole image on the line (same as Format Font → Position for inline shapes).
 */
export async function applyInlinePictureRunPosition(context, pic, hostPt, opts) {
  const shiftPt = inlinePictureBaselineShiftPt(hostPt, opts);
  if (!shiftPt) return;
  try {
    const range = pic.getRange(W.rangeWhole());
    range.font.position = shiftPt;
    await context.sync();
  } catch {
    /* optional on some hosts */
  }
}

/**
 * Replace the marks run with an inline picture of the kaeriten, leaving the base
 * kanji as text. `marksRange` is the ㆒㆑ span after the base.
 */
export async function insertKaeritenInlinePicture(
  context,
  marksRange,
  marks,
  byChar,
  hostPt,
  opts,
  viewId
) {
  const { base64, widthPt, heightPt } = drawKaeritenImage(
    marks,
    byChar,
    hostPt,
    opts
  );
  const pic = marksRange.insertInlinePictureFromBase64(base64, W.insertReplace());
  pic.altTextTitle = "marinaMoji kaeriten";
  pic.altTextDescription = encodeKaeritenSourceTag(marks, viewId);
  applyPictureGeometry(pic, widthPt, heightPt);
  await context.sync();
  await applyInlinePictureRunPosition(context, pic, hostPt, opts);
  return { pic, widthPt, heightPt };
}

async function pictureOverlapsWorkRange(context, workRange, pic) {
  if (!workRange) return true;
  try {
    const rel = workRange.compareLocationWith(pic.getRange(W.rangeWhole()));
    rel.load("value");
    await context.sync();
    const v = rel.value;
    return v !== W.locBefore() && v !== W.locAfter();
  } catch {
    return true;
  }
}

/** marinaMoji inline pictures (by alt text) overlapping the work range. */
export async function listMarinaMojiInlinePictures(context, workRange) {
  const pics = context.document.body.inlinePictures;
  pics.load("items");
  await context.sync();
  for (const pic of pics.items) {
    pic.load(["altTextDescription", "altTextTitle"]);
  }
  await context.sync();

  const matched = [];
  for (const pic of pics.items) {
    const parsed =
      parseKaeritenSourceTag(pic.altTextDescription) ||
      parseKaeritenSourceTag(pic.altTextTitle);
    if (!parsed?.marks) continue;
    if (!(await pictureOverlapsWorkRange(context, workRange, pic))) continue;
    matched.push({ pic, marks: parsed.marks, viewId: parsed.viewId });
  }
  return matched;
}

/** Replace one kaeriten picture with its Unicode marks (round-trip restore). */
export async function unrenderOneInlinePicture(context, pic, marks) {
  if (!marks) return false;
  try {
    const range = pic.getRange(W.rangeWhole());
    range.insertText(marks, W.insertReplace());
    await context.sync();
    return true;
  } catch {
    return false;
  }
}

/** Redraw a kaeriten picture at the current host font size (Refresh). */
export async function refreshInlinePicture(
  context,
  pic,
  marks,
  byChar,
  hostPt,
  opts,
  viewId
) {
  const { base64, widthPt, heightPt } = drawKaeritenImage(
    marks,
    byChar,
    hostPt,
    opts
  );
  const range = pic.getRange(W.rangeWhole());
  const fresh = range.insertInlinePictureFromBase64(base64, W.insertReplace());
  fresh.altTextTitle = "marinaMoji kaeriten";
  fresh.altTextDescription = encodeKaeritenSourceTag(marks, viewId);
  applyPictureGeometry(fresh, widthPt, heightPt);
  await context.sync();
  await applyInlinePictureRunPosition(context, fresh, hostPt, opts);
  return fresh;
}
