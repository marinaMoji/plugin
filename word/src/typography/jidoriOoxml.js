/**
 * OOXML `w:fitText` for jidori (字取り).
 */

import { setRunPropElement, ooxmlHasRunProp } from "./runPropsOoxml.js";

export function ooxmlHasFitText(ooxml) {
  return ooxmlHasRunProp(ooxml, "fitText");
}

/**
 * @param {string} ooxml
 * @param {number} twips width
 * @param {number} [id] optional link id for multi-run fit
 */
export function applyFitTextInOoxml(ooxml, twips, id = 1) {
  const val = Math.max(1, Math.min(31680, Math.round(Number(twips) || 0)));
  const eid = Math.max(0, Math.floor(Number(id) || 1));
  return setRunPropElement(
    ooxml,
    "fitText",
    `<w:fitText w:val="${val}" w:id="${eid}"/>`
  );
}

export function clearFitTextInOoxml(ooxml) {
  return setRunPropElement(ooxml, "fitText", null);
}
