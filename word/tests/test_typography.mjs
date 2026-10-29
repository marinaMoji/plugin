#!/usr/bin/env node
import assert from "node:assert/strict";
import {
  classifySelection,
  classifyRun,
  selectionCoversWholeParagraphText,
  OK,
  CONFIRM,
  REFUSE,
} from "../src/typography/tatechuyokoPolicy.js";
import {
  applyWarichuInOoxml,
  applyTatechuyokoInOoxml,
  clearEastAsianLayoutInOoxml,
  ooxmlHasWarichu,
  ooxmlHasTatechuyoko,
  ooxmlHasRuby,
} from "../src/typography/eastAsianLayoutOoxml.js";
import {
  buildRubyReplaceOoxml,
  unwrapRubyInOoxml,
} from "../src/typography/rubyOoxml.js";
import {
  applyFitTextInOoxml,
  clearFitTextInOoxml,
  ooxmlHasFitText,
} from "../src/typography/jidoriOoxml.js";
import {
  countGraphemes,
  fitTextTwipsForCells,
  initialN,
} from "../src/typography/jidoriMath.js";

const bareRun = `<?xml version="1.0"?>
<pkg:package xmlns:pkg="http://schemas.microsoft.com/office/2006/xmlPackage">
  <pkg:part pkg:name="/word/document.xml">
    <pkg:xmlData>
      <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:body><w:p><w:r><w:t>割り注は良い</w:t></w:r></w:p></w:body>
      </w:document>
    </pkg:xmlData>
  </pkg:part>
</pkg:package>`;

/* --- tate-chū-yoko policy --- */
assert.equal(classifySelection("12").verdict, OK);
assert.equal(classifySelection("AB").verdict, OK);
assert.equal(classifySelection("123").verdict, CONFIRM);
assert.equal(classifySelection("1").verdict, REFUSE);
assert.equal(classifySelection("令和").verdict, REFUSE);
assert.equal(classifySelection("12345").verdict, REFUSE);
assert.equal(classifyRun("12").kind, "digits");
assert.equal(
  selectionCoversWholeParagraphText("全文", "全文"),
  true
);
assert.equal(
  selectionCoversWholeParagraphText("注", "本文注残り"),
  false
);

/* --- warichū / tate OOXML --- */
const warichu = applyWarichuInOoxml(bareRun);
assert.ok(warichu.includes('w:combine="1"'));
assert.equal(ooxmlHasWarichu(warichu), true);
assert.equal(ooxmlHasTatechuyoko(warichu), false);

const tate = applyTatechuyokoInOoxml(bareRun);
assert.ok(tate.includes('w:vert="1"'));
assert.equal(ooxmlHasTatechuyoko(tate), true);

const cleared = clearEastAsianLayoutInOoxml(warichu);
assert.equal(ooxmlHasWarichu(cleared), false);
assert.ok(!cleared.includes("eastAsianLayout"));

/* --- ruby --- */
const rubyPkg = buildRubyReplaceOoxml("漢字", "かんじ", { basePt: 12 });
assert.ok(rubyPkg.includes("<w:ruby>"));
assert.ok(rubyPkg.includes(">かんじ</w:t>"));
assert.ok(rubyPkg.includes(">漢字</w:t>"));
assert.equal(ooxmlHasRuby(rubyPkg), true);
const flat = unwrapRubyInOoxml(rubyPkg);
assert.ok(flat.includes(">漢字</w:t>"));
assert.ok(!flat.includes("<w:ruby>"));
assert.ok(!flat.includes("かんじ"));

/* --- jidori / fitText --- */
assert.equal(countGraphemes("あい"), 2);
assert.equal(fitTextTwipsForCells(5, 10.5), Math.round(5 * 10.5 * 20));
assert.equal(initialN(3), 3);
const fit = applyFitTextInOoxml(bareRun, 1050, 1);
assert.ok(fit.includes('<w:fitText w:val="1050" w:id="1"/>'));
assert.equal(ooxmlHasFitText(fit), true);
const noFit = clearFitTextInOoxml(fit);
assert.equal(ooxmlHasFitText(noFit), false);

console.log("test_typography: ok");
