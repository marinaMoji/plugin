/* global Office, Word */

/**
 * Insert a composed-character SVG produced by marinaMoji's character composer.
 *
 * Flow:
 *  1. User opens the character composer from the marinaMoji toolbar.
 *  2. Builds an unencoded structure and clicks Insert (SVG → clipboard).
 *  3. This button reads the clipboard and inserts via XmlSvg (desktop Word).
 */

import { isXmlSvgSupported } from "./wordSvgSpike.js";

function looksLikeSvg(text) {
  if (!text || typeof text !== "string") return false;
  const t = text.trim();
  return t.startsWith("<svg") || t.includes("<svg");
}

async function readSvgFromClipboard() {
  // Prefer the MIME type the Qt composer sets.
  try {
    if (navigator.clipboard?.read) {
      const items = await navigator.clipboard.read();
      for (const item of items) {
        if (item.types.includes("image/svg+xml")) {
          const blob = await item.getType("image/svg+xml");
          const text = await blob.text();
          if (looksLikeSvg(text)) return text;
        }
      }
    }
  } catch (err) {
    console.warn("marinaMoji: clipboard.read failed", err);
  }
  try {
    if (navigator.clipboard?.readText) {
      const text = await navigator.clipboard.readText();
      if (looksLikeSvg(text)) return text.trim();
    }
  } catch (err) {
    console.warn("marinaMoji: clipboard.readText failed", err);
  }
  return null;
}

async function selectionFontSizePt() {
  let size = 12;
  await Word.run(async (context) => {
    const sel = context.document.getSelection();
    sel.font.load("size");
    await context.sync();
    if (Number.isFinite(sel.font.size) && sel.font.size > 0) {
      size = sel.font.size;
    }
  });
  return size;
}

function setSelectedSvg(svgString, imageWidthPt) {
  return new Promise((resolve, reject) => {
    const opts = { coercionType: Office.CoercionType.XmlSvg };
    if (Number.isFinite(imageWidthPt) && imageWidthPt > 0) {
      opts.imageWidth = imageWidthPt;
      opts.imageHeight = imageWidthPt;
    }
    Office.context.document.setSelectedDataAsync(svgString, opts, (result) => {
      if (result.status === Office.AsyncResultStatus.Succeeded) {
        resolve(result);
      } else {
        const err = result.error || {};
        reject(
          new Error(
            err.message ||
              `XmlSvg insert failed (${err.code || result.status || "unknown"})`
          )
        );
      }
    });
  });
}

function idsFromSvg(svg) {
  const m = /aria-label="([^"]+)"/.exec(svg) || /<title>([^<]+)<\/title>/.exec(svg);
  return m ? m[1] : "composed";
}

async function tagLastPicture(idsLabel) {
  try {
    await Word.run(async (context) => {
      const sel = context.document.getSelection();
      const para = sel.paragraphs.getFirst();
      const paraPics = para.inlinePictures;
      paraPics.load("items");
      await context.sync();
      let items = paraPics.items;
      if (!items.length) {
        const bodyPics = context.document.body.inlinePictures;
        bodyPics.load("items");
        await context.sync();
        items = bodyPics.items;
      }
      if (!items.length) return;
      const pic = items[items.length - 1];
      pic.altTextTitle = "marinaMoji composed character";
      pic.altTextDescription = `MARINAMOJI:ids=${idsLabel}`;
      await context.sync();
    });
  } catch (err) {
    console.warn("marinaMoji: could not set alt text", err);
  }
}

/**
 * Insert clipboard SVG from the character composer at the caret.
 */
export async function runInsertComposedCharacter() {
  if (!isXmlSvgSupported()) {
    return (
      "Composed SVG needs Word desktop (ImageCoercion 1.2). " +
      "Word on the web cannot insert SVG this way."
    );
  }

  const svg = await readSvgFromClipboard();
  if (!svg) {
    return (
      "No composed drawing on the clipboard. Open the marinaMoji character " +
      "composer from the toolbar, build a character with no Unicode match, " +
      "click Insert, then click this button again."
    );
  }

  const hostPt = await selectionFontSizePt();
  await setSelectedSvg(svg, hostPt);
  const ids = idsFromSvg(svg);
  await tagLastPicture(ids);
  return `Inserted composed character (${ids}) at ~${hostPt} pt.`;
}
