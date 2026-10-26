/* global Office, Word */

/**
 * Spike: insert an IDS-style SVG via Office.CoercionType.XmlSvg
 * (ImageCoercion 1.2). Not the production kaeriten path.
 *
 * Checks:
 *  - Is ImageCoercion 1.2 available?
 *  - Does insert succeed on Word Mac desktop?
 *  - Can we find the picture afterward and set alt text / read imageFormat?
 */

function escapeXml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * Schematic ⿰ (left–right) character: two components in one em-box.
 * This mirrors the composer’s layout idea without needing the Qt tool.
 */
export function buildIdsLeftRightSvg({
  left = "言",
  right = "某",
  ids = "⿰言某",
  sizePx = 200,
} = {}) {
  const leftX = 25;
  const rightX = 75;
  const baseline = 72;
  const fontSize = 52;
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${sizePx}" height="${sizePx}" ` +
    `viewBox="0 0 100 100" role="img" aria-label="${escapeXml(ids)}">` +
    `<title>${escapeXml(ids)}</title>` +
    `<rect x="0" y="0" width="100" height="100" fill="none"/>` +
    `<text x="${leftX}" y="${baseline}" font-size="${fontSize}" ` +
    `font-family="Hiragino Mincho ProN, Yu Mincho, Songti SC, serif" ` +
    `text-anchor="middle" dominant-baseline="alphabetic">${escapeXml(left)}</text>` +
    `<text x="${rightX}" y="${baseline}" font-size="${fontSize}" ` +
    `font-family="Hiragino Mincho ProN, Yu Mincho, Songti SC, serif" ` +
    `text-anchor="middle" dominant-baseline="alphabetic">${escapeXml(right)}</text>` +
    `</svg>`
  );
}

export function isXmlSvgSupported() {
  try {
    return !!(
      typeof Office !== "undefined" &&
      Office.context?.requirements?.isSetSupported &&
      Office.context.requirements.isSetSupported("ImageCoercion", "1.2") &&
      Office.CoercionType?.XmlSvg
    );
  } catch {
    return false;
  }
}

function setSelectedSvg(svgString, imageWidthPt) {
  return new Promise((resolve, reject) => {
    const opts = {
      coercionType: Office.CoercionType.XmlSvg,
    };
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

/**
 * Try to tag the picture we just inserted and report what Word stored.
 * Best-effort: finds the last inline picture in the selection's paragraph.
 */
async function inspectAndTagLastPicture(idsLabel) {
  const info = {
    found: false,
    imageFormat: null,
    altSet: false,
    width: null,
    height: null,
  };
  try {
    await Word.run(async (context) => {
      const sel = context.document.getSelection();
      const para = sel.paragraphs.getFirst();
      const paraPics = para.inlinePictures;
      paraPics.load("items");
      await context.sync();
      let items = paraPics.items;
      if (!items.length) {
        // Fall back: last picture in the body (spike docs are usually short).
        const bodyPics = context.document.body.inlinePictures;
        bodyPics.load("items");
        await context.sync();
        items = bodyPics.items;
      }
      if (!items.length) return;
      const pic = items[items.length - 1];
      pic.load(["width", "height", "altTextDescription", "altTextTitle"]);
      try {
        pic.load("imageFormat");
      } catch {
        /* WordApiDesktop only */
      }
      await context.sync();
      info.found = true;
      info.width = pic.width;
      info.height = pic.height;
      try {
        info.imageFormat = pic.imageFormat;
      } catch {
        info.imageFormat = "(unavailable)";
      }
      pic.altTextTitle = "marinaMoji composed character";
      pic.altTextDescription = `MARINAMOJI:ids=${idsLabel}`;
      await context.sync();
      info.altSet = true;
    });
  } catch (err) {
    info.error = String(err.message || err);
  }
  return info;
}

/**
 * Insert a sample ⿰言某 SVG at the caret. Returns a human-readable report.
 */
export async function runInsertComposedSvgSpike() {
  const ids = "⿰言某";
  const report = {
    imageCoercion12: isXmlSvgSupported(),
    platform: null,
    hostPt: null,
    inserted: false,
    inspect: null,
  };

  try {
    report.platform = Office.context?.platform || "(unknown)";
  } catch {
    report.platform = "(unknown)";
  }

  if (!report.imageCoercion12) {
    return (
      "Spike: ImageCoercion 1.2 / XmlSvg is not available on this Word host " +
      `(platform ${report.platform}). Word on the web usually lacks it; ` +
      "try Word for Mac/Windows desktop."
    );
  }

  const hostPt = await selectionFontSizePt();
  report.hostPt = hostPt;

  const svg = buildIdsLeftRightSvg({
    left: "言",
    right: "某",
    ids,
    sizePx: Math.max(64, Math.round(hostPt * 8)),
  });

  await setSelectedSvg(svg, hostPt);
  report.inserted = true;

  report.inspect = await inspectAndTagLastPicture(ids);

  const parts = [
    `Spike OK: inserted SVG (${ids}) at ~${hostPt} pt.`,
    `Platform: ${report.platform}.`,
  ];
  if (report.inspect?.found) {
    parts.push(
      `Picture found (${report.inspect.width}×${report.inspect.height} pt` +
        (report.inspect.imageFormat != null
          ? `, format=${report.inspect.imageFormat}`
          : "") +
        `).`
    );
    parts.push(
      report.inspect.altSet
        ? `Alt text set to MARINAMOJI:ids=${ids}.`
        : "Could not set alt text."
    );
  } else {
    parts.push(
      "Insert seemed to succeed, but no inline picture was found afterward " +
        "(Word may have wrapped it differently — check the document)."
    );
    if (report.inspect?.error) {
      parts.push(`Inspect error: ${report.inspect.error}`);
    }
  }
  parts.push(
    "Please check: sharp when zoomed? selectable? survives save/reopen?"
  );
  return parts.join(" ");
}
