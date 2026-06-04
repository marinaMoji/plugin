/**
 * Word Range helpers without moveStart/moveEnd (unreliable on Word Mac).
 * Strategy: expandTo on verified clusters, then search inside non-collapsed spans.
 */

import { W } from "./wordEnums.js";
import { normalizeDisplayKey, normalizeMarksRun } from "./exportCore.js";

/** Collapsed range at the gap immediately after a base character. */
export function insertPointAfterBase(baseRange) {
  return baseRange.getRange(W.rangeEnd());
}

/**
 * Marks-only span inside a verified cluster (問㆒㆑ → ㆒㆑).
 * Uses expandTo — avoids search() on a zero-width range at base end.
 */
export async function marksRangeInCluster(context, baseRange, clusterRange, marks) {
  try {
    const span = baseRange.getRange(W.rangeEnd()).expandTo(clusterRange);
    span.load("text");
    await context.sync();
    if (normalizeMarksRun(span.text) === normalizeMarksRun(marks)) {
      return span;
    }
  } catch {
    /* fall through */
  }
  return contiguousRangeAfterAnchor(
    context,
    baseRange,
    marks,
    clusterRange
  );
}

/**
 * Contiguous range for `charSequence` after anchor end, bounded by `boundRange` or paragraph end.
 * Search runs inside a non-collapsed span (Word Mac rejects search on collapsed ranges).
 */
export async function contiguousRangeAfterAnchor(
  context,
  anchorRange,
  charSequence,
  boundRange = null
) {
  const endBound =
    boundRange ||
    anchorRange.paragraphs.getFirst().getRange(W.rangeEnd());
  let searchSpan;
  try {
    searchSpan = anchorRange.getRange(W.rangeEnd()).expandTo(endBound);
  } catch {
    return null;
  }
  searchSpan.load("text");
  await context.sync();
  const normTail = normalizeMarksRun(searchSpan.text);
  const normSeq = normalizeMarksRun(charSequence);
  if (normTail === normSeq) {
    return searchSpan;
  }

  let cursor = searchSpan;
  let first = null;
  let last = null;
  for (const ch of charSequence) {
    if (ch === "\r") continue;
    const hit = cursor.search(ch, {
      matchCase: true,
      matchWholeWord: false,
    });
    hit.load("items");
    await context.sync();
    if (!hit.items.length) return null;
    const r = hit.items[0].getRange();
    if (!first) first = r;
    last = r;
    try {
      cursor = r.getRange(W.rangeEnd()).expandTo(searchSpan.getRange(W.rangeEnd()));
    } catch {
      return null;
    }
  }
  if (!first || !last) return null;
  return first.expandTo(last);
}

/**
 * True when Unicode marks sit immediately after baseRange (not “marks + following kanji”).
 * Uses a short tail after the base — not the whole paragraph (問㆒㆑題 would fail otherwise).
 */
export async function marksPresentAfterBase(context, baseRange, marks) {
  if (!baseRange || !marks) return false;
  const normMarks = normalizeMarksRun(marks);
  if (!normMarks) return false;
  try {
    const gap = insertPointAfterBase(baseRange);
    const paraEnd = baseRange.paragraphs.getFirst().getRange(W.rangeEnd());
    const span = gap.expandTo(paraEnd);
    span.load("text");
    await context.sync();
    let tail = normalizeMarksRun((span.text || "").replace(/\r/g, ""));
    tail = tail.replace(/\uFFFC/g, "");
    if (tail.startsWith(normMarks)) return true;
    const span2 = await marksRangeAfterBase(context, baseRange, marks, null);
    if (!span2) return false;
    span2.load("text");
    await context.sync();
    return normalizeMarksRun(span2.text) === normMarks;
  } catch {
    return false;
  }
}

/** Marks ㆒㆑ immediately after the base kanji (pass clusterRange when already verified). */
export async function marksRangeAfterBase(
  context,
  baseRange,
  marks,
  clusterRange = null
) {
  if (clusterRange) {
    const inCluster = await marksRangeInCluster(
      context,
      baseRange,
      clusterRange,
      marks
    );
    if (inCluster) return inCluster;
  }
  return contiguousRangeAfterAnchor(
    context,
    baseRange,
    marks,
    clusterRange
  );
}

/** Base kanji at the start of a cluster range (not an earlier homograph in the span). */
export async function baseRangeAtClusterStart(context, clusterRange, baseChar) {
  const baseResults = clusterRange.search(baseChar, {
    matchCase: true,
    matchWholeWord: false,
  });
  baseResults.load("items");
  await context.sync();
  if (!baseResults.items.length) return null;

  const clusterStart = clusterRange.getRange(W.rangeStart());
  for (const item of baseResults.items) {
    const baseRange = item.getRange();
    try {
      const rel = clusterStart.compareLocationWith(baseRange);
      rel.load("value");
      await context.sync();
      if (rel.value === "Equal" || rel.value === W.locEqual()) {
        return baseRange;
      }
    } catch {
      continue;
    }
  }
  return baseResults.items[0].getRange();
}

/** First character range after base (for gap cleanup). */
export async function nextCharacterRange(context, baseRange) {
  const para = baseRange.paragraphs.getFirst().getRange();
  const tail = baseRange.getRange(W.rangeEnd()).expandTo(para.getRange(W.rangeEnd()));
  tail.load("text");
  await context.sync();
  const t = (tail.text || "").replace(/\r/g, "");
  if (!t) return null;
  const ch = t[0];
  const hits = tail.search(ch, {
    matchCase: true,
    matchWholeWord: false,
  });
  hits.load("items");
  await context.sync();
  if (!hits.items.length) return null;
  return hits.items[0].getRange();
}

/**
 * Last non-mark character immediately before view (inline OOXML / text box).
 * More tolerant than baseKanjiAdjacentBefore when paragraph text omits the shape body.
 */
export async function baseCharRangeBeforeView(context, viewRange) {
  try {
    const viewStart = viewRange.getRange(W.rangeStart());
    const para = viewRange.paragraphs.getFirst().getRange();
    const beforeView = para.getRange(W.rangeStart()).expandTo(viewStart);
    beforeView.load("text");
    await context.sync();
    let beforeText = (beforeView.text || "").replace(/\r/g, "");
    beforeText = beforeText.replace(/[\u3190-\u319f\s\u000b\u2028]+$/g, "");
    if (!beforeText) return null;
    const baseChar = beforeText[beforeText.length - 1];
    if (!baseChar || /[\u3190-\u319f\s]/.test(baseChar)) return null;
    const hits = beforeView.search(baseChar, {
      matchCase: true,
      matchWholeWord: false,
    });
    hits.load("items");
    await context.sync();
    if (!hits.items.length) return null;
    return hits.items[hits.items.length - 1].getRange();
  } catch {
    return null;
  }
}

/** Character offset of baseRange start within workRange (for export splice). */
export async function baseOffsetInWorkRange(context, workRange, baseRange) {
  if (!workRange || !baseRange) return -1;
  try {
    const workStart = workRange.getRange(W.rangeStart());
    const baseStart = baseRange.getRange(W.rangeStart());
    const prefix = workStart.expandTo(baseStart);
    prefix.load("text");
    await context.sync();
    return (prefix.text || "").replace(/\r/g, "").length;
  } catch {
    return -1;
  }
}

/** Find base kanji range for an inline view using paragraph context. */
export async function findBaseRangeForView(context, workRange, viewRange) {
  let base =
    (await baseKanjiAdjacentBefore(context, viewRange)) ||
    (await baseCharRangeBeforeView(context, viewRange));
  if (base) return base;

  try {
    const viewStart = viewRange.getRange(W.rangeStart());
    const para = viewRange.paragraphs.getFirst().getRange();
    const beforeView = para.getRange(W.rangeStart()).expandTo(viewStart);
    beforeView.load("text");
    await context.sync();
    let beforeText = (beforeView.text || "").replace(/\r/g, "");
    beforeText = beforeText.replace(/[\u3190-\u319f\s\u000b\u2028\uFFFC]+$/g, "");
    if (!beforeText) return null;
    const baseChar = beforeText[beforeText.length - 1];
    if (!baseChar || /[\u3190-\u319f\s]/.test(baseChar)) return null;

    const scope = workRange || para;
    const hits = scope.search(baseChar, {
      matchCase: true,
      matchWholeWord: false,
    });
    hits.load("items");
    await context.sync();
    for (let i = hits.items.length - 1; i >= 0; i--) {
      const candidate = hits.items[i].getRange();
      try {
        const rel = candidate.getRange(W.rangeEnd()).compareLocationWith(viewStart);
        rel.load("value");
        await context.sync();
        const v = rel.value;
        if (v === W.locEqual() || v === "Equal" || v === W.locBefore() || v === "Before") {
          return candidate;
        }
      } catch {
        continue;
      }
    }
    if (hits.items.length) {
      return hits.items[hits.items.length - 1].getRange();
    }
  } catch {
    /* optional */
  }
  return null;
}

/** Base kanji immediately before a view range (content control / shape body). */
export async function baseKanjiAdjacentBefore(context, viewRange) {
  try {
    const viewStart = viewRange.getRange(W.rangeStart());
    const para = viewRange.paragraphs.getFirst().getRange();
    const beforeView = para.getRange(W.rangeStart()).expandTo(viewStart);
    beforeView.load("text");
    await context.sync();
    const beforeText = (beforeView.text || "").replace(/\r/g, "");
    const match = beforeText.match(
      /([^\u3190-\u319f\s\u000b\u2028])(?:[\u3190-\u319f\s\u000b\u2028]*)$/
    );
    if (!match) return null;
    const baseChar = match[1];
    const hits = beforeView.search(baseChar, {
      matchCase: true,
      matchWholeWord: false,
    });
    hits.load("items");
    await context.sync();
    if (!hits.items.length) return null;
    return hits.items[hits.items.length - 1].getRange();
  } catch {
    return null;
  }
}

/** base + display glyphs (orphan plain-text view). */
export async function findOrphanViewInWorkRange(
  context,
  workRange,
  baseChar,
  marks,
  displayRaw,
  displayKey
) {
  const bases = workRange.search(baseChar, {
    matchCase: true,
    matchWholeWord: false,
  });
  bases.load("items");
  await context.sync();

  for (const item of bases.items) {
    const baseRange = item.getRange();
    const viewRange = await contiguousRangeAfterAnchor(
      context,
      baseRange,
      displayRaw,
      workRange
    );
    if (!viewRange) continue;
    try {
      const full = baseRange.expandTo(viewRange);
      full.load("text");
      await context.sync();
      const norm = normalizeDisplayKey(full.text || "");
      if (norm === baseChar + displayKey) {
        return { baseRange, viewRange, full };
      }
    } catch {
      continue;
    }
  }
  return null;
}
