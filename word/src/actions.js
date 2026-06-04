/* global Word */

import { wordEnumsReady } from "./wordEnums.js";
import {
  exportPlainText,
  exportTeiForClipboard,
  exportLatexForClipboard,
} from "./exportCore.js";
import {
  loadMapping,
  renderKaeritenDocument,
  unrenderKaeritenDocument,
  refreshKaeritenDocument,
  canonicalTextForExport,
} from "./render.js";
import { writeClipboardText } from "./clipboard.js";

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
  let count = 0;
  await wordRun(async (context) => {
    count = await renderKaeritenDocument(context, mapping);
  });
  return count;
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
  const mapping = await loadMapping();
  await wordRun(async (context) => {
    await refreshKaeritenDocument(context, mapping);
  });
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

export function runCopyTei() {
  return copyPayload((result) =>
    exportTeiForClipboard(result.text, false)
  );
}

export function runCopyLatex() {
  return copyPayload((result, mapping) =>
    exportLatexForClipboard(result.text, mapping, false)
  );
}
