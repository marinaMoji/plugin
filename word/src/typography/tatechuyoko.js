/**
 * Tate-chū-yoko (縦中横) — Word `w:eastAsianLayout w:vert`.
 */

import {
  applyTatechuyokoInOoxml,
  clearEastAsianLayoutInOoxml,
  ooxmlHasWarichu,
  ooxmlHasRuby,
} from "./eastAsianLayoutOoxml.js";
import {
  classifySelection,
  OK,
  CONFIRM,
  REFUSE,
} from "./tatechuyokoPolicy.js";
import { patchSelectionOoxml } from "./wordHostOps.js";

/**
 * @param {{ confirm?: (msg: string) => boolean }} [hooks]
 */
export async function runApplyTatechuyoko(hooks = {}) {
  const confirmFn =
    typeof hooks.confirm === "function"
      ? hooks.confirm
      : (msg) =>
          typeof window !== "undefined" && window.confirm
            ? window.confirm(msg)
            : false;

  let applied = false;
  await patchSelectionOoxml(
    ({ text, ooxml }) => {
      const decision = classifySelection(text);
      if (decision.verdict === REFUSE) {
        throw new Error(decision.message_en || "Cannot apply tate-chū-yoko.");
      }
      if (decision.verdict === CONFIRM) {
        if (!confirmFn(decision.message_en)) {
          throw new Error("Cancelled.");
        }
      }
      if (ooxmlHasWarichu(ooxml)) {
        throw new Error(
          "This selection is warichū. Remove warichū first — Word cannot combine both."
        );
      }
      if (ooxmlHasRuby(ooxml)) {
        throw new Error(
          "This selection has ruby. Remove ruby first, or apply tate-chū-yoko to a separate span."
        );
      }
      applied = true;
      return applyTatechuyokoInOoxml(ooxml);
    },
    {}
  );

  if (!applied) return "Done.";
  return "Applied tate-chū-yoko (visible in vertical text).";
}

export async function runRemoveTatechuyoko() {
  await patchSelectionOoxml(({ ooxml }) => clearEastAsianLayoutInOoxml(ooxml), {});
  return "Removed tate-chū-yoko / East Asian layout on the selection.";
}

export { classifySelection, OK, CONFIRM, REFUSE };
