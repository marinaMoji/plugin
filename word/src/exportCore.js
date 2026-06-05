/**
 * Canonical-text exporters for marinaMoji kaeriten (no Word dependency).
 * Port of libreoffice/marinamoji_kaeriten/export_core.py
 */

/** Marks may be split across lines in the document (漢㆒↵㆖字) — whitespace only between mark code points. */
const CLUSTER_RE =
  /([^\u3190-\u319f\s])([\u3190-\u319f]+(?:\s*[\u3190-\u319f]+)*)/gu;

export function normalizeMarks(marks) {
  return marks.replace(/\s+/g, "");
}

export const BOOKMARK_PREFIX = "_MMK_";

/** Content-control tag / shape descr prefix for source marks. */
export const SOURCE_PREFIX = "MARINAMOJI:source=";

const KAERITEN_TAG_PREFIX = "MARINAMOJI:kaeriten:";

let _kaeritenViewIdSeq = 0;

export function nextKaeritenViewId() {
  _kaeritenViewIdSeq += 1;
  return `v${Date.now().toString(36)}${_kaeritenViewIdSeq}`;
}

/** Tag on CC / shape alt text. New renders use a unique id + source marks. */
export function encodeKaeritenSourceTag(marks, viewId = null, flow = null) {
  const id = viewId || nextKaeritenViewId();
  const source = normalizeMarks(marks);
  const flowBit =
    flow === "v" || flow === "vertical"
      ? ";flow=v"
      : flow === "h" || flow === "horizontal"
        ? ";flow=h"
        : "";
  return `${KAERITEN_TAG_PREFIX}id=${id};source=${source}${flowBit}`;
}

/**
 * Parse marinaMoji tag (new or legacy `MARINAMOJI:source=㆒㆑`).
 * @returns {{ viewId: string|null, marks: string }|null}
 */
export function parseKaeritenSourceTag(raw) {
  const s = String(raw ?? "").trim();
  if (!s) return null;
  if (/^[\u3190-\u319f]+$/.test(s)) {
    return { viewId: null, marks: normalizeMarks(s) };
  }
  const idFirst = s.match(/id=([^;]+);source=([\u3190-\u319f]+)/i);
  if (idFirst) {
    return {
      viewId: idFirst[1],
      marks: normalizeMarks(idFirst[2]),
    };
  }
  if (s.startsWith(SOURCE_PREFIX)) {
    return {
      viewId: null,
      marks: normalizeMarks(s.slice(SOURCE_PREFIX.length)),
    };
  }
  const loose = s.match(/source=([\u3190-\u319f]+)/i);
  if (loose && /marinamoji/i.test(s)) {
    return { viewId: null, marks: normalizeMarks(loose[1]) };
  }
  return null;
}

/** Hidden bookmark for a specific view id (metadata only — not primary unrender). */
export function bookmarkNameForViewId(viewId) {
  const safe = String(viewId).replace(/[^a-zA-Z0-9_-]/g, "");
  return `${BOOKMARK_PREFIX}ID_${safe}`;
}

/** Hidden bookmark name encoding source marks (legacy; two ㆑ share one name). */
export function bookmarkNameForMarks(marks) {
  const codes = [...marks].map((c) =>
    c.codePointAt(0).toString(16).toUpperCase()
  );
  return BOOKMARK_PREFIX + codes.join("_");
}

/** View-id bookmark (`_MMK_ID_v…`) — metadata only, no marks in the name. */
export function isViewIdBookmarkName(name) {
  return !!name && name.startsWith(`${BOOKMARK_PREFIX}ID_`);
}

export function marksFromBookmarkName(name) {
  if (!name || !name.startsWith(BOOKMARK_PREFIX)) return null;
  if (isViewIdBookmarkName(name)) return null;
  const part = name.slice(BOOKMARK_PREFIX.length);
  if (!part) return null;
  try {
    return part
      .split("_")
      .map((h) => String.fromCodePoint(parseInt(h, 16)))
      .join("");
  } catch {
    return null;
  }
}

export function findClusters(text) {
  const out = [];
  if (!text) return out;
  CLUSTER_RE.lastIndex = 0;
  let match;
  while ((match = CLUSTER_RE.exec(text)) !== null) {
    out.push({
      baseChar: match[1],
      marks: normalizeMarks(match[2]),
      start: match.index,
      end: match.index + match[0].length,
    });
  }
  return out;
}

export function exportPlainText(text) {
  return text || "";
}

const OBJECT_REPLACEMENT = "\uFFFC";

/**
 * Replace one rendered view (base + box / object char / display glyphs) with base + Unicode marks.
 * Does not mutate Word — used for clipboard export only.
 */
export function substituteKaeritenViewInText(text, baseChar, marks, displayText) {
  if (!text || !baseChar || !marks) return text;
  const canonical = baseChar + normalizeMarks(marks);
  if (text.includes(canonical)) return text;

  const display = String(displayText ?? "").replace(/\r/g, "");
  const lines = display.split("\n").filter((l) => l.length > 0);
  const variants = new Set();
  if (display) variants.add(baseChar + display);
  if (lines.length) {
    variants.add(baseChar + lines.join(""));
    variants.add(baseChar + lines.join("\u000b"));
  }
  const compact = display.replace(/\s/g, "");
  if (compact) variants.add(baseChar + compact);
  variants.add(baseChar + OBJECT_REPLACEMENT);

  for (const needle of variants) {
    if (needle.length > baseChar.length && text.includes(needle)) {
      return text.replace(needle, canonical);
    }
  }

  let idx = 0;
  while (idx < text.length) {
    const at = text.indexOf(baseChar, idx);
    if (at < 0) break;
    const after = at + baseChar.length;
    if (after < text.length && text[after] === OBJECT_REPLACEMENT) {
      return text.slice(0, after) + marks + text.slice(after + 1);
    }
    idx = at + 1;
  }
  return text;
}

/** End index in plain text of rendered view span (exclusive); keeps following kanji. */
export function findExportSpanEnd(text, afterBase, displayText) {
  let end = afterBase;
  const display = String(displayText ?? "").replace(/\r/g, "");
  const compact = display.replace(/\s/g, "");
  const lines = display.split("\n").filter((l) => l.length > 0);

  while (end < text.length) {
    const ch = text[end];
    if (ch === OBJECT_REPLACEMENT) {
      end += 1;
      continue;
    }
    if (compact && text.slice(end, end + compact.length) === compact) {
      end += compact.length;
      continue;
    }
    if (display && text.slice(end, end + display.length) === display) {
      end += display.length;
      continue;
    }
    if (lines.length > 1 && text.slice(end, end + lines.join("").length) === lines.join("")) {
      end += lines.join("").length;
      continue;
    }
    break;
  }
  return end;
}

/**
 * Insert Unicode marks at known offsets (when Word selection text omits the inline box).
 * @param {Array<{ index: number, baseChar: string, marks: string, displayText?: string }>} views
 */
export function spliceCanonicalViewsIntoText(rawText, views) {
  let text = String(rawText ?? "").replace(/\r/g, "");
  const sorted = [...views]
    .filter((v) => v.index >= 0 && v.baseChar && v.marks)
    .sort((a, b) => b.index - a.index);

  for (const { index, baseChar, marks, displayText } of sorted) {
    const normMarks = normalizeMarks(marks);
    const canonical = baseChar + normMarks;
    const afterBase = index + baseChar.length;
    if (text.slice(index, afterBase + normMarks.length) === canonical) {
      continue;
    }
    const end = findExportSpanEnd(text, afterBase, displayText);
    text = text.slice(0, index) + canonical + text.slice(end);
  }
  return text;
}

/**
 * Apply view substitutions from end of string toward start (stable indices).
 */
export function buildCanonicalPlainText(rawText, viewTuples) {
  let text = String(rawText ?? "").replace(/\r/g, "");
  const sorted = [...viewTuples].sort(
    (a, b) => (b.position ?? -1) - (a.position ?? -1)
  );
  for (const { baseChar, marks, displayText } of sorted) {
    text = substituteKaeritenViewInText(text, baseChar, marks, displayText);
  }

  const forSplice = viewTuples
    .filter((t) => t.index != null && t.index >= 0)
    .map((t) => ({
      index: t.index,
      baseChar: t.baseChar,
      marks: t.marks,
      displayText: t.displayText,
    }));
  if (forSplice.length) {
    text = spliceCanonicalViewsIntoText(text, forSplice);
  }
  return text;
}

function xmlEscape(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function latexEscape(s) {
  let out = "";
  for (const ch of s) {
    if ("\\{}#$%&_~^".includes(ch)) out += "\\" + ch;
    else out += ch;
  }
  return out;
}

export function mappingByChar(mappingData) {
  const byChar = {};
  if (!mappingData?.marks) return byChar;
  for (const entry of mappingData.marks) {
    if (entry.char) byChar[entry.char] = entry;
  }
  return byChar;
}

export function glyphsForMarks(marks, byChar) {
  const chars = [...marks];
  chars.sort((a, b) => {
    const oa = Number(byChar[a]?.stack_order ?? 0);
    const ob = Number(byChar[b]?.stack_order ?? 0);
    if (oa !== ob) return oa - ob;
    return marks.indexOf(a) - marks.indexOf(b);
  });
  return chars.map((c) => byChar[c]?.display_glyph ?? c).join("\n");
}

/** Compare content-control text to mapping (strip spaces / soft breaks). */
export function normalizeDisplayKey(text) {
  return (text || "")
    .replace(/\s+/g, "")
    .replace(/\u000b/g, "")
    .replace(/\u2028/g, "");
}

/** Marks run text for comparing a Word range to expected ㆒㆑ (drops \\r and whitespace). */
export function normalizeMarksRun(text) {
  return (text || "").replace(/\r/g, "").replace(/\s/g, "");
}

/** Reverse lookup: stacked display glyphs (一上) → source marks (㆒㆖). */
export function buildDisplayToMarksMap(byChar, maxCompound = 3) {
  const markList = Object.keys(byChar).filter((c) =>
    /[\u3190-\u319f]/.test(c)
  );
  const lookup = new Map();
  const register = (marks) => {
    const key = normalizeDisplayKey(glyphsForMarks(marks, byChar));
    if (key) lookup.set(key, marks);
  };
  for (const a of markList) register(a);
  if (maxCompound >= 2) {
    for (const a of markList) {
      for (const b of markList) register(a + b);
    }
  }
  if (maxCompound >= 3) {
    for (const a of markList) {
      for (const b of markList) {
        for (const c of markList) register(a + b + c);
      }
    }
  }
  return lookup;
}

/** How many characters of `text` normalize to `displayKey` (includes soft breaks). */
export function rawLengthForNormalizedPrefix(text, displayKey) {
  if (!text || !displayKey) return 0;
  for (let i = 1; i <= text.length; i++) {
    if (normalizeDisplayKey(text.slice(0, i)) === displayKey) return i;
  }
  return 0;
}

/**
 * After a base kanji, match a known rendered view (display glyphs only).
 * Used when Word Mac unwraps content controls and leaves plain small text.
 */
export function matchDisplayViewAfterBase(text, offset, displayLookup) {
  if (!text || offset < 0 || offset >= text.length || !displayLookup?.size) {
    return null;
  }
  const baseChar = text[offset];
  if (!baseChar || /[\u3190-\u319f\s]/.test(baseChar)) return null;
  const rest = text.slice(offset + 1);
  if (/^[\u3190-\u319f]/.test(rest)) return null;
  const norm = normalizeDisplayKey(rest);
  const keys = [...displayLookup.keys()].filter((k) => k.length > 0);
  keys.sort((a, b) => b.length - a.length);
  for (const displayKey of keys) {
    if (!norm.startsWith(displayKey)) continue;
    const rawLen = rawLengthForNormalizedPrefix(rest, displayKey);
    if (rawLen <= 0) continue;
    return {
      baseChar,
      marks: displayLookup.get(displayKey),
      displayKey,
      displayRaw: rest.slice(0, rawLen),
    };
  }
  return null;
}

/** Plain-text clusters: base + marinaMoji display glyphs (not Unicode ㆒…). */
export function findOrphanViewClusters(text, displayLookup) {
  if (!text || !displayLookup?.size) return [];
  const out = [];
  let i = 0;
  while (i < text.length) {
    const hit = matchDisplayViewAfterBase(text, i, displayLookup);
    if (hit) {
      out.push({
        baseChar: hit.baseChar,
        marks: hit.marks,
        displayKey: hit.displayKey,
        displayRaw: hit.displayRaw,
        start: i,
        end: i + 1 + hit.displayRaw.length,
      });
      i = i + 1 + hit.displayRaw.length;
    } else {
      i += 1;
    }
  }
  return out;
}

/** True only for controls this add-in created (not any small レ/一 in the document). */
export function isMarinaMojiTaggedControl(cc, sourcePrefix) {
  const tag = (cc.tag || "").trim();
  if (tag.startsWith(sourcePrefix)) return true;
  if (tag && /marinamoji/i.test(tag) && /source=/i.test(tag)) return true;
  const title = (cc.title || "").trim();
  return /^[\u3190-\u319f]+$/.test(title);
}

/**
 * Resolve canonical marks from a marinaMoji content control (Tag or Title only).
 * @param {string} sourcePrefix e.g. MARINAMOJI:source=
 */
export function resolveMarksFromControl(
  cc,
  displayLookup,
  displayText,
  sourcePrefix
) {
  if (!isMarinaMojiTaggedControl(cc, sourcePrefix)) {
    return null;
  }
  const tag = (cc.tag || "").trim();
  if (tag.startsWith(sourcePrefix)) {
    const fromTag = tag.slice(sourcePrefix.length).replace(/\s/g, "");
    if (fromTag) return fromTag;
  }
  const loose = tag.match(/source=([\u3190-\u319f]+)/i);
  if (loose) return loose[1];
  if (/marinamoji/i.test(tag)) {
    const tail = tag.replace(/^.*source=/i, "").replace(/\s/g, "");
    if (tail && /^[\u3190-\u319f]+$/.test(tail)) return tail;
  }
  const title = (cc.title || "").trim();
  if (title && /^[\u3190-\u319f]+$/.test(title)) return title;
  if (displayLookup) {
    const key = normalizeDisplayKey(displayText);
    if (key && displayLookup.has(key)) return displayLookup.get(key);
  }
  return null;
}

function teiBodyContent(text) {
  if (!text) return "";
  const parts = [];
  let pos = 0;
  for (const { baseChar, marks, start, end } of findClusters(text)) {
    if (start > pos) parts.push(xmlEscape(text.slice(pos, start)));
    parts.push(
      `<kanbun char="${xmlEscape(baseChar)}" kaeriten="${xmlEscape(marks)}"/>`
    );
    pos = end;
  }
  if (pos < text.length) parts.push(xmlEscape(text.slice(pos)));
  return parts.join("");
}

export function exportTeiFragment(text) {
  const body = teiBodyContent(text);
  if (!body) return "";
  return `<p xml:lang="ja-Hani">${body}</p>`;
}

export function exportTeiXml(text, title = "marinaMoji kaeriten export") {
  const body = teiBodyContent(text);
  const titleEsc = xmlEscape(title);
  return (
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<TEI xmlns="http://www.tei-c.org/ns/1.0">\n' +
    "  <teiHeader>\n" +
    "    <fileDesc>\n" +
    "      <titleStmt>\n" +
    `        <title>${titleEsc}</title>\n` +
    "      </titleStmt>\n" +
    "    </fileDesc>\n" +
    "  </teiHeader>\n" +
    "  <text>\n" +
    "    <body>\n" +
    `      <p xml:lang="ja-Hani">${body}</p>\n` +
    "    </body>\n" +
    "  </text>\n" +
    "</TEI>\n"
  );
}

export function exportTeiForClipboard(text, fullDocument = false) {
  if (fullDocument) return exportTeiXml(text);
  return exportTeiFragment(text);
}

function latexBody(text, byChar) {
  if (!text) return "";
  const parts = [];
  let pos = 0;
  for (const { baseChar, marks, start, end } of findClusters(text)) {
    if (start > pos) parts.push(latexEscape(text.slice(pos, start)));
    parts.push(
      `{${latexEscape(baseChar)}}\\marinamojiKaeriten{${latexEscape(marks)}}`
    );
    pos = end;
  }
  if (pos < text.length) parts.push(latexEscape(text.slice(pos)));
  return parts.join("");
}

export function exportLatexFragment(text, mappingData = null) {
  const byChar = mappingByChar(mappingData);
  const body = latexBody(text, byChar);
  const lines = [
    "% marinaMoji kaeriten — paste into a document that defines \\marinamojiKaeriten",
    "% \\newcommand{\\marinamojiKaeriten}[1]{{\\small #1}}",
  ];
  if (Object.keys(byChar).length && findClusters(text).length) {
    lines.push(
      "% Display glyphs: " + plainWithDisplayGlyphs(text, byChar)
    );
  }
  lines.push(body);
  return lines.join("\n") + "\n";
}

export function exportLatex(text, mappingData = null) {
  const byChar = mappingByChar(mappingData);
  const body = latexBody(text, byChar);
  let displayHint = "";
  if (Object.keys(byChar).length && findClusters(text).length) {
    displayHint =
      "% Display glyphs: " + plainWithDisplayGlyphs(text, byChar) + "\n";
  }
  return (
    "% marinaMoji kaeriten export — compile with xelatex or lualatex\n" +
    "\\documentclass{article}\n" +
    "\\usepackage{fontspec}\n" +
    "\\usepackage{xeCJK}\n" +
    "\\newcommand{\\marinamojiKaeriten}[1]{{\\small #1}}\n" +
    displayHint +
    "\\begin{document}\n\n" +
    body +
    "\n\n\\end{document}\n"
  );
}

export function exportLatexForClipboard(text, mappingData = null, fullDocument = false) {
  if (fullDocument) return exportLatex(text, mappingData);
  return exportLatexFragment(text, mappingData);
}

function plainWithDisplayGlyphs(text, byChar) {
  const parts = [];
  let pos = 0;
  for (const { baseChar, marks, start, end } of findClusters(text)) {
    if (start > pos) parts.push(text.slice(pos, start));
    parts.push(baseChar + glyphsForMarks(marks, byChar));
    pos = end;
  }
  if (pos < text.length) parts.push(text.slice(pos));
  return parts.join("");
}
