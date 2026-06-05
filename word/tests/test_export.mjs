#!/usr/bin/env node
/**
 * Export tests (no Word required). Mirrors libreoffice/tests/test_export.py
 */
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  findClusters,
  exportPlainText,
  exportTeiXml,
  exportTeiFragment,
  exportTeiForClipboard,
  exportLatexFragment,
  exportLatexForClipboard,
  mappingByChar,
  glyphsForMarks,
  buildDisplayToMarksMap,
  findOrphanViewClusters,
  normalizeDisplayKey,
  normalizeMarksRun,
  rawLengthForNormalizedPrefix,
  resolveMarksFromControl,
  bookmarkNameForMarks,
  marksFromBookmarkName,
  encodeKaeritenSourceTag,
  parseKaeritenSourceTag,
  isViewIdBookmarkName,
  substituteKaeritenViewInText,
  buildCanonicalPlainText,
  spliceCanonicalViewsIntoText,
  findExportSpanEnd,
} from "../src/exportCore.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const mapping = JSON.parse(
  fs.readFileSync(path.join(__dirname, "../../mapping.json"), "utf8")
);

assert.equal(exportPlainText("說㆒㆑者"), "說㆒㆑者");

const clusters = findClusters("說㆒㆑者");
assert.equal(clusters.length, 1);
assert.equal(clusters[0].baseChar, "說");
assert.equal(clusters[0].marks, "㆒㆑");

const xml = exportTeiXml("說㆒㆑者");
assert.ok(xml.includes('<kanbun char="說" kaeriten="㆒㆑"/>'));
assert.ok(xml.includes("者"));

assert.ok(exportTeiXml("a & b").includes("&amp;"));

const tex = exportLatexFragment("說㆒㆑者", mapping);
assert.ok(tex.includes("\\marinamojiKaeriten"));

const frag = exportTeiForClipboard("說㆒㆑者", false);
assert.ok(frag.startsWith("<p "));
const full = exportTeiForClipboard("說㆒㆑者", true);
assert.ok(full.includes("<TEI "));

const latexFrag = exportLatexForClipboard("說㆒㆑者", mapping, false);
assert.ok(latexFrag.includes("% marinaMoji"));
const latexFull = exportLatexForClipboard("說㆒㆑者", mapping, true);
assert.ok(latexFull.includes("\\documentclass"));

const byChar = mappingByChar(mapping);
assert.ok(byChar["㆒"]);

const compound = findClusters("說㆒㆖者");
assert.equal(compound[0].marks, "㆒㆖");
assert.equal(glyphsForMarks("㆒㆖", byChar), "一\n上");

const eol = findClusters("者㆒㆖");
assert.equal(eol.length, 1);
assert.equal(eol[0].baseChar, "者");

const splitMarks = findClusters("漢㆒\n㆖字");
assert.equal(splitMarks.length, 1);
assert.equal(splitMarks[0].baseChar, "漢");
assert.equal(splitMarks[0].marks, "㆒㆖");

assert.equal(normalizeMarksRun("㆒㆑"), "㆒㆑");
assert.equal(normalizeMarksRun("㆒\n㆑"), "㆒㆑");
assert.equal(normalizeMarksRun("問㆒㆑"), "問㆒㆑");

assert.equal(
  substituteKaeritenViewInText("問\uFFFC題", "問", "㆒㆑", "一\nレ"),
  "問㆒㆑題"
);
assert.equal(
  substituteKaeritenViewInText("問一レ題", "問", "㆒㆑", "一\nレ"),
  "問㆒㆑題"
);
assert.equal(
  buildCanonicalPlainText("問\uFFFC題", [
    { baseChar: "問", marks: "㆒㆑", displayText: "一\nレ", index: 0, position: 0 },
  ]),
  "問㆒㆑題"
);
assert.equal(
  spliceCanonicalViewsIntoText("問題", [
    { index: 0, baseChar: "問", marks: "㆒㆑", displayText: "一\nレ" },
  ]),
  "問㆒㆑題"
);
assert.equal(findExportSpanEnd("問\uFFFC題", 1, "一\nレ"), 2);
assert.equal(findExportSpanEnd("問題", 1, "一\nレ"), 1);

const lookup = buildDisplayToMarksMap(byChar);
assert.equal(lookup.get(normalizeDisplayKey("一\n上")), "㆒㆖");
assert.equal(
  resolveMarksFromControl(
    { tag: "MARINAMOJI:source=㆒㆖", title: "㆒㆖" },
    lookup,
    "一\n上",
    "MARINAMOJI:source="
  ),
  "㆒㆖"
);
assert.equal(
  resolveMarksFromControl(
    { tag: "", title: "" },
    lookup,
    "レ",
    "MARINAMOJI:source="
  ),
  null
);
assert.equal(
  resolveMarksFromControl(
    { tag: "MARINAMOJI:source=㆒㆑", title: "㆒㆑" },
    lookup,
    "一\nレ",
    "MARINAMOJI:source="
  ),
  "㆒㆑"
);

assert.equal(bookmarkNameForMarks("㆑"), "_MMK_3191");
assert.equal(marksFromBookmarkName("_MMK_3192_3196"), "㆒㆖");

assert.equal(
  parseKaeritenSourceTag("MARINAMOJI:kaeriten:id=abc;source=㆒㆑")?.marks,
  "㆒㆑"
);
assert.equal(
  parseKaeritenSourceTag("MARINAMOJI:kaeriten:id=abc;source=㆒㆑")?.viewId,
  "abc"
);
assert.equal(encodeKaeritenSourceTag("㆑", "x1").includes("id=x1"), true);
assert.equal(isViewIdBookmarkName("_MMK_ID_v1"), true);
assert.equal(marksFromBookmarkName("_MMK_ID_v1"), null);

const {
  orderedGlyphs,
  imageMetricsFromHost,
  inlinePictureBaselineShiftPt,
  imageOptsForFlow,
  patchKaeritenPictureOoxml,
} = await import("../src/wordInlinePicture.js");
const { kaeritenImageUseRowLayout, ooxmlIndicatesVerticalFlow } = await import(
  "../src/wordLayout.js"
);
assert.equal(ooxmlIndicatesVerticalFlow('<w:pPr><w:textDirection w:val="tbRl"/></w:pPr>'), true);
assert.equal(ooxmlIndicatesVerticalFlow('<w:sectPr><w:textDirection w:val="tbRlV"/></w:sectPr>'), true);
assert.equal(ooxmlIndicatesVerticalFlow('<w:textDirection w:val="lrTb"/>'), false);
assert.equal(inlinePictureBaselineShiftPt(12, { imageBaselineShiftPt: -5 }), -5);
assert.equal(
  Math.round(inlinePictureBaselineShiftPt(18, { imageBaselineShiftPt: -4 }) * 10) / 10,
  -6
);
assert.equal(inlinePictureBaselineShiftPt(12, { vertical: true, imageVerticalBaselineShiftPt: 6 }), 6);
assert.equal(inlinePictureBaselineShiftPt(12, { vertical: true, imageBaselineShiftPt: -5 }), -5);
assert.equal(kaeritenImageUseRowLayout(false, 2, { imageRow: false }), false);
assert.equal(kaeritenImageUseRowLayout(true, 2, {}), true);
assert.equal(imageOptsForFlow({ imageRow: false }, true, 2).row, true);
assert.equal(imageOptsForFlow({ imageRow: false }, false, 2).row, false);
const vertRow = imageMetricsFromHost(12, 2, {
  row: true,
  vertical: true,
  imageCompoundGlyphRatio: 0.34,
  imageCompoundLineGapRatio: -0.08,
});
assert.equal(vertRow.rows, 1);
assert.equal(vertRow.columns, 2);
assert.equal(vertRow.verticalStrip, false);
assert.equal(Math.round(vertRow.widthPt), 8);
assert.equal(Math.round(vertRow.heightPt), 4);
const vertCrop = imageMetricsFromHost(12, 1, { vertical: true });
assert.equal(vertCrop.verticalStrip, false);
assert.equal(Math.round(vertCrop.widthPt), 5);
assert.equal(Math.round(vertCrop.heightPt), 5);
const touchStack = imageMetricsFromHost(12, 2, {
  vertical: true,
  imageCompoundTouch: true,
  imageCompoundGlyphRatio: 0.34,
  imageCompoundTouchOverlapRatio: 0.72,
});
assert.equal(touchStack.rows, 2);
assert.equal(Math.round(touchStack.heightPt), 5);

assert.equal(encodeKaeritenSourceTag("㆑", "t1", "v").includes("flow=v"), true);
const patched = patchKaeritenPictureOoxml(
  '<w:r><w:drawing><wp:inline><wp:extent cx="1000" cy="500"/></wp:inline></w:drawing></w:r>',
  { shiftHalfPoints: -10, wideCxEmu: 20000, distREmu: 30000 }
);
assert.equal(patched.includes('w:val="-10"'), true);
assert.equal(patched.includes('cx="20000"'), true);
assert.equal(patched.includes('distR="30000"'), true);
assert.deepEqual(orderedGlyphs("㆒㆑", byChar), ["一", "レ"]);
assert.deepEqual(orderedGlyphs("㆑", byChar), ["レ"]);
const single = imageMetricsFromHost(12, 1, {});
assert.equal(single.rows, 1);
assert.equal(single.columns, 1);
assert.equal(Math.round(single.widthPt), 5);
assert.equal(Math.round(single.contentHeightPt), 5);
assert.equal(Math.round(single.heightPt), 5);
assert.equal(Math.round(single.contentTopPt), 0);
const stack = imageMetricsFromHost(12, 2, {
  imageCompoundGlyphRatio: 0.34,
  imageCompoundLineGapRatio: -0.15,
});
assert.equal(stack.rows, 2);
assert.equal(Math.round(stack.contentHeightPt), 8);
assert.equal(Math.round(stack.heightPt), 8);
assert.equal(Math.round(stack.contentTopPt), 0);
const tall = imageMetricsFromHost(12, 3, {
  imageCompoundGlyphRatio: 0.34,
  imageCompoundLineGapRatio: -0.15,
});
assert.equal(Math.round(tall.contentHeightPt), 11);
assert.equal(Math.round(tall.heightPt), 11);
const row = imageMetricsFromHost(12, 2, { row: true });
assert.equal(row.columns, 2);
assert.equal(Math.round(row.widthPt), 10);

assert.equal(rawLengthForNormalizedPrefix("一\n上", "一上"), 3);
const orphan = findOrphanViewClusters("あのレ漢文", lookup);
assert.equal(orphan.length, 1);
assert.equal(orphan[0].baseChar, "の");
assert.equal(orphan[0].marks, "㆑");
assert.equal(findOrphanViewClusters("說㆒㆑", lookup).length, 0);

const { marksFromShape, isMarinaMojiTextBox } = await import(
  "../src/wordTextBox.js"
);
assert.equal(
  marksFromShape(
    { altTextDescription: "MARINAMOJI:source=㆒㆑", altTextTitle: "" },
    null,
    ""
  ),
  "㆒㆑"
);
assert.equal(isMarinaMojiTextBox({ altTextDescription: "MARINAMOJI:source=㆑" }), true);
assert.equal(isMarinaMojiTextBox({ altTextDescription: "レ" }), false);

console.log("All export tests passed.");
