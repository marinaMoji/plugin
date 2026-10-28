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
import { W } from "./wordEnums.js";

export const COMPOSED_TITLE = "marinaMoji composed character";
const COMPOSED_TAG = "MARINAMOJI:ids=";

/**
 * Is this one of ours? The add-in titles its pictures; the composer, which
 * inserts straight into Word through AppleScript, can only set the alternative
 * text, so that carries the tag too.
 */
export function isComposedPicture(pic) {
  return (
    pic.altTextTitle === COMPOSED_TITLE ||
    String(pic.altTextDescription || "").includes(COMPOSED_TAG)
  );
}

// The drawing fills its square; a font's ink is a little smaller and hangs a
// little below the baseline. Same values as the ONLYOFFICE plugin, measured
// against Arial/Mincho text there.
export const INK_SCALE = 1.0;
export const DROP_EM = 0.19;

/** Picture size (pt, square) and Font.position (pt) for text of |hostPt|. */
export function composedMetrics(hostPt) {
  return { sizePt: hostPt * INK_SCALE, shiftPt: -hostPt * DROP_EM };
}

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

async function tagInsertedPicture(idsLabel, hostPt) {
  try {
    await Word.run(async (context) => {
      const sel = context.document.getSelection();
      const selPics = sel.inlinePictures;
      selPics.load("items");
      await context.sync();
      let items = selPics.items;
      if (!items.length) {
        const paraPics = sel.paragraphs.getFirst().inlinePictures;
        paraPics.load("items");
        await context.sync();
        items = paraPics.items;
      }
      if (!items.length) {
        const bodyPics = context.document.body.inlinePictures;
        bodyPics.load("items");
        await context.sync();
        items = bodyPics.items;
      }
      if (!items.length) return;
      const pic = items[items.length - 1];
      pic.altTextTitle = COMPOSED_TITLE;
      pic.altTextDescription = `MARINAMOJI:ids=${idsLabel}`;
      await context.sync();
      try {
        // XmlSvg's imageWidth/Height are not reliably points (the picture came
        // out at 75%), so set the size in points here.
        const { sizePt, shiftPt } = composedMetrics(hostPt);
        pic.load("width,height");
        await context.sync();
        const aspect = pic.height > 0 ? pic.width / pic.height : 1;
        pic.lockAspectRatio = false;
        pic.height = sizePt;
        pic.width = sizePt * aspect;
        pic.getRange(W.rangeWhole()).font.position = shiftPt;
        await context.sync();
      } catch (err) {
        console.warn("marinaMoji: could not set baseline position", err);
      }
    });
  } catch (err) {
    console.warn("marinaMoji: could not tag the composed picture", err);
  }
}

/**
 * Resize every composed-character picture to the font size of the text it sits
 * in (aspect kept) and re-apply its baseline position. Returns how many changed.
 */
export async function refreshComposedCharacters(context) {
  const bodies = [context.document.body];
  try {
    const sections = context.document.sections;
    sections.load("items");
    await context.sync();
    for (const section of sections.items) {
      for (const kind of ["Primary", "FirstPage", "EvenPages"]) {
        bodies.push(section.getHeader(kind), section.getFooter(kind));
      }
    }
  } catch {
    /* headers and footers are optional on some hosts */
  }
  try {
    const notes = [
      context.document.body.footnotes,
      context.document.body.endnotes,
    ];
    notes.forEach((n) => n.load("items"));
    await context.sync();
    for (const list of notes) for (const note of list.items) bodies.push(note.body);
  } catch {
    /* footnotes need WordApi 1.5 */
  }

  const lists = bodies.map((body) => {
    const pics = body.inlinePictures;
    pics.load("items/altTextTitle,items/altTextDescription,items/width,items/height");
    return pics;
  });
  try {
    await context.sync();
  } catch {
    return refreshInBody(context, context.document.body);
  }
  const mine = [];
  for (const pics of lists) {
    for (const p of pics.items) if (isComposedPicture(p)) mine.push(p);
  }
  return resizeComposed(context, mine);
}

async function refreshInBody(context, body) {
  const pics = body.inlinePictures;
  pics.load("items/altTextTitle,items/altTextDescription,items/width,items/height");
  await context.sync();
  return resizeComposed(context, pics.items.filter(isComposedPicture));
}

async function resizeComposed(context, mine) {
  if (!mine.length) return 0;
  const ranges = mine.map((p) => {
    const r = p.getRange(W.rangeWhole());
    r.font.load("size,position");
    return r;
  });
  await context.sync();
  let count = 0;
  mine.forEach((pic, i) => {
    const hostPt = ranges[i].font.size;
    if (!Number.isFinite(hostPt) || hostPt <= 0 || !pic.height) return;
    const { sizePt, shiftPt } = composedMetrics(hostPt);
    const aspect = pic.width / pic.height;
    const same =
      Math.abs(pic.height - sizePt) < 0.1 &&
      Math.abs(ranges[i].font.position - shiftPt) < 0.1;
    if (same) return;
    pic.lockAspectRatio = false;
    pic.height = sizePt;
    pic.width = sizePt * aspect;
    ranges[i].font.position = shiftPt;
    count++;
  });
  await context.sync();
  return count;
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
      "Word did not let the pane read the clipboard. Press ⌘V in the paste " +
      "box below (after clicking Insert in the composer)."
    );
  }
  return insertComposedSvgText(svg);
}

/** Insert |svg| (text) at the caret; used by the button and by the paste box. */
export async function insertComposedSvgText(svg) {
  if (!looksLikeSvg(svg)) {
    return "That is not a composed drawing. Click Insert in the character composer, then paste.";
  }
  svg = svg.trim();
  const hostPt = await selectionFontSizePt();
  await setSelectedSvg(svg, composedMetrics(hostPt).sizePt);
  const ids = idsFromSvg(svg);
  await tagInsertedPicture(ids, hostPt);
  return `Inserted composed character (${ids}) at ~${hostPt} pt.`;
}
