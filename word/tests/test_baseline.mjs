// Horizontal kaeriten pictures: shift = -(bottom line + ink inset) * host size, with a
// per-font bottom line. Run: node tests/test_baseline.mjs
import assert from "node:assert/strict";
import { bottomLineEm, inlinePictureBaselineShiftPt } from "../src/wordInlinePicture.js";

const base = { imageBottomLineEm: 0.06, imageFontBottomLineEm: { "Songti SC": 0.122 }, imageInkInsetEm: 0.066 };

// default font
assert.ok(Math.abs(inlinePictureBaselineShiftPt(24, { ...base, hostFontName: "Hiragino Mincho ProN" }) - -(0.126 * 24)) < 1e-9);
// per-font override, case-insensitive prefix
assert.equal(bottomLineEm({ ...base, hostFontName: "songti sc" }), 0.122);
assert.ok(Math.abs(inlinePictureBaselineShiftPt(12, { ...base, hostFontName: "Songti SC" }) - -(0.188 * 12)) < 1e-9);
// scales with the host size
assert.ok(Math.abs(inlinePictureBaselineShiftPt(48, base) / inlinePictureBaselineShiftPt(12, base) - 4) < 1e-9);
// no bottom-line setting: the old fixed shift (-5 pt at 12 pt) applies
assert.equal(inlinePictureBaselineShiftPt(12, { imageBaselineShiftPt: -5 }), -5);
// vertical text keeps its own shift
assert.equal(inlinePictureBaselineShiftPt(12, { ...base, vertical: true, imageVerticalBaselineShiftPt: 3 }), 3);
// vertical text: the picture's left edge meets the characters' left edge for any width
const v = { ...base, vertical: true, imageVerticalCenterEm: 0.458 };
const left = (host, w) => 0.458 * host + inlinePictureBaselineShiftPt(host, { ...v, pictureWidthPt: w }) - w / 2; // box-left minus ink-left at shift
for (const w of [0.42 * 24, 0.34 * 24, 0.92 * 24]) assert.ok(Math.abs(left(24, w)) < 1e-9);
assert.ok(Math.abs(inlinePictureBaselineShiftPt(24, { ...v, pictureWidthPt: 0.42 * 24 }) - -(0.248 * 24)) < 1e-9);
console.log("test_baseline: ok");
