/**
 * Jidori (字取り) — Word native Fit Text (`w:fitText`).
 */

import {
  countGraphemes,
  fitTextTwipsForCells,
  initialN,
} from "./jidoriMath.js";
import {
  applyFitTextInOoxml,
  clearFitTextInOoxml,
} from "./jidoriOoxml.js";
import { ooxmlHasWarichu } from "./eastAsianLayoutOoxml.js";
import { patchSelectionOoxml } from "./wordHostOps.js";

/**
 * @param {number} nCells target fullwidth cells
 */
export async function runApplyJidori(nCells) {
  const n = Math.floor(Number(nCells));
  if (!Number.isFinite(n) || n < 1) {
    throw new Error("Enter a target width of at least 1 cell.");
  }
  if (n > 40) {
    throw new Error("Target is too large (try 40 cells or fewer).");
  }

  let graphemes = 0;
  await patchSelectionOoxml(
    ({ text, ooxml, fontSize }) => {
      graphemes = countGraphemes(String(text).replace(/\s+/g, ""));
      if (graphemes < 1) {
        throw new Error("Select the characters to fit.");
      }
      if (ooxmlHasWarichu(ooxml)) {
        throw new Error(
          "This selection is warichū. Remove warichū before applying jidori " +
            "(Word ignores eastAsianLayout when fitText is present)."
        );
      }
      const twips = fitTextTwipsForCells(n, fontSize || 12);
      return applyFitTextInOoxml(ooxml, twips, 1);
    },
    { loadFontSize: true }
  );

  return `Applied jidori (fit to ${n} cells; ${graphemes} grapheme${
    graphemes === 1 ? "" : "s"
  }).`;
}

export async function runRemoveJidori() {
  await patchSelectionOoxml(({ ooxml }) => clearFitTextInOoxml(ooxml), {});
  return "Removed Fit Text / jidori on the selection.";
}

export { countGraphemes, initialN, fitTextTwipsForCells };
