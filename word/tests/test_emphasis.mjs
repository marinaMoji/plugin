#!/usr/bin/env node
import assert from "node:assert/strict";
import {
  EMPHASIS_BUILTIN_DEFAULT,
  normalizeEmphasisStyleId,
  resolveEmphasisDefault,
  styleToEmVal,
  emValToStyle,
  labelForStyle,
  styleOptions,
} from "../src/typography/emphasisStyles.js";
import {
  applyEmphasisStyleInOoxml,
  clearEmphasisInOoxml,
  setEmValInOoxml,
  ooxmlHasEmphasis,
} from "../src/typography/emphasisOoxml.js";

assert.equal(normalizeEmphasisStyleId("black-sesame"), "BLACK_SESAME");
assert.equal(normalizeEmphasisStyleId("SESAME"), "BLACK_SESAME");
assert.equal(normalizeEmphasisStyleId("BLACK_DOT"), "DOT");
assert.equal(normalizeEmphasisStyleId("nope"), null);
assert.equal(resolveEmphasisDefault(null), EMPHASIS_BUILTIN_DEFAULT);
assert.equal(styleToEmVal("BLACK_SESAME"), "comma");
assert.equal(styleToEmVal("WHITE_CIRCLE"), "circle");
assert.equal(styleToEmVal("DOT"), "dot");
assert.equal(emValToStyle("comma"), "BLACK_SESAME");
assert.equal(emValToStyle("none"), null);
assert.ok(labelForStyle("BLACK_SESAME", "ja").includes("黒ゴマ"));
assert.equal(styleOptions("en").length, 3);

const bareRun = `<?xml version="1.0"?>
<pkg:package xmlns:pkg="http://schemas.microsoft.com/office/2006/xmlPackage">
  <pkg:part pkg:name="/word/document.xml">
    <pkg:xmlData>
      <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:body><w:p><w:r><w:t>重要</w:t></w:r></w:p></w:body>
      </w:document>
    </pkg:xmlData>
  </pkg:part>
</pkg:package>`;

assert.equal(ooxmlHasEmphasis(bareRun), false);
const withSesame = applyEmphasisStyleInOoxml(bareRun, "BLACK_SESAME");
assert.ok(withSesame.includes('<w:em w:val="comma"/>'));
assert.ok(withSesame.includes("<w:rPr>"));
assert.ok(withSesame.includes(">重要</w:t>"));
assert.equal(ooxmlHasEmphasis(withSesame), true);

const withRPr = bareRun.replace(
  "<w:r><w:t>重要</w:t></w:r>",
  '<w:r><w:rPr><w:b/></w:rPr><w:t>重要</w:t></w:r>'
);
const boldAndDot = applyEmphasisStyleInOoxml(withRPr, "DOT");
assert.ok(boldAndDot.includes('<w:em w:val="dot"/>'));
assert.ok(boldAndDot.includes("<w:b/>"));

const already = setEmValInOoxml(withSesame, "circle");
assert.ok(already.includes('<w:em w:val="circle"/>'));
assert.ok(!already.includes('w:val="comma"'));

const cleared = clearEmphasisInOoxml(already);
assert.ok(cleared.includes('<w:em w:val="none"/>'));
assert.equal(ooxmlHasEmphasis(cleared), false);

console.log("test_emphasis: ok");
