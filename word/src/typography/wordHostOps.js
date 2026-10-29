/* global Word */

/**
 * Shared Word.run helpers for typography OOXML apply/remove.
 */

import { wordEnumsReady, W } from "../wordEnums.js";

export async function wordRun(fn) {
  if (!wordEnumsReady()) {
    throw new Error(
      "Word API still loading. Wait a few seconds and try again, or reopen the pane."
    );
  }
  return Word.run(fn);
}

export function selectionTextIsEmpty(text) {
  return !text || !String(text).replace(/\u200b/g, "").trim();
}

/**
 * Load selection text (+ optional paragraph text), read OOXML, patch, write back.
 * @param {(ctx: {
 *   selection: Word.Range,
 *   text: string,
 *   paraText: string|null,
 *   ooxml: string,
 *   fontSize: number|null
 * }) => string|Promise<string>} patchFn returns new OOXML package
 */
export async function patchSelectionOoxml(patchFn, opts = {}) {
  const { allowEmpty = false, loadParagraph = false, loadFontSize = false } =
    opts;
  let meta = { text: "", paraText: null, fontSize: null };

  await wordRun(async (context) => {
    const sel = context.document.getSelection();
    sel.load("text");
    let para = null;
    if (loadParagraph) {
      para = sel.paragraphs.getFirst();
      para.load("text");
    }
    if (loadFontSize) {
      sel.font.load("size");
    }
    await context.sync();

    if (!allowEmpty && selectionTextIsEmpty(sel.text)) {
      throw new Error("Select text first.");
    }

    meta.text = sel.text || "";
    meta.paraText = para ? para.text || "" : null;
    meta.fontSize =
      loadFontSize && sel.font && typeof sel.font.size === "number"
        ? sel.font.size
        : null;

    const pkg = sel.getOoxml();
    await context.sync();
    if (!pkg.value) {
      throw new Error("Could not read the selection as OOXML.");
    }

    const patched = await patchFn({
      selection: sel,
      text: meta.text,
      paraText: meta.paraText,
      ooxml: pkg.value,
      fontSize: meta.fontSize,
    });
    if (!patched || patched === pkg.value) {
      // Still write if caller returned identical (noop) — skip insert.
      return;
    }
    sel.insertOoxml(patched, W.insertReplace());
    await context.sync();
  });

  return meta;
}
