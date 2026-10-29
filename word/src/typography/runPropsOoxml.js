/**
 * Shared helpers for injecting / clearing elements inside every text run's w:rPr.
 */

/**
 * Replace or inject a run-property element on every text run.
 * @param {string} ooxml
 * @param {string} localName e.g. "eastAsianLayout" or "fitText" (no prefix)
 * @param {string|null} elementXml full element e.g. `<w:eastAsianLayout w:vert="1"/>`,
 *   or null to remove the element entirely
 */
export function setRunPropElement(ooxml, localName, elementXml) {
  if (typeof ooxml !== "string" || !ooxml) {
    throw new Error("OOXML package is empty.");
  }
  const name = String(localName || "").trim();
  if (!name) throw new Error("Missing run property name.");

  const selfRe = new RegExp(
    `<w:${name}\\b[^>]*?(?:\\/>|>\\s*<\\/w:${name}>)`,
    "gi"
  );

  let out = ooxml;
  if (elementXml) {
    out = out.replace(selfRe, elementXml);
  } else {
    out = out.replace(selfRe, "");
  }

  out = out.replace(
    /<w:rPr(\s[^>]*)?>([\s\S]*?)<\/w:rPr>/gi,
    (match, attrs, inner) => {
      const has = new RegExp(`<w:${name}\\b`, "i").test(inner);
      if (elementXml) {
        if (has) return match;
        return `<w:rPr${attrs || ""}>${elementXml}${inner}</w:rPr>`;
      }
      if (!has) return match;
      const cleaned = inner.replace(selfRe, "");
      return `<w:rPr${attrs || ""}>${cleaned}</w:rPr>`;
    }
  );

  if (elementXml) {
    out = out.replace(
      /<w:r(\s[^>]*)?>((?:(?!<\/w:r>)[\s\S])*?)<\/w:r>/gi,
      (match, attrs, body) => {
        if (/<w:rPr\b/i.test(body)) return match;
        if (!/<w:t[\s>]/i.test(body)) return match;
        return `<w:r${attrs || ""}><w:rPr>${elementXml}</w:rPr>${body}</w:r>`;
      }
    );
  }

  return out;
}

/** True if any run has `<w:localName ...>` matching attrRegex (optional). */
export function ooxmlHasRunProp(ooxml, localName, attrRegex = null) {
  if (typeof ooxml !== "string") return false;
  const re = new RegExp(`<w:${localName}\\b([^>]*)>`, "gi");
  let m;
  while ((m = re.exec(ooxml)) !== null) {
    if (!attrRegex) return true;
    if (attrRegex.test(m[1] || "")) return true;
  }
  return false;
}

/** ST_OnOff-ish: Word accepts on/1/true. */
export function onOff(value) {
  return value ? "1" : "0";
}
