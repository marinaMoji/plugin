// Composed-character size and baseline shift follow the host font size.
// Run: node tests/test_composed.mjs
import assert from "node:assert/strict";
import { composedMetrics, isComposedPicture, INK_SCALE, DROP_EM } from "../src/wordComposedInsert.js";

const m = composedMetrics(11);
assert.ok(Math.abs(m.sizePt - 11 * INK_SCALE) < 1e-9);
assert.ok(Math.abs(m.shiftPt + 11 * DROP_EM) < 1e-9);
assert.ok(Math.abs(composedMetrics(44).sizePt / composedMetrics(11).sizePt - 4) < 1e-9);
assert.ok(composedMetrics(12).shiftPt < 0, "lowered");
assert.ok(isComposedPicture({ altTextTitle: "marinaMoji composed character" }));
assert.ok(isComposedPicture({ altTextTitle: "", altTextDescription: "MARINAMOJI:ids=⿰木巻" }));
assert.ok(!isComposedPicture({ altTextTitle: "photo", altTextDescription: "a cat" }));
console.log("composed metrics ok");
