/* global Word */

/**
 * Group ruby Apply / Remove for Word.
 */

import { wordEnumsReady, W } from "../wordEnums.js";
import {
  buildRubyReplaceOoxml,
  unwrapRubyInOoxml,
  assertRubyApplyAllowed,
} from "./rubyOoxml.js";
import { ooxmlHasRuby } from "./eastAsianLayoutOoxml.js";
import {
  wordRun,
  selectionTextIsEmpty,
  patchSelectionOoxml,
} from "./wordHostOps.js";

/**
 * @param {string} reading furigana / reading text
 */
export async function runApplyRuby(reading) {
  const rt = String(reading || "").trim();
  if (!rt) {
    throw new Error("Enter a ruby reading first.");
  }

  await wordRun(async (context) => {
    if (!wordEnumsReady()) {
      throw new Error("Word API still loading.");
    }
    const sel = context.document.getSelection();
    sel.load("text");
    sel.font.load("size");
    await context.sync();
    if (selectionTextIsEmpty(sel.text)) {
      throw new Error("Select the base text that should receive a ruby reading.");
    }
    const pkg = sel.getOoxml();
    await context.sync();
    assertRubyApplyAllowed(pkg.value || "");
    const basePt =
      sel.font && typeof sel.font.size === "number" ? sel.font.size : 12;
    const ooxml = buildRubyReplaceOoxml(sel.text, rt, { basePt });
    sel.insertOoxml(ooxml, W.insertReplace());
    await context.sync();
  });

  return "Applied ruby.";
}

export async function runRemoveRuby() {
  let found = false;
  await patchSelectionOoxml(({ ooxml }) => {
    if (!ooxmlHasRuby(ooxml)) {
      throw new Error(
        "No ruby found in the selection. Select the base text (or a range that includes the ruby)."
      );
    }
    found = true;
    return unwrapRubyInOoxml(ooxml);
  }, {});
  return found ? "Removed ruby." : "Done.";
}
