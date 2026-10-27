/* global Word */

import { wordEnumsReady } from "./wordEnums.js";
import { exportPlainText } from "./exportCore.js";
import {
  loadMapping,
  renderKaeritenDocument,
  unrenderKaeritenDocument,
  refreshKaeritenDocument,
  canonicalTextForExport,
} from "./render.js";
import { writeClipboardText } from "./clipboard.js";
import {
  runInsertComposedCharacter,
  insertComposedSvgText,
  refreshComposedCharacters,
} from "./wordComposedInsert.js";
import { runInsertComposedSvgSpike } from "./wordSvgSpike.js";

async function wordRun(fn) {
  if (!wordEnumsReady()) {
    throw new Error(
      "Word API still loading. Wait a few seconds and try again, or reopen the pane."
    );
  }
  await Word.run(fn);
}

export async function runRenderKaeriten() {
  const mapping = await loadMapping();
  let result = { newCount: 0, viewCount: 0, composedCount: 0 };
  await wordRun(async (context) => {
    result = await renderKaeritenDocument(context, mapping);
    // Composed characters follow the font size too.
    result = { ...result, composedCount: await refreshComposedCharacters(context) };
  });
  return result;
}

export async function runUnrenderKaeriten() {
  const mapping = await loadMapping();
  let count = 0;
  await wordRun(async (context) => {
    count = await unrenderKaeritenDocument(context, mapping);
  });
  return count;
}

export async function runRefreshKaeriten() {
  return runRenderKaeriten();
}

async function copyPayload(buildPayload) {
  const mapping = await loadMapping();
  let payload;
  await wordRun(async (context) => {
    const result = await canonicalTextForExport(context, mapping);
    payload = buildPayload(result, mapping);
  });
  if (!payload || !String(payload).trim()) {
    throw new Error("Nothing to export in this scope.");
  }
  const clip = await writeClipboardText(payload);
  if (clip.copied) {
    return null;
  }
  return (
    "Automatic copy failed. The text is in the box below — click it, then press ⌘C."
  );
}

export function runCopyPlainText() {
  return copyPayload((result) => exportPlainText(result.text));
}

/** Insert SVG left by marinaMoji's character composer (clipboard). */
export function runComposedInsert() {
  return runInsertComposedCharacter();
}

/** Insert an SVG pasted into the pane (when it cannot read the clipboard itself). */
export function runComposedInsertFromText(svg) {
  return insertComposedSvgText(svg);
}

/** Dev spike: hard-coded ⿰言某 SVG (Api smoke test). */
export function runSvgSpike() {
  return runInsertComposedSvgSpike();
}
