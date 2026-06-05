/* global Word */

/** OOXML values for East Asian vertical layout (sectPr or pPr). */
const VERTICAL_TEXT_DIRECTION_RE =
  /<w:textDirection[^>]*w:val="(tbRlV|tbRl|tbLrV|tbLr|btLrV|btLr)"/i;

const VERTICAL_ORIENTATION_NAMES = new Set([
  "verticalfareast",
  "vertical",
  "upward",
  "downward",
  "horizontalrotatedfareast",
]);

/** Word.TextOrientation numeric values (desktop). */
const VERTICAL_ORIENTATION_NUMBERS = new Set([1, 2, 3, 4, 5]);

function normalizeOrientationKey(value) {
  if (value == null || value === "") return "";
  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }
  return String(value).toLowerCase().replace(/[\s_-]/g, "");
}

export function ooxmlIndicatesVerticalFlow(xml) {
  if (!xml) return false;
  return VERTICAL_TEXT_DIRECTION_RE.test(String(xml));
}

function isVerticalOrientation(value) {
  if (value == null || value === "") return false;
  if (typeof value === "number" && VERTICAL_ORIENTATION_NUMBERS.has(value)) {
    return value !== 0;
  }
  const key = normalizeOrientationKey(value);
  if (!key) return false;
  if (key === "0" || key === "horizontal") return false;
  if (VERTICAL_ORIENTATION_NUMBERS.has(Number(key))) {
    return Number(key) !== 0;
  }
  return VERTICAL_ORIENTATION_NAMES.has(key);
}

async function verticalFromParagraphOoxml(context, range) {
  try {
    const para = range.paragraphs.getFirst();
    const pkg = para.getRange().getOoxml();
    await context.sync();
    return ooxmlIndicatesVerticalFlow(pkg.value);
  } catch {
    return false;
  }
}

async function documentUsesVerticalFlow(context) {
  try {
    const body = context.document.body;
    const pkg = body.getOoxml();
    await context.sync();
    const xml = String(pkg.value || "");
    if (ooxmlIndicatesVerticalFlow(xml)) return true;
    const sectBlocks = xml.match(/<w:sectPr[\s\S]*?<\/w:sectPr>/gi) || [];
    for (const block of sectBlocks) {
      if (ooxmlIndicatesVerticalFlow(block)) return true;
    }
  } catch {
    /* getOoxml optional on some hosts */
  }
  return false;
}

async function verticalFromSelectionOrientation(context) {
  try {
    const sel = context.document.getSelection();
    sel.load("orientation");
    await context.sync();
    return isVerticalOrientation(sel.orientation);
  } catch {
    return false;
  }
}

async function verticalFromFontOrientation(context, range) {
  try {
    const para = range.paragraphs.getFirst();
    para.font.load("orientation");
    await context.sync();
    if (isVerticalOrientation(para.font.orientation)) return true;
  } catch {
    /* WordApiDesktop 1.4+ */
  }
  try {
    range.font.load("orientation");
    await context.sync();
    if (isVerticalOrientation(range.font.orientation)) return true;
  } catch {
    /* optional */
  }
  return false;
}

/**
 * True when the paragraph uses East Asian vertical layout (縦書き).
 * @param {boolean} [assumeVertical] — mapping.json `word_assume_vertical`
 */
export async function isVerticalFlow(context, range, assumeVertical = false) {
  if (assumeVertical) return true;
  if (await documentUsesVerticalFlow(context)) return true;
  if (await verticalFromParagraphOoxml(context, range)) return true;
  if (await verticalFromFontOrientation(context, range)) return true;
  if (await verticalFromSelectionOrientation(context)) return true;
  return false;
}

export function pickTextOrientation(vertical) {
  if (!vertical) return null;
  try {
    if (Word?.ShapeTextOrientation?.horizontal != null) {
      return Word.ShapeTextOrientation.horizontal;
    }
  } catch {
    /* ignore */
  }
  return "Horizontal";
}

/**
 * Inline-picture compound layout: 縦書き stacks marks (一 over レ) on the left;
 * 横書き stacks to the right of the kanji (or row if imageRow).
 */
export function kaeritenImageUseRowLayout(vertical, markCount, opts = {}) {
  if (markCount <= 1) return false;
  if (vertical) {
    const layout = String(
      opts.imageVerticalCompoundLayout ??
        opts.verticalCompoundLayout ??
        "row"
    ).toLowerCase();
    return layout !== "stack";
  }
  return !!opts.imageRow;
}
