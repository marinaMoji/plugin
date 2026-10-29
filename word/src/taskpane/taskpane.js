/* global Office, Word */

import {
  runRenderKaeriten,
  runUnrenderKaeriten,
  runCopyPlainText,
  runComposedInsert,
  runComposedInsertFromText,
  runEmphasisApply,
  runEmphasisRemove,
  runEmphasisSetDefault,
  getEmphasisDefaultStyle,
  listEmphasisStyles,
  runWarichuApply,
  runWarichuRemove,
  runTatechuyokoApply,
  runTatechuyokoRemove,
  runRubyApply,
  runRubyRemove,
  runJidoriApply,
  runJidoriRemove,
} from "../actions.js";
import { whenOfficeReady } from "../officeReady.js";
import {
  getCompoundTouch,
  setCompoundTouch,
} from "../wordRuntimeOpts.js";
import { fetchUpdateInfo, showUpdateBanner } from "../updateCheck.js";

const HELP_URL = "https://marinamoji.crcao.fr";

let statusFadeTimer = null;

function setStatus(text, kind) {
  const el = document.getElementById("status");
  if (!el) return;
  if (statusFadeTimer) {
    clearTimeout(statusFadeTimer);
    statusFadeTimer = null;
  }
  const msg = text || "Ready";
  el.textContent = msg;
  el.dataset.kind = kind || "";

  const hint = document.getElementById("launch-hint");
  if (hint) {
    const catalog =
      typeof msg === "string" &&
      (msg.includes("Compléments") || msg.includes("preview only"));
    hint.hidden = !catalog;
  }

  if (kind === "ok" && msg !== "Ready" && !msg.startsWith("Ready")) {
    statusFadeTimer = setTimeout(() => {
      if (el.textContent === msg) {
        el.textContent = "Ready";
        el.dataset.kind = "";
      }
    }, 4500);
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
    setStatus("Working…");
    try {
      await whenOfficeReady();
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
      if (id === "btn-render" || id === "btn-unrender") {
        refreshScopeIndicator();
      }
    } catch (err) {
      const msg = String((err && err.message) || err);
      if (msg === "Cancelled.") {
        setStatus("Cancelled.", "ok");
      } else {
        console.error("marinaMoji:", err);
        setStatus(msg, "err");
      }
    } finally {
      btn.disabled = false;
    }
  });
}

function wireHelpPops() {
  document.querySelectorAll(".info-btn[data-help]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("aria-controls");
      const panel = id && document.getElementById(id);
      if (!panel) return;
      const open = panel.hidden;
      document.querySelectorAll(".help-pop").forEach((p) => {
        p.hidden = true;
      });
      document.querySelectorAll(".info-btn").forEach((b) => {
        b.setAttribute("aria-expanded", "false");
      });
      if (open) {
        panel.hidden = false;
        btn.setAttribute("aria-expanded", "true");
      }
    });
  });

  const helpBtn = document.getElementById("btn-help");
  if (helpBtn) {
    helpBtn.addEventListener("click", () => {
      try {
        window.open(HELP_URL, "_blank", "noopener,noreferrer");
      } catch {
        setStatus(`Open ${HELP_URL} in a browser.`, "warn");
      }
    });
  }
}

async function refreshScopeIndicator() {
  const el = document.getElementById("scope-indicator");
  if (!el) return;
  try {
    await whenOfficeReady(3000);
    if (typeof Word === "undefined" || !Word.run) {
      el.textContent = "Scope: —";
      return;
    }
    await Word.run(async (context) => {
      const selection = context.document.getSelection();
      selection.load("text");
      await context.sync();
      const t = (selection.text || "").trim();
      if (!t) {
        el.textContent = "Scope: entire document";
      } else {
        const preview =
          t.length > 24 ? `${[...t].slice(0, 24).join("")}…` : t;
        el.textContent = `Scope: selection (${preview})`;
      }
    });
  } catch {
    el.textContent = "Scope: selection or entire document";
  }
}

function wireSelectionChanged() {
  try {
    if (
      typeof Office !== "undefined" &&
      Office.context &&
      Office.context.document &&
      Office.EventType &&
      Office.EventType.DocumentSelectionChanged
    ) {
      Office.context.document.addHandlerAsync(
        Office.EventType.DocumentSelectionChanged,
        () => refreshScopeIndicator()
      );
    }
  } catch {
    /* optional */
  }
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

function fillEmphasisStyleSelect() {
  const select = document.getElementById("opt-emphasis-style");
  if (!select) return;
  const opts = listEmphasisStyles("en");
  const current = getEmphasisDefaultStyle();
  select.innerHTML = "";
  for (const row of opts) {
    const opt = document.createElement("option");
    opt.value = row.id;
    opt.textContent = row.label;
    if (row.id === current) opt.selected = true;
    select.appendChild(opt);
  }
}

function wireAll() {
  wireCompoundTouch();
  fillEmphasisStyleSelect();

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
          ? "Formatted 1 kaeriten group."
          : `Formatted ${newCount} kaeriten groups.`;
      }
      if (viewCount > 0) return "Updated kaeriten views in scope.";
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

  wire("btn-warichu-apply", runWarichuApply, null);
  wire("btn-warichu-remove", runWarichuRemove, null);
  wire("btn-tate-apply", () => runTatechuyokoApply(), null);
  wire("btn-tate-remove", runTatechuyokoRemove, null);

  wire(
    "btn-emphasis-apply",
    async () => {
      const styleSelect = document.getElementById("opt-emphasis-style");
      const styleId = styleSelect
        ? styleSelect.value
        : getEmphasisDefaultStyle();
      return runEmphasisApply(styleId);
    },
    null
  );
  wire("btn-emphasis-remove", runEmphasisRemove, null);

  const defBtn = document.getElementById("btn-emphasis-default");
  if (defBtn) {
    defBtn.addEventListener("click", async () => {
      defBtn.disabled = true;
      try {
        await whenOfficeReady();
        const styleSelect = document.getElementById("opt-emphasis-style");
        const styleId = styleSelect
          ? styleSelect.value
          : getEmphasisDefaultStyle();
        setStatus(await runEmphasisSetDefault(styleId), "ok");
      } catch (err) {
        setStatus(String((err && err.message) || err), "err");
      } finally {
        defBtn.disabled = false;
      }
    });
  }

  wire(
    "btn-ruby-apply",
    async () => {
      const input = document.getElementById("opt-ruby-reading");
      return runRubyApply(input ? input.value : "");
    },
    null
  );
  wire("btn-ruby-remove", runRubyRemove, null);

  wire(
    "btn-jidori-apply",
    async () => {
      const input = document.getElementById("opt-jidori-n");
      return runJidoriApply(input ? Number(input.value) : 5);
    },
    null
  );
  wire("btn-jidori-remove", runJidoriRemove, null);

  wire("btn-plain", runCopyPlainText, "Copied plain text.");
  wire("btn-composed-insert", runComposedInsert, null);

  const pasteBox = document.getElementById("composed-paste");
  if (pasteBox) {
    pasteBox.addEventListener("paste", async (event) => {
      const text =
        event.clipboardData && event.clipboardData.getData("text/plain");
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
}

function checkUpdatesQuietly() {
  fetchUpdateInfo()
    .then((info) => {
      if (!info || !info.show) return;
      showUpdateBanner(document.getElementById("app"), info);
    })
    .catch(() => {});
}

function onReady() {
  fillEmphasisStyleSelect();
  refreshScopeIndicator();
  wireSelectionChanged();
  setStatus("Ready", "ok");
  checkUpdatesQuietly();
}

function initUi() {
  showApp();
  wireHelpPops();
  wireAll();
  setStatus("Connecting to Word…");
  whenOfficeReady(45000, {
    onSlow: (hint) => setStatus(hint, "err"),
  })
    .then(onReady)
    .catch((err) => setStatus(String(err.message || err), "err"));
  window.addEventListener("mm-office-ready", () => {
    whenOfficeReady(5000).then(onReady).catch(() => {});
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initUi);
} else {
  initUi();
}
