#!/usr/bin/env node
import assert from "node:assert/strict";
import {
  compareVersions,
  evaluateUpdate,
  parseVersionParts,
} from "../src/updateCheck.js";

assert.deepEqual(parseVersionParts("0.1.3.0"), [0, 1, 3, 0]);
assert.equal(compareVersions("0.1.4", "0.1.3"), 1);
assert.equal(compareVersions("0.1.3", "0.1.3.0"), 0);
assert.equal(compareVersions("0.1.2", "0.1.3"), -1);

const none = evaluateUpdate(
  {
    word: "0.1.3",
    word_manifest: "0.1.3.0",
    release_url: "https://example.com/r",
  },
  { word: "0.1.3", word_manifest: "0.1.3.0" }
);
assert.equal(none.show, false);

const code = evaluateUpdate(
  {
    word: "0.1.4",
    word_manifest: "0.1.3.0",
    release_url: "https://example.com/r",
  },
  { word: "0.1.3", word_manifest: "0.1.3.0" }
);
assert.equal(code.show, true);
assert.equal(code.codeNewer, true);
assert.equal(code.manifestNewer, false);

const man = evaluateUpdate(
  {
    word: "0.1.3",
    word_manifest: "0.1.4.0",
    release_url: "https://example.com/r",
  },
  { word: "0.1.3", word_manifest: "0.1.3.0" }
);
assert.equal(man.show, true);
assert.equal(man.manifestNewer, true);

console.log("test_update_check: ok");
