/* global Office, Word */

import { wordEnumsReady } from "./wordEnums.js";

const CATALOG_HINT =
  "Compléments shows a preview only — Word is not connected here. " +
  "Open a document, then Accueil → Kaeriten → Kaeriten pane (keep npm run serve running).";

const TIMEOUT_HINT =
  "Word did not connect. Run npm run serve, quit Word (Cmd+Q), reopen the pane from Accueil → Kaeriten.";

function hostConnected() {
  try {
    return !!(Office?.context?.host);
  } catch {
    return false;
  }
}

function wordApiAvailable() {
  return wordEnumsReady();
}

/**
 * Wait until Word has finished loading Office.js (onReady can be slow on Mac).
 */
export function whenOfficeReady(timeoutMs = 45000, { onSlow } = {}) {
  return new Promise((resolve, reject) => {
    if (typeof Office === "undefined") {
      reject(
        new Error(
          "Office.js did not load. Run npm run build, keep npm run serve running, restart Word."
        )
      );
      return;
    }

    if (hostConnected()) {
      resolve(Office.context);
      return;
    }

    let settled = false;
    const finish = (fn) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      clearInterval(poll);
      clearTimeout(catalogTimer);
      fn();
    };

    const catalogTimer = setTimeout(() => {
      if (!hostConnected() && !wordApiAvailable()) {
        onSlow?.(CATALOG_HINT);
      }
    }, 6000);

    const poll = setInterval(() => {
      if (hostConnected() || wordApiAvailable()) {
        finish(() => resolve(Office.context || {}));
      }
    }, 250);

    const onWindowReady = () => {
      if (hostConnected() || wordApiAvailable()) {
        finish(() => resolve(Office.context || {}));
      }
    };
    window.addEventListener("mm-office-ready", onWindowReady);

    const timer = setTimeout(() => {
      window.removeEventListener("mm-office-ready", onWindowReady);
      const msg =
        !hostConnected() && !wordApiAvailable()
          ? CATALOG_HINT
          : TIMEOUT_HINT;
      finish(() => reject(new Error(msg)));
    }, timeoutMs);

    try {
      const ready = Office.onReady((info) => {
        window.removeEventListener("mm-office-ready", onWindowReady);
        if (info.host && Office.HostType && info.host !== Office.HostType.Word) {
          finish(() => reject(new Error("Open this add-in from Microsoft Word.")));
          return;
        }
        finish(() => resolve(info));
      });
      if (ready && typeof ready.then === "function") {
        ready
          .then((info) => {
            window.removeEventListener("mm-office-ready", onWindowReady);
            if (
              info?.host &&
              Office.HostType &&
              info.host !== Office.HostType.Word
            ) {
              finish(() => reject(new Error("Open this add-in from Microsoft Word.")));
              return;
            }
            finish(() => resolve(info || Office.context || {}));
          })
          .catch(() => {
            /* callback path or poll will handle */
          });
      }
    } catch {
      /* poll / window event */
    }
  });
}
