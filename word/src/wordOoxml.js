/**
 * Inline kaeriten (wp:inline + wps:txbx) as WordprocessingML for Range.insertOoxml.
 * Replaces the whole cluster atomically (e.g. 問㆒㆑ → 問 + inline box).
 */

import { SOURCE_PREFIX } from "./exportCore.js";
import {
  boxMetricsFromHost,
  baselineShiftHalfPoints,
  inlineEffectExtentEmu,
  compoundLineSpacingPt,
} from "./wordBoxLayout.js";

const W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
const WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing";
const A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main";
const WPS_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape";
const PKG_NS = "http://schemas.microsoft.com/office/2006/xmlPackage";
const REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships";

const DOC_NS = [
  `xmlns:w="${W_NS}"`,
  `xmlns:wp="${WP_NS}"`,
  `xmlns:a="${A_NS}"`,
  `xmlns:wps="${WPS_NS}"`,
  `xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"`,
  `xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"`,
].join(" ");

let _shapeIdSeq = 0;

export function wordHasOoxmlApi() {
  try {
    if (
      typeof Office !== "undefined" &&
      Office.context?.requirements?.isSetSupported
    ) {
      return Office.context.requirements.isSetSupported("WordApi", "1.1");
    }
  } catch {
    /* host not ready */
  }
  return true;
}

function nextShapeId() {
  _shapeIdSeq += 1;
  const base = (Date.now() % 2000000000) + _shapeIdSeq;
  return Math.max(2, base);
}

/** Points → EMU (English Metric Units). */
export function ptToEmu(pt) {
  return Math.max(1, Math.round(pt * 12700));
}

export function escapeXml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Six-digit RRGGBB for DrawingML a:srgbClr (no #). */
export function normalizeSrgbHex(color) {
  let s = String(color ?? "FFFFFF")
    .replace(/^#/, "")
    .trim()
    .toUpperCase();
  if (/^[0-9A-F]{3}$/.test(s)) {
    s = s
      .split("")
      .map((c) => c + c)
      .join("");
  }
  if (!/^[0-9A-F]{6}$/.test(s)) return "FFFFFF";
  return s;
}

/**
 * Shape fill + outline inside wps:spPr.
 * Default: no fill, no outline (publication-safe; geometry is wp:inline + bodyPr).
 * Optional Mac hack: word_mac_force_solid_fill + word_mac_fill_color (often FFFFFF).
 */
export function shapeSpPrFillLineXml(opts = {}) {
  if (opts.macForceSolidFill === true) {
    const hex = normalizeSrgbHex(opts.macFillColor ?? "FFFFFF");
    const fill = `<a:solidFill><a:srgbClr val="${hex}"/></a:solidFill>`;
    const ln =
      opts.macNoOutline !== false
        ? "<a:ln><a:noFill/></a:ln>"
        : `<a:ln w="6350"><a:solidFill><a:srgbClr val="B8C8E0"/></a:solidFill></a:ln>`;
    return `${fill}\n              ${ln}`;
  }
  return `<a:noFill/>
              <a:ln><a:noFill/></a:ln>`;
}

function boxSizeEmu(opts, glyphCount, hostPt) {
  const m = boxMetricsFromHost(hostPt, glyphCount, opts);
  return {
    cx: ptToEmu(m.widthPt),
    cy: ptToEmu(m.heightPt),
    fontHalfPt: Math.max(12, Math.round(m.fontPt * 2)),
    fontPt: m.fontPt,
    hostPt: m.hostPt,
  };
}

/** Line spacing in twips (exact) for soft breaks between stacked glyphs. */
function stackLineTwips(fontPt, hostPt, opts) {
  const linePt = compoundLineSpacingPt(fontPt, hostPt, opts);
  return Math.max(60, Math.round(linePt * 20));
}

function txbxJcXml(opts) {
  const gap = Number(opts?.boxExtraWidthRightPt ?? 0);
  return gap > 0 ? '<w:jc w:val="left"/>' : "";
}

function txbxContentXml(glyphText, layout, fontHalfPt, fontPt, opts) {
  const lines = glyphText.split("\n").filter((line) => line.length > 0);
  const rPr = `<w:rPr><w:sz w:val="${fontHalfPt}"/><w:szCs w:val="${fontHalfPt}"/></w:rPr>`;
  const jc = txbxJcXml(opts);

  if (layout === "row" || lines.length <= 1) {
    const pPr =
      `<w:pPr>${jc}<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>`;
    const text = lines.join("") || glyphText;
    return `<w:p>${pPr}<w:r>${rPr}<w:t xml:space="preserve">${escapeXml(text)}</w:t></w:r></w:p>`;
  }

  const lineTwips = stackLineTwips(fontPt, opts.hostFontPt ?? 12, opts);
  const pPr = `<w:pPr>${jc}<w:spacing w:before="0" w:after="0" w:line="${lineTwips}" w:lineRule="exact"/></w:pPr>`;
  const runs = lines
    .map((line, i) => {
      const br = i > 0 ? "<w:r><w:br/></w:r>" : "";
      return `${br}<w:r>${rPr}<w:t xml:space="preserve">${escapeXml(line)}</w:t></w:r>`;
    })
    .join("");
  return `<w:p>${pPr}${runs}</w:p>`;
}

function inlineDrawingRun(marks, glyphText, layout, opts, hostPt) {
  const glyphCount =
    glyphText.split("\n").filter((l) => l.length > 0).length || 1;
  const { cx, cy, fontHalfPt, fontPt } = boxSizeEmu(opts, glyphCount, hostPt);
  const shapeId = nextShapeId();
  const descr = escapeXml(SOURCE_PREFIX + marks);
  const layoutOpts = {
    ...opts,
    hostFontPt: hostPt,
    boxExtraWidthRightPt: opts?.boxExtraWidthRightPt,
  };
  const body = txbxContentXml(glyphText, layout, fontHalfPt, fontPt, layoutOpts);
  const anchor = "b";
  const shiftHp = baselineShiftHalfPoints(layoutOpts);
  const runPr = shiftHp
    ? `<w:rPr><w:position w:val="${shiftHp}"/></w:rPr>`
    : "";
  const pad = inlineEffectExtentEmu(opts);

  return `<w:r>${runPr}
  <w:drawing>
    <wp:inline distT="0" distB="0" distL="0" distR="0">
      <wp:extent cx="${cx}" cy="${cy}"/>
      <wp:effectExtent l="${pad}" t="${pad}" r="${pad}" b="${pad}"/>
      <wp:docPr id="${shapeId}" name="marinaMoji_${shapeId}" descr="${descr}"/>
      <wp:cNvGraphicFramePr>
        <a:graphicFrameLocks noChangeAspect="1"/>
      </wp:cNvGraphicFramePr>
      <a:graphic>
        <a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
          <wps:wsp>
            <wps:cNvPr id="${shapeId}" name="marinaMoji_${shapeId}" descr="${descr}"/>
            <wps:cNvSpPr txBox="1"/>
            <wps:spPr>
              <a:xfrm>
                <a:off x="0" y="0"/>
                <a:ext cx="${cx}" cy="${cy}"/>
              </a:xfrm>
              <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
              ${shapeSpPrFillLineXml(opts)}
            </wps:spPr>
            <wps:txbx>
              <w:txbxContent>
                ${body}
              </w:txbxContent>
            </wps:txbx>
            <wps:bodyPr anchor="${anchor}" anchorCtr="1" vert="horz" spcFirstLastPara="0" lIns="0" tIns="0" rIns="0" bIns="0"/>
          </wps:wsp>
        </a:graphicData>
      </a:graphic>
    </wp:inline>
  </w:drawing>
</w:r>`;
}

/** Rich-text content control (simpler OOXML; second attempt if inline shape is rejected). */
function inlineSdtRun(marks, glyphText, layout, fontHalfPt) {
  const sdtId = nextShapeId();
  const tag = escapeXml(SOURCE_PREFIX + marks);
  const lines = glyphText.split("\n").filter((l) => l.length > 0);
  let inner = "";
  const rPr = `<w:rPr><w:sz w:val="${fontHalfPt}"/><w:szCs w:val="${fontHalfPt}"/></w:rPr>`;
  if (layout === "row" || lines.length <= 1) {
    inner = `<w:r>${rPr}<w:t xml:space="preserve">${escapeXml(lines.join("") || glyphText)}</w:t></w:r>`;
  } else {
    inner = lines
      .map((line, i) => {
        const br =
          i > 0 ? "<w:r><w:br/></w:r>" : "";
        return `${br}<w:r>${rPr}<w:t xml:space="preserve">${escapeXml(line)}</w:t></w:r>`;
      })
      .join("");
  }
  return `<w:r>
  <w:sdt>
    <w:sdtPr>
      <w:tag w:val="${tag}"/>
      <w:alias w:val="${escapeXml(marks)}"/>
      <w:id w:val="${sdtId}"/>
      <w:text/>
    </w:sdtPr>
    <w:sdtContent>
      ${inner}
    </w:sdtContent>
  </w:sdt>
</w:r>`;
}

function baseRun(baseChar) {
  return `<w:r><w:t xml:space="preserve">${escapeXml(baseChar)}</w:t></w:r>`;
}

/** Plain Unicode cluster (問㆒㆑) for insertOoxml unrender on Mac inline boxes. */
export function buildPlainClusterOoxml(baseChar, marks) {
  const text = String(baseChar || "") + String(marks || "").replace(/\s/g, "");
  return wrapOoxmlPackage(
    `<w:r><w:t xml:space="preserve">${escapeXml(text)}</w:t></w:r>`
  );
}

/** Microsoft pkg:package wrapper (requires /_rels/.rels per Word insertOoxml samples). */
export function wrapOoxmlPackage(paragraphInner) {
  return `<?xml version="1.0" standalone="yes"?>
<pkg:package xmlns:pkg="${PKG_NS}">
  <pkg:part pkg:name="/_rels/.rels" pkg:contentType="application/vnd.openxmlformats-package.relationships+xml" pkg:padding="512">
    <pkg:xmlData>
      <Relationships xmlns="${REL_NS}">
        <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
      </Relationships>
    </pkg:xmlData>
  </pkg:part>
  <pkg:part pkg:name="/word/document.xml" pkg:contentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml">
    <pkg:xmlData>
      <w:document ${DOC_NS}>
        <w:body>
          <w:p>
            ${paragraphInner}
          </w:p>
        </w:body>
      </w:document>
    </pkg:xmlData>
  </pkg:part>
</pkg:package>`;
}

/**
 * Build OOXML variants (shape first, then content control). Caller tries each with insertOoxml.
 */
export function buildClusterReplaceOoxmlVariants(
  baseChar,
  marks,
  glyphText,
  layout,
  opts,
  hostFontPt = 12
) {
  const glyphCount =
    glyphText.split("\n").filter((l) => l.length > 0).length || 1;
  const built = boxSizeEmu(opts, glyphCount, hostFontPt);
  const fontHalfPt = Math.max(12, Math.round(built.fontPt * 2));
  const shapeRuns = `${baseRun(baseChar)}${inlineDrawingRun(marks, glyphText, layout, opts, hostFontPt)}`;
  const sdtRuns = `${baseRun(baseChar)}${inlineSdtRun(marks, glyphText, layout, fontHalfPt)}`;
  return [
    { kind: "inlineShape", ooxml: wrapOoxmlPackage(shapeRuns) },
    { kind: "contentControl", ooxml: wrapOoxmlPackage(sdtRuns) },
  ];
}

/** @deprecated Use buildClusterReplaceOoxmlVariants */
export function buildClusterReplaceOoxml(
  baseChar,
  marks,
  glyphText,
  layout,
  opts,
  hostFontPt = 12
) {
  return buildClusterReplaceOoxmlVariants(
    baseChar,
    marks,
    glyphText,
    layout,
    opts,
    hostFontPt
  )[0].ooxml;
}
