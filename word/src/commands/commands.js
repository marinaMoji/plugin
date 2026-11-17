/* global Office */

import {
  runRenderKaeriten,
  runUnrenderKaeriten,
  runRefreshKaeriten,
  runCopyPlainText,
} from "../actions.js";

// Resolves once Office.js is up. Ribbon buttons can fire before that on Windows.
const officeReady = Office.onReady(() => {});

function notify(event, message) {
  if (message) console.warn("marinaMoji:", message);
  event.completed();
}

async function ribbonCall(event, fn) {
  try {
    await officeReady;
    await fn();
    notify(event);
  } catch (err) {
    console.error("marinaMoji:", err);
    notify(event, String(err));
  }
}

export async function renderKaeriten(event) {
  await ribbonCall(event, runRenderKaeriten);
}
export async function unrenderKaeriten(event) {
  await ribbonCall(event, runUnrenderKaeriten);
}
export async function refreshKaeriten(event) {
  await ribbonCall(event, runRenderKaeriten);
}
export async function copyPlainText(event) {
  await ribbonCall(event, runCopyPlainText);
}

globalThis.renderKaeriten = renderKaeriten;
globalThis.unrenderKaeriten = unrenderKaeriten;
globalThis.refreshKaeriten = refreshKaeriten;
globalThis.copyPlainText = copyPlainText;

// Word on Windows looks handlers up through Office.actions, not only globals.
try {
  const names = {
    renderKaeriten,
    unrenderKaeriten,
    refreshKaeriten,
    copyPlainText,
  };
  Office.onReady(() => {
    for (const [name, handler] of Object.entries(names)) {
      Office.actions.associate(name, handler);
    }
  });
} catch (err) {
  console.warn("marinaMoji: Office.actions.associate unavailable:", err);
}
