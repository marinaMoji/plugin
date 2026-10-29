/**
 * Pure OOXML transforms for East Asian emphasis marks (`w:em` on run properties).
 * Works on the string returned by Range.getOoxml() / accepted by insertOoxml().
 */

import { styleToEmVal } from "./emphasisStyles.js";

const EM_SELF =
  /<w:em\b[^>]*?(?:\/>|>\s*<\/w:em>)/gi;

function emElement(emVal) {
  return `<w:em w:val="${emVal}"/>`;
}

/**
 * Set or replace `w:em` on every text run in the package XML.
 * @param {string} ooxml
 * @param {string} emVal ST_Em: dot | comma | circle | underDot | none
 * @returns {string}
 */
export function setEmValInOoxml(ooxml, emVal) {
  if (typeof ooxml !== "string" || !ooxml) {
    throw new Error("OOXML package is empty.");
  }
  const val = String(emVal || "").trim();
  if (!val) throw new Error("Missing emphasis value.");

  const el = emElement(val);
  let out = ooxml.replace(EM_SELF, el);

  out = out.replace(
    /<w:rPr(\s[^>]*)?>([\s\S]*?)<\/w:rPr>/gi,
    (match, attrs, inner) => {
      if (/<w:em\b/i.test(inner)) return match;
      return `<w:rPr${attrs || ""}>${el}${inner}</w:rPr>`;
    }
  );

  out = out.replace(
    /<w:r(\s[^>]*)?>((?:(?!<\/w:r>)[\s\S])*?)<\/w:r>/gi,
    (match, attrs, body) => {
      if (/<w:rPr\b/i.test(body)) return match;
      if (!/<w:t[\s>]/i.test(body)) return match;
      return `<w:r${attrs || ""}><w:rPr>${el}</w:rPr>${body}</w:r>`;
    }
  );

  return out;
}

/** Apply a marinaMoji semantic style id. */
export function applyEmphasisStyleInOoxml(ooxml, styleId) {
  return setEmValInOoxml(ooxml, styleToEmVal(styleId));
}

/** Clear emphasis on every run (`w:em w:val="none"`). */
export function clearEmphasisInOoxml(ooxml) {
  return setEmValInOoxml(ooxml, "none");
}

/** True if the package already has a non-none emphasis mark. */
export function ooxmlHasEmphasis(ooxml) {
  if (typeof ooxml !== "string") return false;
  const re = /<w:em\b[^>]*\bw:val\s*=\s*["']([^"']+)["']/gi;
  let m;
  while ((m = re.exec(ooxml)) !== null) {
    if (m[1] && m[1].toLowerCase() !== "none") return true;
  }
  return false;
}
