/**
 * Word renderer: canonical Unicode → locked content controls (kaeriten view).
 * Tag stores source marks: MARINAMOJI:source=…
 */

import {
  findClusters,
  glyphsForMarks,
  mappingByChar,
  buildCanonicalPlainText,
  buildDisplayToMarksMap,
  findOrphanViewClusters,
  normalizeDisplayKey,
  resolveMarksFromControl,
  bookmarkNameForMarks,
  bookmarkNameForViewId,
  nextKaeritenViewId,
  marksFromBookmarkName,
  isViewIdBookmarkName,
  SOURCE_PREFIX,
} from "./exportCore.js";
import { W } from "./wordEnums.js";
import {
  wordHasTextBoxApi,
  insertKaeritenInlineTextBox,
  insertKaeritenTextBox,
  listMarinaMojiTextBoxes,
  unrenderOneTextBox,
  deleteShapeIfMarksPresent,
  recoverMarksAfterBase,
  emergencyRestoreMarks,
  refreshKaeritenTextBox,
  isMarinaMojiTextBox,
  marksFromShape,
  viewKeyForShape,
  shapeOverlapsWorkRange,
  tagInlineShapeAfterBase,
} from "./wordTextBox.js";
import { isWordMac } from "./wordHost.js";
import { isVerticalFlow } from "./wordLayout.js";
import {
  insertPointAfterBase,
  marksRangeAfterBase,
  marksRangeInCluster,
  baseRangeAtClusterStart,
  baseKanjiAdjacentBefore,
  baseCharRangeBeforeView,
  findBaseRangeForView,
  baseOffsetInWorkRange,
  findOrphanViewInWorkRange,
} from "./wordRange.js";
import { resolveBaseBeforeShape } from "./wordTextBox.js";
import {
  resolveBaselineShiftPt,
  parseFontSizeRatio,
} from "./wordBoxLayout.js";
import {
  wordHasOoxmlApi,
  buildClusterReplaceOoxmlVariants,
} from "./wordOoxml.js";
import {
  sanityCheckOoxml,
  probeOoxmlWithWord,
  ooxmlErrorDetail,
} from "./wordOoxmlProbe.js";

export { SOURCE_PREFIX };

const PLACEHOLDER_TEXT =
  /^(Cliquez ou appuyez ici pour entrer du texte\.?|Click or tap here to enter text\.?|Appuyez sur Ctrl\+Entrée.*)$/i;

let _mappingCache = null;

function isPlaceholderText(text) {
  return PLACEHOLDER_TEXT.test((text || "").trim());
}

export function loadMapping() {
  if (_mappingCache) return Promise.resolve(_mappingCache);
  const base =
    typeof document !== "undefined" && document.currentScript?.src
      ? document.currentScript.src
      : typeof window !== "undefined"
        ? window.location.href
        : "";
  const url = new URL("mapping.json", base || "https://localhost:3000/");
  return fetch(url).then((r) => {
    if (!r.ok) throw new Error("mapping.json not found");
    return r.json().then((data) => {
      _mappingCache = data;
      return data;
    });
  });
}

function wordRenderOptions(mappingData) {
  const r = mappingData?.rendering || {};
  const cc = r.word_content_control || {};
  const inline = r.word_inline_textbox || {};
  const lo = r.libreoffice_frame || {};
  const primary = (r.word_primary || "content_control").toLowerCase();
  const useOoxml =
    primary === "ooxml" ||
    primary === "inline_ooxml" ||
    (isWordMac() && r.word_mac_use_ooxml === true);
  const preferInlineOnMac =
    !useOoxml && r.word_mac_prefer_inline_textbox !== false;
  let useInlineTextBox =
    primary === "inline_textbox" ||
    primary === "inline_text_box" ||
    primary === "inline";
  const useTextBox = primary === "textbox" || primary === "text_box";
  if (
    !useInlineTextBox &&
    !useTextBox &&
    preferInlineOnMac &&
    isWordMac() &&
    wordHasTextBoxApi()
  ) {
    useInlineTextBox = true;
  }
  const box = useInlineTextBox ? { ...cc, ...inline } : cc;
  const marginAll = Number(box.margin_pt ?? lo.margin_pt ?? 0);
  const contentAlign = String(
    box.content_align ?? lo.content_align ?? "bottom"
  ).toLowerCase();
  const contentAlignHorizontal = String(
    box.content_align_horizontal ?? lo.content_align_horizontal ?? "center"
  ).toLowerCase();
  return {
    fontSizeRatio: parseFontSizeRatio(
      box.font_size_ratio ?? lo.font_size_ratio ?? "12:5"
    ),
    minFontSizePt: Number(box.min_font_size_pt ?? 6),
    useOoxml,
    useInlineTextBox,
    useTextBox,
    preferInlineOnMac,
    textFrameVerticalAlign: contentAlign,
    textFrameHorizontalAlign: contentAlignHorizontal,
    textFrameMarginTop: Number(box.margin_top_pt ?? lo.margin_top_pt ?? marginAll),
    textFrameMarginBottom: Number(
      box.margin_bottom_pt ?? lo.margin_bottom_pt ?? marginAll
    ),
    textFrameMarginLeft: Number(
      box.margin_left_pt ?? lo.margin_left_pt ?? marginAll
    ),
    textFrameMarginRight: Number(
      box.margin_right_pt ?? lo.margin_right_pt ?? marginAll
    ),
    macCompoundRow:
      String(
        box.word_mac_compound_layout ?? lo.word_mac_compound_layout ?? "stack"
      ).toLowerCase() === "row",
    ooxmlFallbackApi: r.word_mac_ooxml_fallback_api !== false,
    compoundLineSpacingPt:
      inline.compound_line_spacing_pt != null
        ? Number(inline.compound_line_spacing_pt)
        : null,
    compoundLineSpacingMultiple: Number(
      inline.compound_line_spacing_multiple ?? 0.82
    ),
    compoundBoxHeightPerMark: Number(
      inline.compound_box_height_per_mark ?? 0.88
    ),
    compoundBoxPaddingPt: Number(inline.compound_box_padding_pt ?? 0.12),
    frameWidthHmm: Number(inline.frame_width_hmm ?? lo.frame_width_hmm ?? 180),
    frameWidthReferencePt: Number(
      inline.frame_width_reference_pt ?? lo.frame_width_reference_pt ?? 12
    ),
    frameHeightPaddingHmm: Number(
      inline.frame_height_padding_hmm ?? lo.frame_height_padding_hmm ?? 80
    ),
    ooxmlProbeWithWord: r.word_mac_ooxml_probe_with_word !== false,
    boxWidthPt:
      inline.box_width_pt != null ? Number(inline.box_width_pt) : null,
    boxWidthEm:
      inline.box_width_em != null ? Number(inline.box_width_em) : null,
    baselineShiftPt: resolveBaselineShiftPt(inline),
    inlineEffectExtentPt: Number(inline.inline_effect_extent_pt ?? 0),
    boxExtraWidthRightPt:
      inline.box_extra_width_right_pt != null
        ? Number(inline.box_extra_width_right_pt)
        : 0,
    macForceSolidFill:
      r.word_mac_force_solid_fill === true ||
      inline.word_mac_force_solid_fill === true,
    macFillColor: String(
      inline.word_mac_fill_color ?? r.word_mac_fill_color ?? "FFFFFF"
    ),
    macNoOutline:
      r.word_mac_no_outline !== false && inline.word_mac_no_outline !== false,
  };
}

function selectionHasKaeritenMarks(text) {
  return /[\u3190-\u319f]/.test(text || "");
}

export async function getWorkRange(context) {
  const selection = context.document.getSelection();
  selection.load("text");
  await context.sync();
  if (selection.text && selection.text.length > 0) {
    if (isPlaceholderText(selection.text)) {
      throw new Error(
        "The grey placeholder is selected. Click in the document, type 說㆒㆑者 with marinaMoji, select it, then Render."
      );
    }
    return selection.getRange();
  }
  return context.document.body.getRange();
}

/** Render/Unrender scope: selection must include marks (avoids silent whole-document scans). */
/** Unrender scope: need a selection (do not scan the whole document). */
export async function getWorkRangeForUnrender(context) {
  const selection = context.document.getSelection();
  selection.load("text");
  await context.sync();
  const selText = selection.text || "";
  if (!selText.trim()) {
    throw new Error(
      "Select the formatted kaeriten (e.g. 漢 with a small レ beside it), then Unrender."
    );
  }
  if (isPlaceholderText(selText)) {
    throw new Error(
      "The grey placeholder is selected. Select your document text with rendered kaeriten, then Unrender."
    );
  }
  return selection.getRange();
}

export async function getWorkRangeForRender(context) {
  const selection = context.document.getSelection();
  selection.load("text");
  await context.sync();
  const selText = selection.text || "";
  if (!selText.trim() || !selectionHasKaeritenMarks(selText)) {
    throw new Error(
      "Select the text that contains kaeriten marks (e.g. 漢㆒㆑字), then Render. " +
        "A cursor on an empty line is not enough."
    );
  }
  if (isPlaceholderText(selText)) {
    throw new Error(
      "The grey placeholder is selected. Type 說㆒㆑者 with marinaMoji, select it, then Render."
    );
  }
  return selection.getRange();
}

export function selectionIsEmpty(context) {
  const selection = context.document.getSelection();
  selection.load("text");
  return context.sync().then(() => !selection.text || selection.text.length === 0);
}

/**
 * Delete the marks run inside a verified cluster (search/expandTo only), then insert view at gap.
 * Returns false if any mark codepoints remain in the cluster text.
 */
async function deleteMarksFromCluster(context, clusterRange, baseChar, marks) {
  const baseRange = await baseRangeAtClusterStart(
    context,
    clusterRange,
    baseChar
  );
  if (!baseRange) return false;
  let marksRange = await marksRangeInCluster(
    context,
    baseRange,
    clusterRange,
    marks
  );
  if (!marksRange) {
    marksRange = await marksRangeAfterBase(
      context,
      baseRange,
      marks,
      clusterRange
    );
  }
  if (!marksRange) return false;
  marksRange.delete();
  await context.sync();
  clusterRange.load("text");
  await context.sync();
  return !clusterStillHasMarks(clusterRange.text);
}

function clusterStillHasMarks(text) {
  return /[\u3190-\u319f]/.test(normalizeClusterText(text));
}

function viewFontLooksLikeKaeriten(viewPt, basePt, ratio, minPt) {
  if (!viewPt || viewPt <= 0) return true;
  if (!basePt || basePt <= 0) return viewPt <= minPt + 4;
  if (viewPt <= basePt + 0.5) return true;
  const maxView = Math.max(minPt, Math.round(basePt * ratio * 1.35 * 10) / 10);
  return viewPt <= maxView + 1;
}

async function applySmallFont(context, targetRange, anchorRange, opts) {
  anchorRange.font.load(["name", "size"]);
  targetRange.font.load(["name", "size"]);
  await context.sync();
  const hostSize = anchorRange.font.size;
  const boxSize =
    hostSize && hostSize > 0
      ? Math.max(
          opts.minFontSizePt,
          Math.round(hostSize * opts.fontSizeRatio * 10) / 10
        )
      : opts.minFontSizePt;
  targetRange.font.size = boxSize;
  if (anchorRange.font.name) {
    targetRange.font.name = anchorRange.font.name;
  }
  await context.sync();
}

async function insertContentControlAfterBase(context, insertAnchor) {
  let cc = insertAnchor.insertContentControl(W.ccRichText(), W.insertAfter());
  try {
    await context.sync();
    return cc;
  } catch {
    cc = insertAnchor.insertContentControl(W.ccRichText(), W.insertBefore());
    await context.sync();
    return cc;
  }
}

function normalizeClusterText(text) {
  return (text || "").replace(/\s/g, "");
}

function clusterTextMatches(text, baseChar, marks) {
  return normalizeClusterText(text) === baseChar + marks;
}

async function tagKaeritenView(context, viewRange, marks, viewId = null) {
  try {
    const id = viewId || nextKaeritenViewId();
    viewRange.insertBookmark(bookmarkNameForViewId(id));
    await context.sync();
  } catch {
    /* optional — bookmark API may be missing on some Word Mac builds */
  }
}

/**
 * Insert display glyphs in one shot (extra breaks/strategies can unwrap the CC on Word Mac).
 */
async function fillContentControlGlyphs(
  context,
  cc,
  glyphText,
  layout = "stack"
) {
  const lines = glyphText.split("\n").filter((line) => line.length > 0);
  const ccRange = cc.getRange();
  let text = glyphText;
  if (layout === "row" && lines.length > 1) {
    text = lines.join("");
  } else if (lines.length > 1) {
    text = lines.join("\u000b");
  }
  ccRange.insertText(text, W.insertReplace());
  await context.sync();
  return ccRange;
}

async function restoreMarksAfterBase(context, clusterRange, baseChar, marks) {
  const baseRange = await baseRangeAtClusterStart(
    context,
    clusterRange,
    baseChar
  );
  if (!baseRange) return;
  try {
    insertPointAfterBase(baseRange).insertText(marks, W.insertAfter());
    await context.sync();
  } catch {
    /* best effort */
  }
}

/** Find cluster ranges (base + all marks); Word often fails compact search for ㆒㆖. */
async function searchClusterOccurrences(context, workRange, baseChar, marks) {
  const compact = baseChar + marks;
  const verified = [];

  let direct = workRange.search(compact, {
    matchCase: true,
    matchWholeWord: false,
  });
  direct.load("items");
  await context.sync();
  for (const item of direct.items) {
    const range = item.getRange();
    range.load("text");
    await context.sync();
    if (clusterTextMatches(range.text, baseChar, marks)) {
      verified.push({ getRange: () => range });
    }
  }
  if (verified.length > 0) return { items: verified };

  const bases = workRange.search(baseChar, {
    matchCase: true,
    matchWholeWord: false,
  });
  bases.load("items");
  await context.sync();

  for (const item of bases.items) {
    const baseRange = item.getRange();
    baseRange.load("text");
    await context.sync();
    const marksRange = await marksRangeAfterBase(
      context,
      baseRange,
      marks,
      null
    );
    if (!marksRange) continue;
    try {
      const full = baseRange.expandTo(marksRange);
      full.load("text");
      await context.sync();
      if (clusterTextMatches(full.text, baseChar, marks)) {
        verified.push({ getRange: () => full });
      }
    } catch {
      continue;
    }
  }

  return { items: verified };
}

/** Try to keep the base kanji and kaeriten box on the same document line. */
async function keepKaeritenWithBase(context, baseRange, ccRange) {
  try {
    const basePara = baseRange.paragraphs.getFirst();
    basePara.paragraphFormat.keepTogether = true;
    const ccPara = ccRange.paragraphs.getFirst();
    ccPara.paragraphFormat.keepTogether = true;
    await context.sync();
  } catch {
    /* keepTogether unsupported on some Word Mac builds */
  }
}

async function insertKaeritenView(
  context,
  baseRange,
  marks,
  byChar,
  opts,
  insertAnchor
) {
  const vertical = await isVerticalFlow(context, baseRange);
  const glyphLayout = vertical && marks.length > 1 ? "row" : "stack";
  const glyphText = glyphsForMarks(marks, byChar);

  if (wordHasTextBoxApi() && !vertical) {
    if (opts.useInlineTextBox) {
      try {
        const box = await insertKaeritenInlineTextBox(
          context,
          insertAnchor,
          baseRange,
          marks,
          byChar,
          opts
        );
        await tagKaeritenView(
          context,
          box.shape.body.getRange(),
          marks,
          box.viewId
        );
        return box;
      } catch (inlineErr) {
        if (opts.preferInlineOnMac && isWordMac()) {
          throw inlineErr;
        }
        /* fall back to content control */
      }
    } else if (opts.useTextBox) {
      try {
        const box = await insertKaeritenTextBox(
          context,
          insertAnchor,
          baseRange,
          marks,
          byChar,
          opts,
          "floating"
        );
        await tagKaeritenView(
          context,
          box.shape.body.getRange(),
          marks,
          box.viewId
        );
        return box;
      } catch {
        /* fall back to content control */
      }
    }
  }
  baseRange.load("text");
  await context.sync();

  const cc = await insertContentControlAfterBase(context, insertAnchor);
  cc.tag = SOURCE_PREFIX + marks;
  cc.title = marks;
  await context.sync();

  let ccRange;
  try {
    ccRange = await fillContentControlGlyphs(
      context,
      cc,
      glyphText,
      glyphLayout
    );
    try {
      await applySmallFont(context, ccRange, baseRange, opts);
    } catch {
      /* font sizing optional */
    }
    await tagKaeritenView(context, ccRange, marks);
    const mac = isWordMac();
    if (!mac) {
      try {
        cc.appearance = W.ccBoundingBox();
        cc.color = "#EEF4FC";
      } catch {
        /* optional on Windows */
      }
      try {
        cc.cannotEdit = true;
        await context.sync();
      } catch {
        /* optional */
      }
    } else {
      try {
        cc.appearance = W.ccTags();
        await context.sync();
      } catch {
        /* Tags appearance keeps CC wrapper on Mac better than boundingBox */
      }
    }
    try {
      await keepKaeritenWithBase(context, baseRange, ccRange);
    } catch {
      /* optional */
    }
    return { kind: vertical ? "contentControlVertical" : "contentControl", cc };
  } catch (err) {
    try {
      cc.delete(true);
      await context.sync();
    } catch {
      /* ignore */
    }
    throw err;
  }
}

/** Delete marks in cluster, insert view at gap (content control / inline text box). */
async function renderClusterWithApi(
  context,
  clusterRange,
  baseChar,
  marks,
  byChar,
  opts
) {
  const baseRange = await baseRangeAtClusterStart(
    context,
    clusterRange,
    baseChar
  );
  if (!baseRange) {
    throw new Error(`Could not locate base character “${baseChar}” in cluster.`);
  }
  if (
    !(await deleteMarksFromCluster(context, clusterRange, baseChar, marks))
  ) {
    throw new Error(
      `Could not remove marks “${marks}” after “${baseChar}”. ` +
        "Select 說㆒㆑者 on one line and Render again."
    );
  }
  const insertAnchor = insertPointAfterBase(baseRange);
  await insertKaeritenView(
    context,
    baseRange,
    marks,
    byChar,
    opts,
    insertAnchor
  );
  clusterRange.load("text");
  await context.sync();
  if (clusterStillHasMarks(clusterRange.text)) {
    throw new Error(
      `Marks still present after render for “${baseChar}${marks}”.`
    );
  }
  return true;
}

/** Replace 問㆒㆑ via insertOoxml; on GeneralException fall back to API render. */
async function renderClusterWithOoxml(
  context,
  clusterRange,
  baseChar,
  marks,
  byChar,
  opts
) {
  if (!wordHasOoxmlApi()) {
    return renderClusterWithApi(
      context,
      clusterRange,
      baseChar,
      marks,
      byChar,
      opts
    );
  }
  const baseRange = await baseRangeAtClusterStart(
    context,
    clusterRange,
    baseChar
  );
  if (!baseRange) {
    throw new Error(`Could not locate base character “${baseChar}” in cluster.`);
  }
  const vertical = await isVerticalFlow(context, baseRange);
  if (vertical) {
    throw new Error(
      "OOXML kaeriten is not supported in vertical (縦書き) layout yet. Use horizontal text."
    );
  }
  baseRange.font.load("size");
  await context.sync();
  const hostPt = baseRange.font.size || 12;
  const glyphText = glyphsForMarks(marks, byChar);
  const viewId = nextKaeritenViewId();
  const layout =
    marks.length > 1 && !opts.macCompoundRow ? "stack" : "row";
  const layoutOpts = { ...opts, hostFontPt: hostPt };
  const variants = buildClusterReplaceOoxmlVariants(
    baseChar,
    marks,
    glyphText,
    layout,
    layoutOpts,
    hostPt
  );

  let lastErr = null;
  let lastProbeErrors = null;
  for (const { kind, ooxml } of variants) {
    const structural = sanityCheckOoxml(ooxml);
    if (!structural.ok) {
      lastProbeErrors = structural.errors;
      continue;
    }
    if (opts.ooxmlProbeWithWord) {
      const probe = await probeOoxmlWithWord(context, ooxml);
      if (!probe.ok) {
        lastProbeErrors = probe.errors;
        lastErr = new Error(
          probe.phase === "sanity"
            ? `OOXML structure: ${probe.errors.join("; ")}`
            : `Word probe: ${probe.errors.join("; ")}`
        );
        continue;
      }
    }
    try {
      clusterRange.insertOoxml(ooxml, W.insertReplace());
      await context.sync();
      clusterRange.load("text");
      await context.sync();
      if (!clusterStillHasMarks(clusterRange.text)) {
        try {
          await tagKaeritenView(
            context,
            insertPointAfterBase(baseRange),
            marks,
            viewId
          );
        } catch {
          /* bookmark optional on Mac */
        }
        await tagInlineShapeAfterBase(context, baseRange, marks, viewId);
        return { method: kind };
      }
    } catch (err) {
      lastErr = err;
    }
  }

  if (opts.ooxmlFallbackApi !== false) {
    try {
      await renderClusterWithApi(
        context,
        clusterRange,
        baseChar,
        marks,
        byChar,
        opts
      );
      return { method: "apiFallback" };
    } catch (apiErr) {
      const ooxmlMsg =
        lastErr && lastErr.message ? lastErr.message : String(lastErr);
      const apiMsg =
        apiErr && apiErr.message ? apiErr.message : String(apiErr);
      throw new Error(
        `OOXML failed (${ooxmlMsg}); API fallback also failed (${apiMsg}).`
      );
    }
  }

  const msg = ooxmlErrorDetail(lastErr);
  const probeHint = lastProbeErrors?.length
    ? ` Probe: ${lastProbeErrors.join("; ")}.`
    : "";
  throw new Error(
    `Word rejected kaeriten OOXML (${msg}).${probeHint} ` +
      "API fallback is enabled in mapping.json; if you still see this, re-render or set word_primary: content_control."
  );
}

async function renderClustersInRange(context, workRange, mappingData) {
  workRange.load("text");
  await context.sync();
  const text = workRange.text || "";
  const clusters = findClusters(text);
  if (!clusters.length) return 0;

  const byChar = mappingByChar(mappingData);
  const opts = wordRenderOptions(mappingData);
  let count = 0;

  for (let i = clusters.length - 1; i >= 0; i--) {
    const { baseChar, marks } = clusters[i];
    const results = await searchClusterOccurrences(
      context,
      workRange,
      baseChar,
      marks
    );

    for (let j = results.items.length - 1; j >= 0; j--) {
      const found = results.items[j];
      const clusterRange = found.getRange();
      clusterRange.load("text");
      await context.sync();
      if (!clusterRange.text || !clusterRange.text.includes(marks)) {
        continue;
      }
      try {
        const baseRange = await baseRangeAtClusterStart(
          context,
          clusterRange,
          baseChar
        );
        if (!baseRange) continue;

        try {
          if (opts.useOoxml) {
            await renderClusterWithOoxml(
              context,
              clusterRange,
              baseChar,
              marks,
              byChar,
              opts
            );
          } else {
            await renderClusterWithApi(
              context,
              clusterRange,
              baseChar,
              marks,
              byChar,
              opts
            );
          }
          count += 1;
        } catch (renderErr) {
          if (!opts.useOoxml) {
            await restoreMarksAfterBase(context, clusterRange, baseChar, marks);
          }
          throw renderErr;
        }
      } catch (err) {
        const msg = err && err.message ? err.message : String(err);
        const compound = marks.length > 1 ? " (compound marks)" : "";
        throw new Error(
          `Could not render “${baseChar}${marks}”${compound}: ${msg}`
        );
      }
    }
  }
  return count;
}

export async function renderKaeritenDocument(context, mappingData) {
  const selection = context.document.getSelection();
  selection.load("text");
  await context.sync();
  const selText = selection.text || "";
  const expectedClusters = findClusters(selText).length;

  const workRange = await getWorkRangeForRender(context);
  const count = await renderClustersInRange(context, workRange, mappingData);

  if (count === 0) {
    throw new Error(
      "Render could not format any marks in the selection. Re-type 漢㆒㆑字 on one line, select all of it, then Render."
    );
  }

  selection.load("text");
  await context.sync();
  const marksLeft = selectionHasKaeritenMarks(selection.text);
  if (marksLeft) {
    throw new Error(
      `Only ${count} of ${expectedClusters} mark group(s) in the selection were formatted. ` +
        "Put all marks on one line (no line break between ㆒ and ㆑), select the whole word, then Render again."
    );
  }

  return count;
}

async function rangesOverlap(context, a, b) {
  try {
    const rel = a.compareLocationWith(b);
    rel.load("value");
    await context.sync();
    const v = rel.value;
    return v !== W.locBefore() && v !== W.locAfter();
  } catch {
    return true;
  }
}

export function marksFromControl(cc, displayLookup, displayText) {
  return resolveMarksFromControl(
    cc,
    displayLookup,
    displayText,
    SOURCE_PREFIX
  );
}

export async function listMarinaMojiControls(context, workRange, mappingData) {
  const byChar = mappingData ? mappingByChar(mappingData) : {};
  const displayLookup =
    Object.keys(byChar).length > 0 ? buildDisplayToMarksMap(byChar) : null;

  const all = context.document.contentControls;
  all.load("items");
  await context.sync();

  const matched = [];
  for (const cc of all.items) {
    cc.load(["tag", "title"]);
    cc.getRange().load("text");
  }
  await context.sync();

  for (const cc of all.items) {
    const ccRange = cc.getRange();
    const displayText = ccRange.text;
    const marks = marksFromControl(cc, displayLookup, displayText);
    if (!marks) continue;
    if (workRange && !(await rangesOverlap(context, workRange, ccRange))) {
      continue;
    }
    matched.push({ cc, marks, ccRange });
  }
  return matched;
}

async function listMarinaMojiViewsInScope(context, mappingData) {
  const byChar = mappingData ? mappingByChar(mappingData) : {};
  const displayLookup =
    Object.keys(byChar).length > 0 ? buildDisplayToMarksMap(byChar) : null;
  const workRange = await getWorkRange(context);

  const ccItems = await listMarinaMojiControls(context, workRange, mappingData);
  let boxItems = [];
  if (wordHasTextBoxApi()) {
    boxItems = await listMarinaMojiTextBoxes(
      context,
      workRange,
      displayLookup
    );
  }

  return { ccItems, boxItems, displayLookup, workRange };
}

async function listMarinaMojiBookmarks(context, workRange) {
  const matched = [];
  const seen = new Set();
  const add = (name, marks, range) => {
    if (!name || seen.has(name) || !marks) return;
    seen.add(name);
    matched.push({ name, marks, range });
  };

  try {
    const all = context.document.body.bookmarks;
    all.load("items");
    await context.sync();
    for (const bm of all.items) {
      bm.load("name");
    }
    await context.sync();
    for (const bm of all.items) {
      const marks = marksFromBookmarkName(bm.name);
      const isIdBm = isViewIdBookmarkName(bm.name);
      if (!marks && !isIdBm) continue;
      let range = null;
      try {
        range = bm.getRange();
      } catch {
        continue;
      }
      if (workRange) {
        const overlaps = await rangesOverlap(context, workRange, range);
        if (!overlaps) {
          workRange.load("text");
          range.load("text");
          await context.sync();
          const inSel =
            (range.text || "").length > 0 &&
            (workRange.text || "").includes(range.text);
          if (!inSel) continue;
        }
      }
      add(bm.name, marks || null, range);
    }
  } catch {
    /* fall back to selection-local names */
  }

  if (matched.length === 0 && workRange) {
    try {
      const result = workRange.getBookmarks(true, true);
      await context.sync();
      const names = result.value || [];
      for (const name of names) {
        const marks = marksFromBookmarkName(name);
        if (!marks && !isViewIdBookmarkName(name)) continue;
        add(name, marks || null, null);
      }
    } catch {
      /* optional */
    }
  }
  return matched;
}

/** Bookmarks are metadata only: never replace bookmark span; insert after base if needed, then delete bookmark. */
async function cleanupKaeritenBookmarkMetadata(
  context,
  name,
  marks,
  workRange,
  rangeHint
) {
  if (!marks) {
    try {
      const bm = context.document.body.bookmarks.getItem(name);
      bm.delete();
      await context.sync();
    } catch {
      /* optional */
    }
    return false;
  }
  let range = rangeHint || null;
  if (!range) {
    try {
      const bm = context.document.body.bookmarks.getItemOrNullObject(name);
      bm.load("name");
      await context.sync();
      if (!bm.isNullObject) {
        range = bm.getRange();
      }
    } catch {
      /* optional */
    }
  }
  if (!range) return false;

  const baseRange =
    (await baseCharRangeBeforeView(context, range)) ||
    (await baseKanjiAdjacentBefore(context, range));
  if (baseRange) {
    const baseChar = (baseRange.text || "").replace(/\r/g, "");
    if (
      !(await marksPresentAfterBase(context, baseRange, marks)) &&
      !(await marksRestoredInWorkRange(context, workRange, baseChar, marks))
    ) {
      try {
        insertPointAfterBase(baseRange).insertText(marks, W.insertAfter());
        await context.sync();
      } catch {
        /* optional */
      }
    }
  }

  try {
    const bm = context.document.body.bookmarks.getItem(name);
    bm.delete();
    await context.sync();
  } catch {
    /* already removed */
  }

  if (baseRange) {
    const baseChar = (baseRange.text || "").replace(/\r/g, "");
    return (
      (await marksPresentAfterBase(context, baseRange, marks)) ||
      (await marksRestoredInWorkRange(context, workRange, baseChar, marks))
    );
  }
  return false;
}

async function marksRestoredInWorkRange(context, workRange, baseChar, marks) {
  if (!workRange || !baseChar || !marks) return false;
  workRange.load("text");
  await context.sync();
  const text = (workRange.text || "").replace(/\r/g, "");
  return text.includes(baseChar + normalizeMarks(marks));
}

/** If only display glyphs are selected, widen to base + view via paragraph search. */
async function expandWorkRangeForOrphanDetect(context, workRange, displayLookup) {
  workRange.load("text");
  await context.sync();
  const text = workRange.text || "";
  if (findOrphanViewClusters(text, displayLookup).length > 0) {
    return workRange;
  }
  const norm = normalizeDisplayKey(text);
  if (!norm || !displayLookup.has(norm)) {
    return workRange;
  }
  const marks = displayLookup.get(norm);
  if (!marks) return workRange;

  try {
    const para = workRange.paragraphs.getFirst().getRange();
    para.load("text");
    await context.sync();
    const orphans = findOrphanViewClusters(para.text || "", displayLookup);
    for (const hit of orphans) {
      if (hit.displayKey !== norm) continue;
      const found = await findOrphanViewInWorkRange(
        context,
        para,
        hit.baseChar,
        hit.marks,
        hit.displayRaw,
        hit.displayKey
      );
      if (!found) continue;
      const overlaps = await rangesOverlap(context, workRange, found.viewRange);
      if (overlaps) return found.full;
    }
  } catch {
    /* keep original */
  }
  return workRange;
}

/**
 * Unrender when Word removed the CC/shape wrapper but left small display glyphs (レ/一).
 */
async function unrenderOrphanDisplayViews(
  context,
  workRange,
  displayLookup,
  opts
) {
  if (!displayLookup?.size) return 0;

  workRange.load("text");
  await context.sync();
  const text = workRange.text || "";
  const candidates = findOrphanViewClusters(text, displayLookup);
  if (!candidates.length) return 0;

  const ratio = opts?.fontSizeRatio ?? 0.42;
  const minPt = opts?.minFontSizePt ?? 6;
  let count = 0;

  for (let i = candidates.length - 1; i >= 0; i--) {
    const { baseChar, marks, displayRaw, displayKey } = candidates[i];
    if (!marks || !displayRaw) continue;

    const found = await findOrphanViewInWorkRange(
      context,
      workRange,
      baseChar,
      marks,
      displayRaw,
      displayKey
    );
    if (!found) continue;
    const { viewRange, baseRange } = found;
    viewRange.load("text");
    baseRange.load("text");
    await context.sync();

    const targetKey = normalizeDisplayKey(displayRaw);
    if (normalizeDisplayKey(viewRange.text) !== targetKey) continue;
    if (baseRange.text !== baseChar) continue;

    try {
      viewRange.font.load("size");
      baseRange.font.load("size");
      await context.sync();
      if (
        !viewFontLooksLikeKaeriten(
          viewRange.font.size,
          baseRange.font.size,
          ratio,
          minPt
        )
      ) {
        continue;
      }
    } catch {
      /* font load optional */
    }

    viewRange.insertText(marks, W.insertReplace());
    await context.sync();
    count += 1;
  }
  return count;
}

/** Render failed but left small Unicode ㆒㆑ — restore mark size to match the base kanji. */
async function unrenderShrunkUnicodeMarks(context, workRange) {
  workRange.load("text");
  await context.sync();
  const clusters = findClusters(workRange.text || "");
  if (!clusters.length) return 0;

  let count = 0;
  for (let i = clusters.length - 1; i >= 0; i--) {
    const { baseChar, marks } = clusters[i];
    const results = await searchClusterOccurrences(
      context,
      workRange,
      baseChar,
      marks
    );
    for (let j = results.items.length - 1; j >= 0; j--) {
      try {
        const clusterRange = results.items[j].getRange();
        const baseRange = await baseRangeAtClusterStart(
          context,
          clusterRange,
          baseChar
        );
        if (!baseRange) continue;
        const marksRange = await marksRangeInCluster(
          context,
          baseRange,
          clusterRange,
          marks
        );
        if (!marksRange) continue;
        marksRange.font.load("size");
        baseRange.font.load("size");
        await context.sync();
        const basePt = baseRange.font.size;
        const markPt = marksRange.font.size;
        if (basePt && markPt && markPt < basePt - 0.5) {
          marksRange.font.size = basePt;
          await context.sync();
          count += 1;
        }
      } catch {
        continue;
      }
    }
  }
  return count;
}

/** Replace view glyphs with source marks and remove the content control wrapper. */
async function unrenderOneControl(context, cc, marks) {
  cc.load("cannotEdit");
  await context.sync();
  if (cc.cannotEdit) {
    cc.cannotEdit = false;
    await context.sync();
  }

  const ccRange = cc.getRange();
  ccRange.insertText(marks, W.insertReplace());
  await context.sync();
  cc.delete(true);
  await context.sync();
  await dropKaeritenBookmark(context, marks);
}

async function dropKaeritenBookmark(context, marks) {
  const name = bookmarkNameForMarks(marks);
  try {
    const bm = context.document.body.bookmarks.getItem(name);
    bm.delete();
    await context.sync();
  } catch {
    /* already removed */
  }
}

export async function unrenderKaeritenDocument(context, mappingData) {
  const workRange = await getWorkRangeForUnrender(context);
  const byChar = mappingByChar(mappingData);
  const displayLookup =
    Object.keys(byChar).length > 0 ? buildDisplayToMarksMap(byChar) : null;
  const opts = wordRenderOptions(mappingData);

  const ccItems = await listMarinaMojiControls(context, workRange, mappingData);
  let boxItems = [];
  if (wordHasTextBoxApi()) {
    boxItems = await listMarinaMojiTextBoxes(
      context,
      workRange,
      displayLookup
    );
    if (!boxItems.length) {
      const allBoxes = await listMarinaMojiTextBoxes(
        context,
        null,
        displayLookup
      );
      for (const item of allBoxes) {
        if (await shapeOverlapsWorkRange(context, workRange, item.shape)) {
          boxItems.push(item);
        }
      }
    }
  }
  const bookmarkItems = await listMarinaMojiBookmarks(context, workRange);

  const restoredBoxKeys = new Set();
  const boxRecoveries = [];
  const emergencyStubs = [];
  const totalViews = ccItems.length + boxItems.length;
  let restoredCount = 0;

  for (const { shape, marks } of boxItems) {
    const resolved =
      marksFromShape(shape, null, "") || String(marks || "").replace(/\s/g, "");
    const baseRange = await resolveBaseBeforeShape(context, workRange, shape);
    emergencyStubs.push({
      marks: resolved,
      baseChar: baseRange ? (baseRange.text || "").replace(/\r/g, "") : "",
      baseRange,
      shape,
      viewKey: viewKeyForShape(shape),
    });
  }

  for (let i = ccItems.length - 1; i >= 0; i--) {
    const { cc, marks } = ccItems[i];
    await unrenderOneControl(context, cc, marks);
    restoredCount += 1;
  }

  for (let i = boxItems.length - 1; i >= 0; i--) {
    const { shape, marks } = boxItems[i];
    const viewKey = viewKeyForShape(shape);
    const { success, recovery } = await unrenderOneTextBox(
      context,
      shape,
      marks,
      workRange
    );
    if (success) {
      restoredCount += 1;
      if (viewKey) restoredBoxKeys.add(viewKey);
    } else if (recovery?.baseRange) {
      boxRecoveries.push(recovery);
    }
  }

  if (boxRecoveries.length) {
    const restoredMarks = await recoverMarksAfterBase(
      context,
      boxRecoveries,
      workRange
    );
    restoredCount += restoredMarks.length;
    for (const { shape } of boxItems) {
      const key = viewKeyForShape(shape);
      if (key) restoredBoxKeys.add(key);
    }
  }

  const pendingStubs = emergencyStubs.filter(
    (s) => s.marks && s.viewKey && !restoredBoxKeys.has(s.viewKey)
  );
  if (pendingStubs.length) {
    const restored = await emergencyRestoreMarks(
      context,
      workRange,
      pendingStubs
    );
    restoredCount += restored.length;
    for (const stub of pendingStubs) {
      if (stub.viewKey) restoredBoxKeys.add(stub.viewKey);
    }
    for (const { shape } of boxItems) {
      const key = viewKeyForShape(shape);
      if (!key || !restoredBoxKeys.has(key)) continue;
      const resolved = marksFromShape(shape, null, "") || "";
      if (resolved) {
        await deleteShapeIfMarksPresent(context, shape, resolved, workRange);
      }
    }
  }

  for (const { name, marks, range } of bookmarkItems) {
    await cleanupKaeritenBookmarkMetadata(
      context,
      name,
      marks,
      workRange,
      range
    );
  }

  let count = restoredCount;
  if (count === 0 && displayLookup) {
    const orphanScope = await expandWorkRangeForOrphanDetect(
      context,
      workRange,
      displayLookup
    );
    count += await unrenderOrphanDisplayViews(
      context,
      orphanScope,
      displayLookup,
      opts
    );
  }
  if (count === 0) {
    count += await unrenderShrunkUnicodeMarks(context, workRange);
  }

  if (count === 0) {
    if (totalViews > 0) {
      throw new Error(
        "Removed the kaeriten box but could not restore Unicode marks (㆒㆑). Press Undo (⌘Z), select the whole word including the kanji, then Unrender again—or type the marks after the kanji manually."
      );
    }
    throw new Error(
      "No marinaMoji kaeriten found in the selection. Select the whole word (kanji + small mark), e.g. の and tiny レ, or 說㆒㆑, then Unrender. " +
        "Re-render after updating the add-in if this text was formatted earlier."
    );
  }
  return count;
}

/** Re-insert OOXML when shape.body is empty but alt/descr still has source marks. */
async function refreshInlineBoxViaOoxml(
  context,
  shape,
  marks,
  baseRange,
  byChar,
  opts
) {
  const baseChar = (baseRange.text || "").replace(/\r/g, "");
  if (!baseChar || baseChar.length !== 1) {
    throw new Error("Could not find base kanji before kaeriten box.");
  }
  baseRange.font.load("size");
  await context.sync();
  const hostPt = baseRange.font.size || 12;
  const glyphText = glyphsForMarks(marks, byChar);
  const layout =
    marks.length > 1 && !opts.macCompoundRow ? "stack" : "row";
  const layoutOpts = { ...opts, hostFontPt: hostPt };
  const variants = buildClusterReplaceOoxmlVariants(
    baseChar,
    marks,
    glyphText,
    layout,
    layoutOpts,
    hostPt
  );

  let clusterRange = null;
  try {
    const boxRange = shape.body.getRange();
    clusterRange = baseRange.expandTo(boxRange);
  } catch {
    /* expandTo can fail on some inline shapes */
  }
  if (!clusterRange) {
    throw new Error("Could not locate inline kaeriten for OOXML refresh.");
  }

  let lastErr = null;
  for (const { ooxml } of variants) {
    try {
      clusterRange.insertOoxml(ooxml, W.insertReplace());
      await context.sync();
      return;
    } catch (err) {
      lastErr = err;
    }
  }
  const msg =
    lastErr && lastErr.message ? lastErr.message : String(lastErr ?? "unknown");
  throw new Error(`OOXML refresh failed (${msg}).`);
}

export async function refreshKaeritenDocument(context, mappingData) {
  const byChar = mappingByChar(mappingData);
  const opts = wordRenderOptions(mappingData);
  const { ccItems, boxItems } = await listMarinaMojiViewsInScope(
    context,
    mappingData
  );

  for (const { cc, marks } of ccItems) {
    const glyphText = glyphsForMarks(marks, byChar);
    const vertical = await isVerticalFlow(context, cc.getRange());
    const glyphLayout = vertical && marks.length > 1 ? "row" : "stack";
    const ccRange = await fillContentControlGlyphs(
      context,
      cc,
      glyphText,
      glyphLayout
    );
    const anchor =
      (await baseKanjiAdjacentBefore(context, ccRange)) || ccRange;
    await applySmallFont(context, ccRange, anchor, opts);
  }

  for (const { shape, marks } of boxItems) {
    shape.body.load("text");
    await context.sync();
    const bodyText = (shape.body.text || "").replace(/\r/g, "").trim();
    const anchorRange = shape.body.getRange();
    const baseRange = await baseKanjiAdjacentBefore(context, anchorRange);
    const vertical = baseRange
      ? await isVerticalFlow(context, baseRange)
      : false;

    if (!bodyText && isMarinaMojiTextBox(shape) && opts.useOoxml && baseRange) {
      await refreshInlineBoxViaOoxml(
        context,
        shape,
        marks,
        baseRange,
        byChar,
        opts
      );
      continue;
    }

    await refreshKaeritenTextBox(
      context,
      shape,
      marks,
      byChar,
      opts,
      vertical
    );
  }

  await context.sync();
  return ccItems.length + boxItems.length;
}

/** Find marinaMoji views for export (relaxed shape scan when selection omits inline boxes). */
async function listMarinaMojiViewsForExport(context, mappingData, workRange) {
  const byChar = mappingByChar(mappingData);
  const displayLookup =
    Object.keys(byChar).length > 0 ? buildDisplayToMarksMap(byChar) : null;

  const ccItems = await listMarinaMojiControls(context, workRange, mappingData);
  let boxItems = [];
  if (wordHasTextBoxApi()) {
    boxItems = await listMarinaMojiTextBoxes(
      context,
      workRange,
      displayLookup
    );
    if (!boxItems.length) {
      const allBoxes = await listMarinaMojiTextBoxes(context, null, displayLookup);
      for (const item of allBoxes) {
        if (await shapeOverlapsWorkRange(context, workRange, item.shape)) {
          boxItems.push(item);
        }
      }
    }
  }
  return { ccItems, boxItems, displayLookup };
}

async function exportTupleForView(
  context,
  workRange,
  viewRange,
  marks,
  displayText,
  byChar
) {
  const resolved = String(marks || "").replace(/\s/g, "");
  if (!resolved) return null;
  const baseRange = await findBaseRangeForView(context, workRange, viewRange);
  if (!baseRange) return null;
  const baseChar = (baseRange.text || "").replace(/\r/g, "");
  if (!baseChar) return null;
  const index = await baseOffsetInWorkRange(context, workRange, baseRange);
  const display =
    displayText || glyphsForMarks(resolved, byChar);
  return {
    baseChar,
    marks: resolved,
    displayText: display,
    index,
    position: index >= 0 ? index : -1,
  };
}

/** Read canonical Unicode from selection without unrendering (clipboard-safe). */
async function readCanonicalTextInRange(
  context,
  workRange,
  mappingData,
  ccItems,
  boxItems
) {
  const byChar = mappingByChar(mappingData);
  workRange.load("text");
  await context.sync();
  const raw = (workRange.text || "").replace(/\r/g, "");

  if (!ccItems.length && !boxItems.length) {
    return raw;
  }

  for (const cc of ccItems) {
    cc.getRange().load("text");
  }
  for (const { shape } of boxItems) {
    shape.body.load("text");
  }
  await context.sync();

  const tuples = [];
  for (const { cc, marks } of ccItems) {
    const t = await exportTupleForView(
      context,
      workRange,
      cc.getRange(),
      marks,
      cc.getRange().text,
      byChar
    );
    if (t) tuples.push(t);
  }
  for (const { shape, marks, displayText } of boxItems) {
    const t = await exportTupleForView(
      context,
      workRange,
      shape.body.getRange(),
      marksFromShape(shape, null, "") || marks,
      displayText || shape.body.text,
      byChar
    );
    if (t) tuples.push(t);
  }

  if (!tuples.length) {
    return raw;
  }

  return buildCanonicalPlainText(raw, tuples);
}

export async function canonicalTextForExport(context, mappingData) {
  const workRange = await getWorkRange(context);
  const fullDocument = await selectionIsEmpty(context);
  const { ccItems, boxItems } = await listMarinaMojiViewsForExport(
    context,
    mappingData,
    workRange
  );
  const text = await readCanonicalTextInRange(
    context,
    workRange,
    mappingData,
    ccItems,
    boxItems
  );
  return { text, fullDocument };
}
