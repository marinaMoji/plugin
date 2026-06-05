/* global Office */

import {
  runRenderKaeriten,
  runUnrenderKaeriten,
  runRefreshKaeriten,
  runCopyPlainText,
} from "../actions.js";

Office.onReady(() => {});

function notify(event, message) {
  if (message) console.warn("marinaMoji:", message);
  event.completed();
}

async function ribbonCall(event, fn) {
  try {
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
  await ribbonCall(event, runRefreshKaeriten);
}
export async function copyPlainText(event) {
  await ribbonCall(event, runCopyPlainText);
}

globalThis.renderKaeriten = renderKaeriten;
globalThis.unrenderKaeriten = unrenderKaeriten;
globalThis.refreshKaeriten = refreshKaeriten;
globalThis.copyPlainText = copyPlainText;
