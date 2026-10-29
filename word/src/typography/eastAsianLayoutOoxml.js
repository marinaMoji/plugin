/**
 * OOXML `w:eastAsianLayout` — warichū (combine) and tate-chū-yoko (vert).
 * Word ignores vert when combine is on; refuse nesting in the host commands.
 */

import { setRunPropElement, ooxmlHasRunProp, onOff } from "./runPropsOoxml.js";

const COMBINE_ON = /w:combine\s*=\s*["'](?:on|1|true)["']/i;
const VERT_ON = /w:vert\s*=\s*["'](?:on|1|true)["']/i;

export function ooxmlHasWarichu(ooxml) {
  return ooxmlHasRunProp(ooxml, "eastAsianLayout", COMBINE_ON);
}

export function ooxmlHasTatechuyoko(ooxml) {
  return ooxmlHasRunProp(ooxml, "eastAsianLayout", VERT_ON);
}

export function ooxmlHasRuby(ooxml) {
  return typeof ooxml === "string" && /<w:ruby\b/i.test(ooxml);
}

/** Two lines in one (割注). No brackets — same bare policy as LibreOffice. */
export function applyWarichuInOoxml(ooxml) {
  return setRunPropElement(
    ooxml,
    "eastAsianLayout",
    `<w:eastAsianLayout w:combine="${onOff(true)}"/>`
  );
}

/** Horizontal-in-vertical (縦中横). */
export function applyTatechuyokoInOoxml(ooxml) {
  return setRunPropElement(
    ooxml,
    "eastAsianLayout",
    `<w:eastAsianLayout w:vert="${onOff(true)}" w:vertCompress="${onOff(true)}"/>`
  );
}

/** Clear both combine and vert (removes the whole eastAsianLayout element). */
export function clearEastAsianLayoutInOoxml(ooxml) {
  return setRunPropElement(ooxml, "eastAsianLayout", null);
}
