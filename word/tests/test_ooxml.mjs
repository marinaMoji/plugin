#!/usr/bin/env node
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SOURCE_PREFIX } from "../src/exportCore.js";
import {
  buildClusterReplaceOoxml,
  buildClusterReplaceOoxmlVariants,
  buildPlainClusterOoxml,
  wrapOoxmlPackage,
  escapeXml,
  ptToEmu,
  shapeSpPrFillLineXml,
  normalizeSrgbHex,
} from "../src/wordOoxml.js";
import { sanityCheckOoxml } from "../src/wordOoxmlProbe.js";
import {
  compoundBoxWidthPt,
  baselineShiftHalfPoints,
  resolveBaselineShiftPt,
  parseFontSizeRatio,
  compoundLineSpacingPt,
  compoundBoxHeightPt,
  effectiveFrameWidthPt,
  boxMetricsFromHost,
  hmmToPt,
  boxExtraWidthRightPt,
} from "../src/wordBoxLayout.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const mapping = JSON.parse(
  fs.readFileSync(path.join(__dirname, "../../mapping.json"), "utf8")
);
const r = mapping.rendering || {};
const lo = r.libreoffice_frame || {};
const inline = r.word_inline_textbox || {};
const opts = {
  fontSizeRatio: parseFontSizeRatio(inline.font_size_ratio ?? "12:5"),
  minFontSizePt: inline.min_font_size_pt ?? 6,
  compoundLineSpacingPt: inline.compound_line_spacing_pt ?? 4,
  compoundBoxPaddingPt: inline.compound_box_padding_pt ?? 0.12,
  frameWidthHmm: inline.frame_width_hmm ?? lo.frame_width_hmm ?? 180,
  frameWidthReferencePt: inline.frame_width_reference_pt ?? 12,
  frameHeightPaddingHmm: inline.frame_height_padding_hmm ?? 80,
  baselineShiftPt: resolveBaselineShiftPt(inline),
  boxExtraWidthRightPt:
    inline.box_extra_width_right_pt != null
      ? Number(inline.box_extra_width_right_pt)
      : 0,
};

assert.equal(escapeXml("a&b"), "a&amp;b");
assert.equal(ptToEmu(1), 12700);

const pkg = wrapOoxmlPackage("<w:r><w:t>x</w:t></w:r>");
assert.ok(pkg.includes("/_rels/.rels"));
assert.ok(pkg.includes("Relationships"));

const variants = buildClusterReplaceOoxmlVariants(
  "問",
  "㆒㆑",
  "一\nレ",
  "stack",
  opts,
  12
);
assert.equal(variants.length, 2);
const xml = variants[0].ooxml;
const plain = buildPlainClusterOoxml("問", "㆒㆑");
assert.ok(plain.includes(">問㆒㆑</w:t>"));

assert.ok(xml.includes("<pkg:package"));
assert.ok(xml.includes("wp:inline"));
assert.ok(xml.includes("wps:txbx"));
assert.ok(xml.includes(">問</w:t>"));
assert.ok(xml.includes(">一</w:t>"));
assert.ok(xml.includes(">レ</w:t>"));
assert.ok(xml.includes(escapeXml(SOURCE_PREFIX + "㆒㆑")));
assert.ok(!xml.includes("wp14:anchorId"));
assert.ok(xml.includes('effectExtent l="0"'));
if (opts.boxExtraWidthRightPt > 0) {
  assert.ok(xml.includes('w:jc w:val="left"'));
  assert.ok(
    effectiveFrameWidthPt(12, opts) >
      effectiveFrameWidthPt(12, { ...opts, boxExtraWidthRightPt: 0 })
  );
  assert.equal(boxExtraWidthRightPt(12, opts), 2.5);
  assert.equal(boxExtraWidthRightPt(18, opts), 3.75);
}
assert.ok(xml.includes("<a:noFill/>"));
assert.ok(!xml.includes("EEF4FC"));
assert.ok(shapeSpPrFillLineXml(opts).includes("<a:noFill/>"));

const hackOpts = {
  ...opts,
  macForceSolidFill: true,
  macFillColor: "FFFFFF",
  macNoOutline: true,
};
const hackXml = buildClusterReplaceOoxmlVariants(
  "問",
  "㆒㆑",
  "一\nレ",
  "stack",
  hackOpts,
  12
)[0].ooxml;
assert.ok(hackXml.includes('<a:srgbClr val="FFFFFF"/>'));
assert.ok(hackXml.includes("<a:ln><a:noFill/></a:ln>"));
assert.equal(normalizeSrgbHex("#fff"), "FFFFFF");

const geomOpts = {
  ...opts,
  baselineShiftPt: -4,
  hostFontPt: 12,
};
const geomXml = buildClusterReplaceOoxmlVariants(
  "問",
  "㆒㆑",
  "一\nレ",
  "stack",
  geomOpts,
  12
)[0].ooxml;
assert.ok(geomXml.includes('w:position w:val="-8"'));

const legacy = buildClusterReplaceOoxml("問", "㆒㆑", "一\nレ", "stack", opts, 12);
assert.ok(legacy.includes("wp:inline"));

const row = buildClusterReplaceOoxml("說", "㆒㆑", "一\nレ", "row", opts, 14);
assert.ok(row.includes(">一レ</w:t>") || row.includes(">一</w:t>"));

assert.equal(parseFontSizeRatio("12:5"), 5 / 12);
assert.equal(parseFontSizeRatio(0.42), 0.42);
assert.equal(compoundLineSpacingPt(5, 12, opts), 4);
assert.equal(compoundLineSpacingPt(5, 18, opts), 6);

const w12 = effectiveFrameWidthPt(12, opts);
const w24 = effectiveFrameWidthPt(24, opts);
assert.ok(w24 > w12, "width should scale with host like LO");

const m12 = boxMetricsFromHost(12, 2, opts);
const m18 = boxMetricsFromHost(18, 2, opts);
assert.ok(m18.widthPt > m12.widthPt);
assert.ok(m18.heightPt >= m12.heightPt);
assert.equal(m12.fontPt, 6);
assert.equal(boxMetricsFromHost(24, 2, opts).fontPt, 10);

const structural = sanityCheckOoxml(xml);
assert.equal(structural.ok, true, structural.errors?.join("; "));
assert.equal(sanityCheckOoxml("").ok, false);
assert.equal(sanityCheckOoxml("<pkg:package/>").ok, false);

console.log("All OOXML build tests passed.");
