/** Task-pane preferences (localStorage; not in mapping.json). */

const COMPOUND_TOUCH_KEY = "marinaMoji.compoundTouch";

export function getCompoundTouch() {
  try {
    return localStorage.getItem(COMPOUND_TOUCH_KEY) === "1";
  } catch {
    return false;
  }
}

export function setCompoundTouch(enabled) {
  try {
    localStorage.setItem(COMPOUND_TOUCH_KEY, enabled ? "1" : "0");
  } catch {
    /* private mode */
  }
}
