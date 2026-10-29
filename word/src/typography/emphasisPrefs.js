/**
 * Document default for Apply emphasis.
 * Stored in Office document settings (survives save in desktop Word).
 */

import {
  EMPHASIS_BUILTIN_DEFAULT,
  normalizeEmphasisStyleId,
  resolveEmphasisDefault,
} from "./emphasisStyles.js";

export const PROP_EMPHASIS_DEFAULT = "marinaMoji.Typography.EmphasisDefault";

function settingsApi() {
  try {
    return Office?.context?.document?.settings || null;
  } catch {
    return null;
  }
}

function saveSettings() {
  const settings = settingsApi();
  if (!settings || typeof settings.saveAsync !== "function") {
    return Promise.resolve();
  }
  return new Promise((resolve, reject) => {
    settings.saveAsync((result) => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        resolve();
      } else {
        reject(
          new Error(
            (result.error && result.error.message) ||
              "Could not save document settings."
          )
        );
      }
    });
  });
}

export function getRawEmphasisDefault() {
  const settings = settingsApi();
  if (!settings || typeof settings.get !== "function") return null;
  try {
    const v = settings.get(PROP_EMPHASIS_DEFAULT);
    return v == null || v === "" ? null : String(v);
  } catch {
    return null;
  }
}

export function getEmphasisDefault() {
  return resolveEmphasisDefault(getRawEmphasisDefault());
}

export async function setEmphasisDefault(styleId) {
  const normalized = normalizeEmphasisStyleId(styleId);
  if (!normalized) {
    throw new Error("Unsupported emphasis style.");
  }
  const settings = settingsApi();
  if (!settings || typeof settings.set !== "function") {
    throw new Error("Document settings are not available in this host.");
  }
  settings.set(PROP_EMPHASIS_DEFAULT, normalized);
  await saveSettings();
  return normalized;
}

export { EMPHASIS_BUILTIN_DEFAULT };
