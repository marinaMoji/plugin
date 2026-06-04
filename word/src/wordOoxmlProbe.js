/**
 * OOXML checks before Range.insertOoxml on the user's cluster.
 * Word has no validate-only API; we use structural checks + a scratch insert at doc end.
 */

import { W } from "./wordEnums.js";
import { SOURCE_PREFIX } from "./exportCore.js";

const MAX_OOXML_BYTES = 512 * 1024;

/** Fast structural checks (no Word host). */
export function sanityCheckOoxml(ooxml) {
  const errors = [];
  if (!ooxml || typeof ooxml !== "string") {
    return { ok: false, errors: ["OOXML is empty"] };
  }
  if (ooxml.includes("\0")) {
    errors.push("OOXML contains null characters");
  }
  if (ooxml.length > MAX_OOXML_BYTES) {
    errors.push(`OOXML exceeds ${MAX_OOXML_BYTES} bytes`);
  }
  const required = [
    ["pkg:package", "pkg:package wrapper"],
    ["Relationships", "package relationships"],
    ["/word/document.xml", "document part"],
    ["<w:document", "wordprocessingML document"],
    ["<w:body", "document body"],
    ["<w:p", "paragraph"],
    ["<w:r", "run"],
  ];
  for (const [needle, label] of required) {
    if (!ooxml.includes(needle)) {
      errors.push(`Missing ${label}`);
    }
  }
  if (!ooxml.includes("wp:inline") && !ooxml.includes("<w:sdt")) {
    errors.push("Missing kaeriten view (wp:inline or w:sdt)");
  }
  if (!ooxml.includes(SOURCE_PREFIX)) {
    errors.push("Missing marinaMoji source tag in descr/tag");
  }
  return { ok: errors.length === 0, errors };
}

export function ooxmlErrorDetail(err) {
  if (!err) return "unknown error";
  const parts = [];
  if (err.message) parts.push(err.message);
  if (err.code) parts.push(`code=${err.code}`);
  try {
    const info = err.debugInfo;
    if (info) {
      if (typeof info === "string") parts.push(info);
      else if (info.message) parts.push(info.message);
    }
  } catch {
    /* ignore */
  }
  return parts.join("; ") || String(err);
}

/**
 * Ask Word to accept the fragment at document end, then delete the probe (no cluster change).
 * A failure here usually means the same OOXML will throw on the real replace.
 */
export async function probeOoxmlWithWord(context, ooxml) {
  const check = sanityCheckOoxml(ooxml);
  if (!check.ok) {
    return { ok: false, phase: "sanity", errors: check.errors };
  }

  const anchor = context.document.body.getRange(W.rangeEnd());
  let inserted = null;
  try {
    inserted = anchor.insertOoxml(ooxml, W.insertAfter());
    await context.sync();
  } catch (err) {
    return {
      ok: false,
      phase: "probe",
      errors: [ooxmlErrorDetail(err)],
    };
  }

  try {
    if (inserted) {
      inserted.delete();
      await context.sync();
    }
  } catch {
    /* probe accepted but cleanup failed — still treat as validated */
  }

  return { ok: true, phase: "probe" };
}
