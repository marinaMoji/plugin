/**
 * Copy text to the system clipboard from the task pane / ribbon.
 * Word Mac often denies navigator.clipboard after await Word.run — use a visible
 * textarea in the task pane and execCommand while it is focused.
 */

const EXPORT_BOX_ID = "export-copy";

function getExportTextarea() {
  return document.getElementById(EXPORT_BOX_ID);
}

function focusTaskPane() {
  try {
    window.focus();
  } catch {
    /* optional */
  }
  try {
    document.body?.focus?.();
  } catch {
    /* optional */
  }
}

function tryExecCommandCopy(element) {
  if (!element) return false;
  try {
    element.focus();
    element.select();
    element.setSelectionRange?.(0, element.value.length);
    return document.execCommand("copy");
  } catch {
    return false;
  }
}

/**
 * @returns {{ copied: boolean, manual: boolean }}
 */
export async function writeClipboardText(text) {
  const payload = String(text ?? "");
  if (!payload) {
    throw new Error("Nothing to copy.");
  }

  focusTaskPane();

  const exportBox = getExportTextarea();
  if (exportBox) {
    exportBox.hidden = false;
    exportBox.value = payload;
    if (tryExecCommandCopy(exportBox)) {
      return { copied: true, manual: false };
    }
  }

  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(payload);
      return { copied: true, manual: false };
    } catch {
      /* fall through */
    }
  }

  const ta = document.createElement("textarea");
  ta.value = payload;
  ta.setAttribute("readonly", "");
  ta.style.position = "fixed";
  ta.style.left = "0";
  ta.style.top = "0";
  ta.style.width = "2em";
  ta.style.height = "2em";
  ta.style.opacity = "0.01";
  document.body.appendChild(ta);
  const ok = tryExecCommandCopy(ta);
  document.body.removeChild(ta);

  if (ok) {
    return { copied: true, manual: false };
  }

  if (exportBox) {
    exportBox.hidden = false;
    exportBox.focus();
    exportBox.select();
  }

  return { copied: false, manual: true };
}
