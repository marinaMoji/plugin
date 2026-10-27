/* global Office */

import {
  runRenderKaeriten,
  runUnrenderKaeriten,
  runCopyPlainText,
  runComposedInsert,
  runComposedInsertFromText,
  runSvgSpike,
} from "../actions.js";
import { whenOfficeReady } from "../officeReady.js";
import {
  getCompoundTouch,
  setCompoundTouch,
} from "../wordRuntimeOpts.js";
import { fetchUpdateInfo, showUpdateBanner } from "../updateCheck.js";

function setStatus(text, kind) {
  const el = document.getElementById("status");
  if (!el) return;
  el.textContent = text || "";
  el.className = "status" + (kind ? " " + kind : "");
  const hint = document.getElementById("launch-hint");
  if (hint) {
    const catalog =
      typeof text === "string" &&
      (text.includes("Compléments") || text.includes("preview only"));
    hint.hidden = !catalog;
  }
}

function showApp() {
  const boot = document.getElementById("boot");
  const app = document.getElementById("app");
  if (boot) boot.hidden = true;
  if (app) app.hidden = false;
}

function wire(id, fn, doneMsg) {
  const btn = document.getElementById(id);
  if (!btn) return;
  btn.addEventListener("click", async () => {
    try {
      window.focus();
    } catch {
      /* optional */
    }
    btn.disabled = true;
    setStatus("Connecting to Word…");
    try {
      await whenOfficeReady();
      setStatus("Working…");
      const result = await fn();
      const msg =
        (typeof result === "string" && result) || doneMsg || "Done.";
      setStatus(msg, "ok");
      if (msg.includes("paste box")) {
        const paste = document.getElementById("composed-paste");
        if (paste) {
          paste.hidden = false;
          paste.value = "";
          paste.focus();
        }
      }
      if (msg.includes("box below")) {
        const box = document.getElementById("export-copy");
        if (box && !box.hidden) {
          box.focus();
          box.select();
        }
      }
    } catch (err) {
      console.error("marinaMoji:", err);
      setStatus(String(err.message || err), "err");
    } finally {
      btn.disabled = false;
    }
  });
}

function wireCompoundTouch() {
  const box = document.getElementById("opt-compound-touch");
  if (!box) return;
  box.checked = getCompoundTouch();
  box.addEventListener("change", () => {
    setCompoundTouch(box.checked);
    setStatus(
      box.checked
        ? "Compound marks will touch on next Render."
        : "Normal compound spacing on next Render.",
      "ok"
    );
  });
}

function checkUpdatesQuietly() {
  fetchUpdateInfo()
    .then((info) => {
      if (!info || !info.show) return;
      showUpdateBanner(document.getElementById("app"), info);
    })
    .catch(() => {});
}

function initUi() {
  showApp();
  wireCompoundTouch();
  wire(
    "btn-render",
    async () => {
      const { newCount, viewCount, composedCount } = await runRenderKaeriten();
      if (composedCount > 0 && newCount === 0 && viewCount === 0) {
        return composedCount === 1
          ? "Resized 1 composed character."
          : `Resized ${composedCount} composed characters.`;
      }
      if (newCount > 0) {
        return newCount === 1
          ? "Formatted 1 kaeriten group (beside kanji)."
          : `Formatted ${newCount} kaeriten groups (beside kanji).`;
      }
      if (viewCount > 0) {
        return "Updated kaeriten views in scope.";
      }
      return "Done.";
    },
    null
  );
  wire(
    "btn-unrender",
    async () => {
      const n = await runUnrenderKaeriten();
      return n === 1
        ? "Restored 1 kaeriten view."
        : `Restored ${n} kaeriten views.`;
    },
    null
  );
  wire("btn-plain", runCopyPlainText, "Copied plain text.");
  wire("btn-composed-insert", runComposedInsert, null);
  const pasteBox = document.getElementById("composed-paste");
  if (pasteBox) {
    pasteBox.addEventListener("paste", async (event) => {
      const text = event.clipboardData && event.clipboardData.getData("text/plain");
      event.preventDefault();
      try {
        await whenOfficeReady();
        const msg = await runComposedInsertFromText(text || "");
        setStatus(msg, msg.startsWith("Inserted") ? "ok" : "err");
        if (msg.startsWith("Inserted")) pasteBox.hidden = true;
      } catch (err) {
        setStatus(String((err && err.message) || err), "err");
      }
    });
  }
  wire("btn-svg-spike", runSvgSpike, null);
  setStatus("Connecting to Word…");
  whenOfficeReady(45000, {
    onSlow: (hint) => setStatus(hint, "err"),
  })
    .then(() => {
      setStatus("Ready — select text and click Render.", "ok");
      checkUpdatesQuietly();
    })
    .catch((err) => setStatus(String(err.message || err), "err"));
  window.addEventListener("mm-office-ready", () => {
    whenOfficeReady(5000)
      .then(() => {
        setStatus("Ready — select text and click Render.", "ok");
        checkUpdatesQuietly();
      })
      .catch(() => {});
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initUi);
} else {
  initUi();
}
