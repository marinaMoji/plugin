/* global Word */

/**
 * Apply / remove East Asian emphasis marks on the Word selection via OOXML.
 */

import { wordEnumsReady, W } from "../wordEnums.js";
import {
  applyEmphasisStyleInOoxml,
  clearEmphasisInOoxml,
} from "./emphasisOoxml.js";
import {
  normalizeEmphasisStyleId,
  shortName,
} from "./emphasisStyles.js";
import { getEmphasisDefault } from "./emphasisPrefs.js";

async function wordRun(fn) {
  if (!wordEnumsReady()) {
    throw new Error(
      "Word API still loading. Wait a few seconds and try again, or reopen the pane."
    );
  }
  return Word.run(fn);
}

function selectionTextIsEmpty(text) {
  return !text || !String(text).replace(/\u200b/g, "").trim();
}

/**
 * @param {string} [styleId] semantic id; omit → document default
 * @returns {Promise<string>} status message
 */
export async function runApplyEmphasis(styleId) {
  const resolved =
    normalizeEmphasisStyleId(styleId) || getEmphasisDefault();
  let chars = 0;
  await wordRun(async (context) => {
    const sel = context.document.getSelection();
    sel.load("text");
    await context.sync();
    if (selectionTextIsEmpty(sel.text)) {
      throw new Error("Select the characters to emphasise first.");
    }
    chars = [...sel.text.replace(/\s+/g, "")].length;
    const pkg = sel.getOoxml();
    await context.sync();
    if (!pkg.value) {
      throw new Error("Could not read the selection as OOXML.");
    }
    const patched = applyEmphasisStyleInOoxml(pkg.value, resolved);
    sel.insertOoxml(patched, W.insertReplace());
    await context.sync();
  });
  const name = shortName(resolved, "en");
  return chars === 1
    ? `Applied ${name} to 1 character.`
    : `Applied ${name} to the selection.`;
}

/** Remove emphasis marks; leaves other run formatting alone. */
export async function runRemoveEmphasis() {
  let hadText = false;
  await wordRun(async (context) => {
    const sel = context.document.getSelection();
    sel.load("text");
    await context.sync();
    if (selectionTextIsEmpty(sel.text)) {
      throw new Error("Select the emphasised text first (or place a range).");
    }
    hadText = true;
    const pkg = sel.getOoxml();
    await context.sync();
    if (!pkg.value) {
      throw new Error("Could not read the selection as OOXML.");
    }
    const patched = clearEmphasisInOoxml(pkg.value);
    sel.insertOoxml(patched, W.insertReplace());
    await context.sync();
  });
  return hadText ? "Removed emphasis marks." : "Done.";
}
