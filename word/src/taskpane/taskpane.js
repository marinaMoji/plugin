/* global Office */

import {
  runRenderKaeriten,
  runUnrenderKaeriten,
  runCopyPlainText,
} from "../actions.js";
import { whenOfficeReady } from "../officeReady.js";
import {
  getCompoundTouch,
  setCompoundTouch,
} from "../wordRuntimeOpts.js";

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

function initUi() {
  showApp();
  wireCompoundTouch();
  wire(
    "btn-render",
    async () => {
      const { newCount, viewCount } = await runRenderKaeriten();
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
  setStatus("Connecting to Word…");
  whenOfficeReady(45000, {
    onSlow: (hint) => setStatus(hint, "err"),
  })
    .then(() => setStatus("Ready — select text and click Render.", "ok"))
    .catch((err) => setStatus(String(err.message || err), "err"));
  window.addEventListener("mm-office-ready", () => {
    whenOfficeReady(5000)
      .then(() => setStatus("Ready — select text and click Render.", "ok"))
      .catch(() => {});
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initUi);
} else {
  initUi();
}
