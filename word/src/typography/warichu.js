/**
 * Warichū (割注) — Word `w:eastAsianLayout w:combine`.
 */

import {
  applyWarichuInOoxml,
  clearEastAsianLayoutInOoxml,
  ooxmlHasRuby,
} from "./eastAsianLayoutOoxml.js";
import { selectionCoversWholeParagraphText } from "./tatechuyokoPolicy.js";
import { patchSelectionOoxml } from "./wordHostOps.js";

export async function runApplyWarichu() {
  await patchSelectionOoxml(
    ({ text, paraText, ooxml }) => {
      if (selectionCoversWholeParagraphText(text, paraText)) {
        throw new Error(
          "The whole paragraph is selected. Warichū must be a span inside the paragraph " +
            "(leave some body text outside the selection)."
        );
      }
      if (ooxmlHasRuby(ooxml)) {
        throw new Error(
          "This selection already has ruby. Remove ruby first, or apply warichū to a separate note span."
        );
      }
      return applyWarichuInOoxml(ooxml);
    },
    { loadParagraph: true }
  );
  return "Applied warichū (two lines in one).";
}

export async function runRemoveWarichu() {
  await patchSelectionOoxml(({ ooxml }) => clearEastAsianLayoutInOoxml(ooxml), {});
  return "Removed warichū / East Asian layout on the selection.";
}
