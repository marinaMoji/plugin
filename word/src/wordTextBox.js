/* global Word */

import {
  glyphsForMarks,
  normalizeDisplayKey,
  normalizeMarks,
  encodeKaeritenSourceTag,
  parseKaeritenSourceTag,
  bookmarkNameForMarks,
  bookmarkNameForViewId,
  nextKaeritenViewId,
} from "./exportCore.js";
import { W } from "./wordEnums.js";
import { isWordMac } from "./wordHost.js";
import { isVerticalFlow, pickTextOrientation } from "./wordLayout.js";
import { boxMetricsFromHost, compoundLineSpacingPt } from "./wordBoxLayout.js";
import {
  contiguousRangeAfterAnchor,
  nextCharacterRange,
  baseKanjiAdjacentBefore,
  baseCharRangeBeforeView,
  findBaseRangeForView,
  insertPointAfterBase,
  marksPresentAfterBase,
} from "./wordRange.js";
import { rawLengthForNormalizedPrefix } from "./exportCore.js";
import { buildPlainClusterOoxml } from "./wordOoxml.js";

export const SHAPE_ALT_PREFIX = "MARINAMOJI:source=";

export function wordHasTextBoxApi() {
  try {
    if (
      typeof Office !== "undefined" &&
      Office.context?.requirements?.isSetSupported
    ) {
      return Office.context.requirements.isSetSupported(
        "WordApiDesktop",
        "1.2"
      );
    }
  } catch {
    /* host not ready */
  }
  return false;
}

function pickEnum(enumObj, key, literal) {
  try {
    if (enumObj && enumObj[key] != null) return enumObj[key];
  } catch {
    /* ignore */
  }
  return literal;
}

function textBoxSize(opts, glyphCount, hostSize, vertical = false) {
  if (vertical) {
    const m = boxMetricsFromHost(hostSize, glyphCount, opts);
    const w = Math.max(7, Math.ceil(m.fontPt * glyphCount * 1.2 + 1));
    const h = Math.max(7, Math.ceil(m.fontPt * 1.15));
    return { width: w, height: h, fontPt: m.fontPt, lineSpacingPt: m.lineSpacingPt };
  }
  const m = boxMetricsFromHost(hostSize, glyphCount, opts);
  return {
    width: m.widthPt,
    height: m.heightPt,
    fontPt: m.fontPt,
    lineSpacingPt: m.lineSpacingPt,
  };
}

function initialTextBoxContent(glyphText) {
  const lines = glyphText.split("\n").filter((line) => line.length > 0);
  if (lines.length <= 1) return lines[0] || glyphText;
  return lines.join("\u000b");
}

/** Text that should live inside the shape (Mac compound differs from LO newline stack). */
function boxTextForShape(glyphText, vertical, opts) {
  const lines = glyphText.split("\n").filter((line) => line.length > 0);
  if (lines.length <= 1) return lines[0] || glyphText;
  if (vertical) return lines.join("");
  if (isWordMac() && opts?.macCompoundRow) return lines.join("");
  if (isWordMac()) return lines.join("\u000b");
  return initialTextBoxContent(glyphText);
}

function kaeritenGapChars(byChar) {
  const chars = new Set();
  for (const entry of Object.values(byChar || {})) {
    if (entry?.char) chars.add(entry.char);
    if (entry?.display_glyph) chars.add(entry.display_glyph);
  }
  return chars;
}

async function deleteNextCharacterAfterBase(context, baseRange) {
  try {
    const span = await nextCharacterRange(context, baseRange);
    if (!span) return false;
    span.delete();
    await context.sync();
    return true;
  } catch {
    return false;
  }
}

function isOnlyKaeritenPlainText(text, byChar) {
  const raw = (text || "").replace(/\r/g, "");
  if (!raw) return false;
  const junk = kaeritenGapChars(byChar);
  for (const ch of raw) {
    if (ch === "\u000b" || ch === "\u2028") continue;
    if (!junk.has(ch) && !/[\u3190-\u319f]/.test(ch)) return false;
  }
  return true;
}

/**
 * Word Mac often leaves 一/レ as plain 12 pt text *before* the inline shape while
 * also copying them into the box. Delete only that gap — never the shape body.
 */
async function clearPlainTextBetweenBaseAndShape(context, baseRange, shape, byChar) {
  try {
    const afterBase = baseRange.getRange(W.rangeEnd());
    const shapeStart = shape.getRange(W.rangeStart());
    const between = afterBase.expandTo(shapeStart);
    between.load("text");
    await context.sync();
    const gapText = (between.text || "").replace(/\r/g, "");
    if (!gapText || !isOnlyKaeritenPlainText(gapText, byChar)) return;
    between.delete();
    await context.sync();
  } catch {
    /* shape may be adjacent with no gap text */
  }
}

/** Duplicate kaeriten plain text immediately after the shape (Mac spillover). */
async function clearPlainTextAfterShape(context, shape, byChar, glyphText) {
  const targetKey = normalizeDisplayKey(glyphText);
  if (!targetKey) return;
  try {
    const afterShape = shape.getRange(W.rangeEnd());
    const para = afterShape.paragraphs.getFirst().getRange();
    const tail = afterShape.expandTo(para.getRange(W.rangeEnd()));
    tail.load("text");
    await context.sync();
    const raw = (tail.text || "").replace(/\r/g, "");
    const prefixLen = rawLengthForNormalizedPrefix(raw, targetKey);
    if (prefixLen <= 0) return;
    const prefix = raw.slice(0, prefixLen);
    if (
      normalizeDisplayKey(prefix) !== targetKey ||
      !isOnlyKaeritenPlainText(prefix, byChar)
    ) {
      return;
    }
    const span = await contiguousRangeAfterAnchor(
      context,
      afterShape,
      prefix
    );
    if (!span) return;
    span.delete();
    await context.sync();
  } catch {
    /* optional */
  }
}

async function removeMacPlainTextDuplicateGlyphs(
  context,
  baseRange,
  shape,
  byChar,
  glyphText,
  opts,
  lineCount,
  vertical
) {
  await clearPlainTextBetweenBaseAndShape(context, baseRange, shape, byChar);
  await clearPlainTextAfterShape(context, shape, byChar, glyphText);
  await applySmallFontToShapeBody(
    context,
    shape,
    baseRange,
    opts,
    lineCount,
    vertical
  );
}

/** Remove stray mark/display chars left in the gap (Mac unwrap orphans). */
async function sanitizeGapBeforeInsert(context, baseRange, byChar) {
  const junk = kaeritenGapChars(byChar);
  for (let attempt = 0; attempt < 8; attempt++) {
    const next = await nextCharacterRange(context, baseRange);
    if (!next) break;
    next.load("text");
    await context.sync();
    const ch = (next.text || "").replace(/\r/g, "")[0] || "";
    if (!ch || (!junk.has(ch) && !/[\u3190-\u319f]/.test(ch))) break;
    if (!(await deleteNextCharacterAfterBase(context, baseRange))) break;
  }
}

/**
 * Floating insertTextBox defaults to page coordinates (left:0 = left margin).
 * Pin the box to the anchor character so it sits after the kanji, not left of the line.
 */
async function anchorTextBoxToCharacter(context, shape, hostFontPt, vertical) {
  shape.relativeHorizontalPosition = W.relHorizCharacter();
  if (vertical) {
    shape.relativeVerticalPosition = W.relVertLine();
    shape.left = hostFontPt > 0 ? Math.round(hostFontPt * 0.12) : 0;
    shape.top = 0;
  } else {
    shape.relativeVerticalPosition = W.relVertLine();
    // Character anchor uses the glyph’s left edge; nudge right by ~1 em to sit after the kanji.
    shape.left = hostFontPt > 0 ? Math.round(hostFontPt * 0.92) : 0;
    shape.top = hostFontPt > 0 ? -Math.round(hostFontPt * 0.25) : 0;
  }
  await context.sync();
}

async function applyInlineTextWrap(context, shape) {
  const wrap = shape.textWrap;
  wrap.type = W.wrapInline();
  await context.sync();
}

/** Shape fill: borderless by default; optional Mac solid fill (mapping flags). */
async function applyKaeritenShapeFill(context, shape, opts) {
  const force =
    opts?.macForceSolidFill === true && isWordMac();
  if (force) {
    const hex = String(opts.macFillColor ?? "FFFFFF").replace(/^#/, "");
    try {
      shape.fill.setSolidColor(`#${hex}`);
      shape.fill.transparency = 0;
      await context.sync();
      return;
    } catch {
      /* fall through to clear */
    }
  }
  try {
    shape.fill.clear();
  } catch {
    try {
      shape.fill.transparency = 1;
    } catch {
      /* optional */
    }
  }
  await context.sync();
}

function pickTextFrameVerticalAlign(align) {
  const key = String(align || "bottom").toLowerCase();
  if (key === "top") return W.vertAlignTop();
  if (key === "middle" || key === "center" || key === "centre") {
    return W.vertAlignMiddle();
  }
  return W.vertAlignBottom();
}

function pickParagraphAlign(align) {
  const key = String(align || "center").toLowerCase();
  if (key === "left") return W.alignLeft();
  if (key === "right") return W.alignRight();
  return W.alignCenter();
}

async function applyTightCompoundLineSpacing(
  context,
  shape,
  opts,
  fontPt,
  hostPt,
  lineCount,
  lineSpacingPt
) {
  if (lineCount <= 1) return;
  try {
    const para = shape.body.paragraphs.getFirst();
    const pf = para.paragraphFormat;
    pf.spaceBefore = 0;
    pf.spaceAfter = 0;
    pf.lineSpacing =
      lineSpacingPt ??
      compoundLineSpacingPt(fontPt, hostPt, opts);
    pf.lineSpacingRule = W.lineSpacingExactly();
    await context.sync();
  } catch {
    /* optional on some Word Mac builds */
  }
}

async function applyTextBoxBodyAlignment(
  context,
  shape,
  opts,
  fontPt,
  hostPt,
  lineCount,
  lineSpacingPt
) {
  const hAlign =
    (opts?.boxExtraWidthRightPt ?? 0) > 0
      ? "left"
      : opts?.textFrameHorizontalAlign ?? "center";
  try {
    const para = shape.body.paragraphs.getFirst();
    para.alignment = pickParagraphAlign(hAlign);
    await context.sync();
  } catch {
    /* optional on some hosts */
  }
  await applyTightCompoundLineSpacing(
    context,
    shape,
    opts,
    fontPt,
    hostPt,
    lineCount,
    lineSpacingPt
  );
}

async function applyTextFrameInsetsOnly(context, shape, opts) {
  const tf = shape.textFrame;
  tf.topMargin = opts?.textFrameMarginTop ?? 0;
  tf.bottomMargin = opts?.textFrameMarginBottom ?? 0;
  tf.leftMargin = opts?.textFrameMarginLeft ?? 0;
  tf.rightMargin = opts?.textFrameMarginRight ?? 0;
  tf.verticalAlignment = pickTextFrameVerticalAlign(opts?.textFrameVerticalAlign);
  await context.sync();
}

/** True if shape is still an inline text box (Mac sometimes flattens after property churn). */
async function inlineShapeStillAlive(context, shape) {
  try {
    shape.load(["type", "textWrap"]);
    shape.textWrap.load("type");
    await context.sync();
    const t = shape.type;
    const isBox = t === Word.ShapeType.textBox || t === "TextBox";
    const wrap = shape.textWrap.type;
    const isInline =
      wrap === W.wrapInline() || wrap === "Inline" || wrap === "inline";
    return isBox && isInline;
  } catch {
    return false;
  }
}

async function applyTextBoxFrameStyle(context, shape, vertical, inlineLayout, opts) {
  try {
    const showLine =
      inlineLayout &&
      isWordMac() &&
      opts?.macForceSolidFill === true &&
      opts?.macNoOutline === false;
    shape.lineFormat.visible = showLine;
    if (showLine) {
      shape.lineFormat.color = "#B8C8E0";
      shape.lineFormat.weight = 0.25;
    }
  } catch {
    /* optional */
  }
  await applyKaeritenShapeFill(context, shape, opts);
  const tf = shape.textFrame;
  tf.topMargin = opts?.textFrameMarginTop ?? 0;
  tf.bottomMargin = opts?.textFrameMarginBottom ?? 0;
  tf.leftMargin = opts?.textFrameMarginLeft ?? 0;
  tf.rightMargin = opts?.textFrameMarginRight ?? 0;
  tf.verticalAlignment = pickTextFrameVerticalAlign(
    opts?.textFrameVerticalAlign
  );
  tf.autoSizeSetting = inlineLayout
    ? W.shapeAutoSizeNone()
    : pickEnum(Word?.ShapeAutoSize, "shapeToFitText", "ShapeToFitText");
  tf.wordWrap = false;
  const orient = pickTextOrientation(vertical);
  if (orient != null) {
    try {
      tf.orientation = orient;
    } catch {
      /* optional */
    }
  }
  if (!inlineLayout) {
    try {
      const wrap = shape.textWrap;
      wrap.type = W.wrapTight();
      wrap.side = pickEnum(Word?.ShapeTextWrapSide, "both", "Both");
    } catch {
      /* optional */
    }
  }
  await context.sync();
}

async function clearTextBoxBody(context, para) {
  try {
    para.getRange().insertText("", W.insertReplace());
    await context.sync();
  } catch {
    /* empty */
  }
}

async function fillTextBoxGlyphs(
  context,
  shape,
  glyphText,
  baseRange,
  opts,
  vertical = false
) {
  const lines = glyphText.split("\n").filter((line) => line.length > 0);
  const body = shape.body;
  const para = body.paragraphs.getFirst();
  const paraRange = para.getRange();
  const inBoxText = boxTextForShape(glyphText, vertical, opts);

  if (isWordMac() && !vertical) {
    paraRange.insertText(inBoxText, W.insertReplace());
    await context.sync();
  } else if (lines.length <= 1) {
    shape.body.load("text");
    await context.sync();
    const current = (shape.body.text || "").replace(/\r/g, "");
    if (current !== glyphText) {
      para.insertText(glyphText, W.insertReplace());
      await context.sync();
    }
  } else if (vertical) {
    paraRange.insertText(lines.join(""), W.insertReplace());
    await context.sync();
  } else {
    const breakStack = async () => {
      para.insertText(lines[0], W.insertReplace());
      await context.sync();
      for (let i = 1; i < lines.length; i++) {
        para.insertBreak(W.breakSoftLine(), W.insertEnd());
        para.insertText(lines[i], W.insertEnd());
        await context.sync();
      }
    };
    const softLineStack = async () => {
      paraRange.insertText(lines.join("\u000b"), W.insertReplace());
      await context.sync();
    };
    const lineSepStack = async () => {
      paraRange.insertText(lines.join("\u2028"), W.insertReplace());
      await context.sync();
    };
    const strategies =
      isWordMac() && !vertical
        ? [breakStack, softLineStack, lineSepStack]
        : [softLineStack, breakStack, lineSepStack];
    let stacked = false;
    let lastError = null;
    for (const strategy of strategies) {
      try {
        await strategy();
        stacked = true;
        break;
      } catch (err) {
        lastError = err;
        await clearTextBoxBody(context, para);
      }
    }
    if (!stacked) {
      if (lastError) throw lastError;
      paraRange.insertText(lines.join(""), W.insertReplace());
      await context.sync();
    }
  }

  return applySmallFontToShapeBody(
    context,
    shape,
    baseRange,
    opts,
    lines.length,
    vertical
  );
}

async function applySmallFontToShapeBody(
  context,
  shape,
  baseRange,
  opts,
  lineCount,
  vertical
) {
  baseRange.font.load(["name", "size"]);
  await context.sync();
  const { fontPt } = textBoxSize(opts, lineCount, baseRange.font.size, vertical);
  // shape.body.getRange() == TextFrame.TextRange (not the shape wrapper).
  const textRange = shape.body.getRange();
  textRange.font.size = fontPt;
  if (baseRange.font.name) {
    textRange.font.name = baseRange.font.name;
  }
  try {
    const paras = shape.body.paragraphs;
    paras.load("items");
    await context.sync();
    for (const para of paras.items) {
      const run = para.getRange();
      run.font.size = fontPt;
      if (baseRange.font.name) {
        run.font.name = baseRange.font.name;
      }
    }
  } catch {
    /* single-paragraph box */
  }
  await context.sync();
  return textRange;
}

async function ensureTextBoxBody(context, shape, glyphText, vertical, opts) {
  const expected = boxTextForShape(glyphText, vertical, opts);
  shape.body.load("text");
  await context.sync();
  const bodyText = (shape.body.text || "").replace(/\r/g, "");
  if (
    bodyText === expected ||
    bodyText === glyphText ||
    normalizeDisplayKey(bodyText) === normalizeDisplayKey(expected)
  ) {
    return;
  }
  const para = shape.body.paragraphs.getFirst();
  para.getRange().insertText(expected, W.insertReplace());
  await context.sync();
}

async function finalizeInlineKaeritenBox(
  context,
  shape,
  size,
  opts,
  glyphText,
  vertical,
  baseRange
) {
  const lineCount = glyphText.split("\n").filter((l) => l.length > 0).length || 1;
  shape.body.load("text");
  await context.sync();
  if (!(shape.body.text || "").replace(/\s/g, "")) {
    await ensureTextBoxBody(context, shape, glyphText, vertical, opts);
  }
  await applySmallFontToShapeBody(
    context,
    shape,
    baseRange,
    opts,
    lineCount,
    vertical
  );
  await applyTextFrameInsetsOnly(context, shape, opts);
  const hostPt = baseRange.font.size;
  const { fontPt, lineSpacingPt } = textBoxSize(
    opts,
    lineCount,
    hostPt,
    vertical
  );
  await applyTextBoxBodyAlignment(
    context,
    shape,
    opts,
    fontPt,
    hostPt,
    lineCount,
    lineSpacingPt
  );
  try {
    shape.width = size.width;
    shape.height = size.height;
    await context.sync();
  } catch {
    /* optional */
  }
  await applyInlineTextWrap(context, shape);
  if (!(await inlineShapeStillAlive(context, shape))) {
    await applyInlineTextWrap(context, shape);
    await applyKaeritenShapeFill(context, shape, opts);
    if (!(await inlineShapeStillAlive(context, shape))) {
      throw new Error(
        "Word removed the inline kaeriten box (shape flattened). Try re-render or use LibreOffice for editing."
      );
    }
  }
}

/**
 * Insert a borderless text box at the gap after the base kanji (insertAnchor = base end).
 * @param {"floating"|"inline"} layout — inline uses textWrap.type = inline (LO “as character”);
 *   floating uses Character position + left/top nudges (legacy Renderer B).
 */
export async function insertKaeritenTextBox(
  context,
  insertAnchor,
  baseRange,
  marks,
  byChar,
  opts,
  layout = "floating"
) {
  const inlineLayout = layout === "inline";
  const glyphText = glyphsForMarks(marks, byChar);
  const lineCount = glyphText.split("\n").filter((l) => l.length > 0).length || 1;
  baseRange.font.load("size");
  await context.sync();
  const hostFontPt = baseRange.font.size;
  const vertical = await isVerticalFlow(context, baseRange);
  const size = textBoxSize(opts, lineCount, hostFontPt, vertical);
  const boxSeed =
    inlineLayout && isWordMac()
      ? ""
      : boxTextForShape(glyphText, vertical, opts);

  const shape = insertAnchor.insertTextBox(boxSeed, {
    width: size.width,
    height: size.height,
  });
  const viewId = nextKaeritenViewId();
  shape.altTextDescription = encodeKaeritenSourceTag(marks, viewId);
  await context.sync();

  if (inlineLayout) {
    await applyInlineTextWrap(context, shape);
    await applyTextBoxFrameStyle(context, shape, vertical, true, opts);
  } else {
    await anchorTextBoxToCharacter(context, shape, hostFontPt, vertical);
    await applyTextBoxFrameStyle(context, shape, vertical, false, opts);
  }

  await fillTextBoxGlyphs(
    context,
    shape,
    glyphText,
    baseRange,
    opts,
    vertical
  );

  if (inlineLayout) {
    await finalizeInlineKaeritenBox(
      context,
      shape,
      size,
      opts,
      glyphText,
      vertical,
      baseRange
    );
    if (isWordMac()) {
      await removeMacPlainTextDuplicateGlyphs(
        context,
        baseRange,
        shape,
        byChar,
        glyphText,
        opts,
        lineCount,
        vertical
      );
    }
  } else {
    await ensureTextBoxBody(context, shape, glyphText, vertical, opts);
    await applyTextFrameInsetsOnly(context, shape, opts);
    const { lineSpacingPt } = textBoxSize(opts, lineCount, hostFontPt, vertical);
    await applyTextBoxBodyAlignment(
      context,
      shape,
      opts,
      size.fontPt,
      hostFontPt,
      lineCount,
      lineSpacingPt
    );
    await anchorTextBoxToCharacter(context, shape, hostFontPt, vertical);
  }
  await context.sync();
  return {
    kind: inlineLayout ? "inlineTextBox" : "textBox",
    shape,
    marks,
    viewId,
  };
}

/** Renderer C: in-line-with-text text box (Word.ShapeTextWrapType.inline). */
export async function insertKaeritenInlineTextBox(
  context,
  insertAnchor,
  baseRange,
  marks,
  byChar,
  opts
) {
  return insertKaeritenTextBox(
    context,
    insertAnchor,
    baseRange,
    marks,
    byChar,
    opts,
    "inline"
  );
}

/** True when shape carries marinaMoji source marks (alt/descr), not arbitrary small text. */
export function isMarinaMojiTextBox(shape) {
  return !!marksFromShape(shape, null, "");
}

export function marksFromShape(shape, displayLookup, displayText) {
  const candidates = [
    shape.altTextDescription,
    shape.altTextTitle,
    shape.name,
  ];
  for (const raw of candidates) {
    const parsed = parseKaeritenSourceTag(raw);
    if (parsed?.marks) return parsed.marks;
  }
  return null;
}

/** Unique per rendered view (not just ㆒㆑ — two boxes can share marks). */
export function viewKeyForShape(shape) {
  const alt = String(
    shape?.altTextDescription ?? shape?.altTextTitle ?? ""
  ).trim();
  if (alt && /marinamoji|source=/i.test(alt)) return alt;
  const id = shape?.id;
  return id != null && id !== "" ? `word-shape:${id}` : "";
}

export function viewIdFromShape(shape) {
  const alt = String(shape?.altTextDescription ?? "").trim();
  const parsed = parseKaeritenSourceTag(alt);
  return parsed?.viewId ?? null;
}

/** Word may not map wp:docPr descr to alt text; set explicitly after OOXML insert. */
export async function tagInlineShapeAfterBase(context, baseRange, marks, viewId) {
  if (!marks) return false;
  const tag = encodeKaeritenSourceTag(marks, viewId);
  try {
    const anchor = insertPointAfterBase(baseRange);
    const shapes = context.document.body.shapes;
    shapes.load("items");
    await context.sync();
    for (const shape of shapes.items) {
      shape.load(["type", "altTextDescription", "body"]);
      shape.body.load("text");
    }
    await context.sync();
    for (const shape of shapes.items) {
      if (
        shape.type !== Word.ShapeType.textBox &&
        shape.type !== "TextBox"
      ) {
        continue;
      }
      try {
        const rel = anchor.compareLocationWith(shape.body.getRange());
        rel.load("value");
        await context.sync();
        const v = rel.value;
        if (v === W.locBefore() || v === W.locAfter()) continue;
      } catch {
        /* include on overlap check failure */
      }
      const alt = (shape.altTextDescription || "").trim();
      if (!parseKaeritenSourceTag(alt)) {
        shape.altTextDescription = tag;
        await context.sync();
      }
      return true;
    }
  } catch {
    /* optional */
  }
  return false;
}

function pushTextBoxMatch(matched, seen, shape, displayLookup) {
  const key = String(shape.id ?? shape.altTextDescription ?? "");
  if (key && seen.has(key)) return;
  const displayText = shape.body.text;
  const marks = marksFromShape(shape, displayLookup, displayText);
  if (!marks || !isMarinaMojiTextBox(shape)) return;
  if (key) seen.add(key);
  matched.push({ shape, marks, displayText });
}

export async function shapeOverlapsWorkRange(context, workRange, shape) {
  if (!workRange) return true;
  try {
    const rel = workRange.compareLocationWith(shape.body.getRange());
    rel.load("value");
    await context.sync();
    const v = rel.value;
    return v !== W.locBefore() && v !== W.locAfter();
  } catch {
    return true;
  }
}

async function collectTextBoxesFromShapeList(
  context,
  shapeItems,
  workRange,
  displayLookup,
  matched,
  seen
) {
  for (const shape of shapeItems) {
    shape.load(["type", "altTextDescription", "altTextTitle", "name", "id", "body"]);
    shape.body.load("text");
  }
  await context.sync();

  for (const shape of shapeItems) {
    if (shape.type !== Word.ShapeType.textBox && shape.type !== "TextBox") {
      continue;
    }
    if (!(await shapeOverlapsWorkRange(context, workRange, shape))) {
      continue;
    }
    pushTextBoxMatch(matched, seen, shape, displayLookup);
  }
}

/** Paragraph scan — inline OOXML boxes are sometimes missing from body.shapes on Mac. */
async function listTextBoxesInWorkRangeParagraphs(
  context,
  workRange,
  displayLookup,
  matched,
  seen
) {
  if (!workRange) return;
  try {
    const paras = workRange.paragraphs;
    paras.load("items");
    await context.sync();
    for (const para of paras.items) {
      const paraShapes = para.shapes;
      paraShapes.load("items");
      await context.sync();
      await collectTextBoxesFromShapeList(
        context,
        paraShapes.items,
        workRange,
        displayLookup,
        matched,
        seen
      );
    }
  } catch {
    /* paragraph.shapes optional */
  }
}

export async function listMarinaMojiTextBoxes(context, workRange, displayLookup) {
  const matched = [];
  const seen = new Set();

  const shapes = context.document.body.shapes;
  shapes.load("items");
  await context.sync();
  await collectTextBoxesFromShapeList(
    context,
    shapes.items,
    workRange,
    displayLookup,
    matched,
    seen
  );

  await listTextBoxesInWorkRangeParagraphs(
    context,
    workRange,
    displayLookup,
    matched,
    seen
  );

  return matched;
}

async function dropKaeritenBookmarkForMarks(context, marks) {
  try {
    const bm = context.document.body.bookmarks.getItem(
      bookmarkNameForMarks(marks)
    );
    bm.delete();
    await context.sync();
  } catch {
    /* optional */
  }
}

async function dropKaeritenBookmarkForViewId(context, viewId) {
  if (!viewId) return;
  try {
    const bm = context.document.body.bookmarks.getItem(
      bookmarkNameForViewId(viewId)
    );
    bm.delete();
    await context.sync();
  } catch {
    /* optional */
  }
}

async function dropKaeritenBookmarksForShape(context, shape, marks) {
  await dropKaeritenBookmarkForViewId(context, viewIdFromShape(shape));
  if (marks) await dropKaeritenBookmarkForMarks(context, marks);
}

async function ensureShapeRemoved(context, shape) {
  try {
    shape.delete();
    await context.sync();
  } catch {
    /* already removed */
  }
}

export async function resolveBaseBeforeShape(context, workRange, shape) {
  const viewRange = shape.body.getRange();
  return (
    (await findBaseRangeForView(context, workRange, viewRange)) ||
    (await baseKanjiAdjacentBefore(context, viewRange)) ||
    (await baseCharRangeBeforeView(context, viewRange))
  );
}

async function unrenderSucceeded(context, baseRange, marks, workRange, baseChar) {
  if (await marksPresentAfterBase(context, baseRange, marks)) {
    return true;
  }
  if (!workRange || !baseChar) return false;
  workRange.load("text");
  await context.sync();
  const text = (workRange.text || "").replace(/\r/g, "");
  return text.includes(baseChar + normalizeMarks(marks));
}

export async function deleteShapeIfMarksPresent(context, shape, marks, workRange) {
  const baseRange = await resolveBaseBeforeShape(context, workRange, shape);
  if (!baseRange || !(await marksPresentAfterBase(context, baseRange, marks))) {
    return false;
  }
  await ensureShapeRemoved(context, shape);
  await dropKaeritenBookmarkForMarks(context, marks);
  return true;
}

/** Last resort: find base in workRange and insert marks after it. */
export async function emergencyRestoreMarks(context, workRange, stubs) {
  const restored = [];
  for (const item of stubs) {
    const { marks, baseChar } = item;
    if (!marks || !baseChar || !workRange) continue;
    let baseRange = item.baseRange;
    try {
      if (baseRange) {
        baseRange.load("text");
        await context.sync();
      }
    } catch {
      baseRange = null;
    }
    if (!baseRange) {
      try {
        const hits = workRange.search(baseChar, {
          matchCase: true,
          matchWholeWord: false,
        });
        hits.load("items");
        await context.sync();
        if (hits.items.length) {
          baseRange = hits.items[hits.items.length - 1].getRange();
        }
      } catch {
        baseRange = null;
      }
    }
    if (!baseRange) continue;
    if (await marksPresentAfterBase(context, baseRange, marks)) {
      restored.push(marks);
      continue;
    }
    try {
      insertPointAfterBase(baseRange).insertText(marks, W.insertAfter());
      await context.sync();
      if (await marksPresentAfterBase(context, baseRange, marks)) {
        await dropKaeritenBookmarkForMarks(context, marks);
        restored.push(marks);
      }
    } catch {
      /* try next stub */
    }
  }
  return restored;
}

/**
 * Restore Unicode marks after the base kanji, then remove the inline text box.
 * Inserts ㆒㆑ first, then deletes the box (cluster replace is fallback only).
 * @returns {{ success: boolean, recovery: { baseRange, baseChar, marks } | null }}
 */
export async function unrenderOneTextBox(context, shape, marks, workRange = null) {
  const resolved =
    marksFromShape(shape, null, "") || String(marks || "").replace(/\s/g, "");
  const recovery = { baseRange: null, baseChar: "", marks: resolved };

  if (!resolved) {
    await ensureShapeRemoved(context, shape);
    return { success: false, recovery: null };
  }

  const boxRange = shape.body.getRange();
  const baseRange = await resolveBaseBeforeShape(context, workRange, shape);

  if (!baseRange) {
    return { success: false, recovery: null };
  }

  const baseChar = (baseRange.text || "").replace(/\r/g, "");
  recovery.baseRange = baseRange;
  recovery.baseChar = baseChar;

  const complete = async () => {
    await ensureShapeRemoved(context, shape);
    await dropKaeritenBookmarksForShape(context, shape, resolved);
    return unrenderSucceeded(
      context,
      baseRange,
      resolved,
      workRange,
      baseChar
    );
  };

  if (await unrenderSucceeded(context, baseRange, resolved, workRange, baseChar)) {
    await ensureShapeRemoved(context, shape);
    await dropKaeritenBookmarksForShape(context, shape, resolved);
    return { success: true, recovery: null };
  }

  const tryInsertThenDelete = async (insertFn) => {
    await insertFn();
    await context.sync();
    await ensureShapeRemoved(context, shape);
    await context.sync();
    return complete();
  };

  try {
    if (
      await tryInsertThenDelete(() =>
        insertPointAfterBase(baseRange).insertText(resolved, W.insertAfter())
      )
    ) {
      return { success: true, recovery: null };
    }
  } catch {
    /* next strategy */
  }

  try {
    if (
      await tryInsertThenDelete(() =>
        boxRange.getRange(W.locBefore()).insertText(resolved, W.insertAfter())
      )
    ) {
      return { success: true, recovery: null };
    }
  } catch {
    /* next strategy */
  }

  if (baseChar) {
    let cluster = null;
    try {
      cluster = baseRange.expandTo(boxRange);
    } catch {
      cluster = null;
    }
    if (cluster) {
      try {
        cluster.insertOoxml(
          buildPlainClusterOoxml(baseChar, resolved),
          W.insertReplace()
        );
        await context.sync();
        if (await complete()) {
          return { success: true, recovery: null };
        }
      } catch {
        /* optional */
      }
      try {
        cluster.insertText(baseChar + resolved, W.insertReplace());
        await context.sync();
        if (await complete()) {
          return { success: true, recovery: null };
        }
      } catch {
        /* optional */
      }
    }
  }

  try {
    insertPointAfterBase(baseRange).insertText(resolved, W.insertAfter());
    await context.sync();
    if (await unrenderSucceeded(context, baseRange, resolved, workRange, baseChar)) {
      await dropKaeritenBookmarksForShape(context, shape, resolved);
      return { success: true, recovery: null };
    }
  } catch {
    /* optional */
  }

  return {
    success: false,
    recovery,
  };
}

async function resolveRecoveryBaseRange(context, item, workRange) {
  const { baseRange, baseChar, marks, shape } = item;
  if (!marks) return null;
  if (shape) {
    const base = await resolveBaseBeforeShape(context, workRange, shape);
    if (base) return base;
  }
  if (baseRange) {
    try {
      baseRange.load("text");
      await context.sync();
      return baseRange;
    } catch {
      /* stale */
    }
  }
  if (!workRange || !baseChar) return null;
  try {
    const hits = workRange.search(baseChar, {
      matchCase: true,
      matchWholeWord: false,
    });
    hits.load("items");
    await context.sync();
    if (!hits.items.length) return null;
    return hits.items[hits.items.length - 1].getRange();
  } catch {
    return null;
  }
}

/** Insert marks after base when the box was removed but Unicode was not restored. */
export async function recoverMarksAfterBase(context, recoveries, workRange) {
  const restored = [];
  for (const item of recoveries) {
    const { marks } = item;
    const base = await resolveRecoveryBaseRange(context, item, workRange);
    if (!base || !marks) continue;
    if (await marksPresentAfterBase(context, base, marks)) {
      restored.push(marks);
      continue;
    }
    try {
      insertPointAfterBase(base).insertText(marks, W.insertAfter());
      await context.sync();
      if (await marksPresentAfterBase(context, base, marks)) {
        await dropKaeritenBookmarkForMarks(context, marks);
        restored.push(marks);
      }
    } catch {
      /* try next */
    }
  }
  return restored;
}

/** Refill box glyphs and resize to current host font (no shape.body.clear). */
export async function refreshKaeritenTextBox(
  context,
  shape,
  marks,
  byChar,
  opts,
  vertical = false
) {
  const glyphText = glyphsForMarks(marks, byChar);
  const bodyRange = shape.body.getRange();
  const baseRange =
    (await baseKanjiAdjacentBefore(context, bodyRange)) || bodyRange;
  await fillTextBoxGlyphs(context, shape, glyphText, baseRange, opts, vertical);

  if (!baseRange || baseRange === bodyRange) return;

  baseRange.font.load("size");
  await context.sync();
  const lineCount =
    glyphText.split("\n").filter((l) => l.length > 0).length || 1;
  const hostFontPt = baseRange.font.size;
  const size = textBoxSize(opts, lineCount, hostFontPt, vertical);
  try {
    shape.width = size.width;
    shape.height = size.height;
    await context.sync();
  } catch {
    /* optional */
  }
  const { lineSpacingPt, fontPt } = textBoxSize(
    opts,
    lineCount,
    hostFontPt,
    vertical
  );
  await applyTextBoxBodyAlignment(
    context,
    shape,
    opts,
    fontPt,
    hostFontPt,
    lineCount,
    lineSpacingPt
  );
}
