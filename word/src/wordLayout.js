/* global Word */

import { W } from "./wordEnums.js";

const VERTICAL_ORIENTATIONS = new Set([
  "VerticalFarEast",
  "Vertical",
  "Upward",
  "Downward",
  "HorizontalRotatedFarEast",
]);

function isVerticalOrientation(value) {
  if (!value) return false;
  const name = String(value);
  return VERTICAL_ORIENTATIONS.has(name);
}

/**
 * True when the paragraph uses East Asian vertical layout (縦書き).
 * Floating text boxes use page-relative coords and misplace beside the column.
 */
export async function isVerticalFlow(context, range) {
  try {
    const para = range.paragraphs.getFirst();
    para.font.load("orientation");
    await context.sync();
    if (isVerticalOrientation(para.font.orientation)) return true;
  } catch {
    /* orientation needs WordApiDesktop 1.4+ on some builds */
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
