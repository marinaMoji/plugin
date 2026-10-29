/**
 * Group ruby via OOXML `w:ruby` (Phonetic Guide).
 */

import { escapeXml, wrapOoxmlPackage } from "../wordOoxml.js";
import { ooxmlHasWarichu } from "./eastAsianLayoutOoxml.js";

/**
 * Build a replace package: one group-ruby over baseText with reading.
 * @param {string} baseText
 * @param {string} reading
 * @param {{ basePt?: number }} [opts]
 */
export function buildRubyReplaceOoxml(baseText, reading, opts = {}) {
  const base = String(baseText || "");
  const rt = String(reading || "").trim();
  if (!base) throw new Error("Ruby base text is empty.");
  if (!rt) throw new Error("Ruby reading is empty.");

  const basePt = Number(opts.basePt) > 0 ? Number(opts.basePt) : 12;
  const baseHalf = Math.max(2, Math.round(basePt * 2));
  // Conventional ruby ~50% of base.
  const rubyHalf = Math.max(2, Math.round(baseHalf * 0.5));
  const raise = Math.max(rubyHalf, Math.round(baseHalf * 0.5) + rubyHalf);

  const inner = `<w:ruby>
  <w:rubyPr>
    <w:rubyAlign w:val="left"/>
    <w:hps w:val="${rubyHalf}"/>
    <w:hpsRaise w:val="${raise}"/>
    <w:hpsBaseText w:val="${baseHalf}"/>
    <w:lid w:val="ja-JP"/>
  </w:rubyPr>
  <w:rt>
    <w:r>
      <w:rPr><w:sz w:val="${rubyHalf}"/><w:szCs w:val="${rubyHalf}"/></w:rPr>
      <w:t xml:space="preserve">${escapeXml(rt)}</w:t>
    </w:r>
  </w:rt>
  <w:rubyBase>
    <w:r>
      <w:rPr><w:sz w:val="${baseHalf}"/><w:szCs w:val="${baseHalf}"/></w:rPr>
      <w:t xml:space="preserve">${escapeXml(base)}</w:t>
    </w:r>
  </w:rubyBase>
</w:ruby>`;

  return wrapOoxmlPackage(inner);
}

/**
 * Flatten every `w:ruby` to its `w:rubyBase` runs (drop readings).
 * Works on a getOoxml() package string.
 */
export function unwrapRubyInOoxml(ooxml) {
  if (typeof ooxml !== "string" || !ooxml) {
    throw new Error("OOXML package is empty.");
  }
  return ooxml.replace(
    /<w:ruby\b[^>]*>([\s\S]*?)<\/w:ruby>/gi,
    (_whole, inner) => {
      const base = /<w:rubyBase\b[^>]*>([\s\S]*?)<\/w:rubyBase>/i.exec(inner);
      if (base) return base[1];
      // Fallback: drop ruby wrapper entirely if base missing.
      return "";
    }
  );
}

export function assertRubyApplyAllowed(ooxml) {
  if (ooxmlHasWarichu(ooxml)) {
    throw new Error(
      "This selection is warichū. Remove warichū first — nesting ruby is unreliable."
    );
  }
}
