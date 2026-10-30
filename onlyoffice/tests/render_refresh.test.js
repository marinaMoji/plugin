#!/usr/bin/env node
/**
 * Render / Unrender against a small in-memory model of the ONLYOFFICE document API.
 *
 *   node tests/render_refresh.test.js [path/to/kaeriten.js]
 *
 * Checks that a second Render replaces only the marinaMoji views and leaves
 * hyperlinks and run formatting alone (reviewer report, ONLYOFFICE Marketplace).
 * The model implements just the calls kaeriten.js makes; it is not ONLYOFFICE.
 */
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

const root = path.join(__dirname, "..");
const kaeritenPath = process.argv[2] || path.join(root, "scripts", "kaeriten.js");

// ---------------------------------------------------------------- document model

class Run {
  constructor() {
    this.text = "";
    this.bold = false;
    this.color = null;
    this.children = []; // drawings
  }
  GetClassType() { return "run"; }
  AddText(t) { this.text += t; }
  GetText() { return this.text; }
  SetBold(v) { this.bold = !!v; }
  GetBold() { return this.bold; }
  SetColor(c) { this.color = c; }
  GetColor() { return this.color; }
  SetFontSize() {}
  SetPosition() {}
  SetSpacing() {}
  AddDrawing(d) { this.children.push(d); }
  GetElementsCount() { return this.children.length; }
  GetElement(i) { return this.children[i]; }
}

class Drawing {
  constructor() { this.name = ""; }
  GetClassType() { return "drawing"; }
  SetName(n) { this.name = n; }
  GetName() { return this.name; }
  SetWrappingStyle() {}
}

class Sdt {
  constructor() { this.tag = ""; this.alias = ""; this.children = []; }
  GetClassType() { return "inlineLvlSdt"; }
  SetTag(t) { this.tag = t; }
  GetTag() { return this.tag; }
  SetAlias(a) { this.alias = a; }
  GetAlias() { return this.alias; }
  AddElement(e, i) {
    if (typeof i === "number") this.children.splice(i, 0, e);
    else this.children.push(e);
  }
  RemoveElement(i) { this.children.splice(i, 1); }
  GetElementsCount() { return this.children.length; }
  GetElement(i) { return this.children[i]; }
  GetText() { return this.children.map((c) => (c.GetText ? c.GetText() : "")).join(""); }
}

// Like ApiHyperlink: no GetText, no child access.
class Hyperlink {
  constructor(text, url) { this.shown = text; this.url = url; }
  GetClassType() { return "hyperlink"; }
  GetDisplayedText() { return this.shown; }
}

class Paragraph {
  constructor(elements) { this.elements = elements; }
  GetClassType() { return "paragraph"; }
  GetElementsCount() { return this.elements.length; }
  GetElement(i) { return this.elements[i]; }
  AddElement(e, i) {
    if (typeof i === "number") this.elements.splice(i, 0, e);
    else this.elements.push(e);
  }
  RemoveElement(i) { this.elements.splice(i, 1); }
  GetText() {
    return this.elements
      .map((e) => (e.GetText ? e.GetText() : e.GetDisplayedText ? e.GetDisplayedText() : ""))
      .join("");
  }
  GetTextPr() { return {}; }
}

function run(text, opts = {}) {
  const r = new Run();
  r.AddText(text);
  if (opts.bold) r.SetBold(true);
  if (opts.color) r.SetColor(opts.color);
  return r;
}

// ---------------------------------------------------------------- plugin harness

function loadPlugin(mappingOverride) {
  const mapping = JSON.parse(fs.readFileSync(path.join(root, "mapping.json"), "utf8"));
  if (mappingOverride) mappingOverride(mapping);

  let paragraphs = [];
  const handlers = {};
  const ctx = {
    console,
    Math, JSON, Number, String, Object, Array, Promise, RegExp, isFinite,
    setTimeout, clearTimeout,
  };
  ctx.window = ctx;
  ctx.Asc = {
    scope: {},
    plugin: {
      callCommand(fn, _silent, _calc, cb) {
        const result = fn();
        if (cb) cb(result);
      },
      attachEvent() {},
      executeMethod() {},
    },
  };
  ctx.Api = {
    GetDocument: () => ({
      GetElementsCount: () => paragraphs.length,
      GetElement: (i) => paragraphs[i],
    }),
    CreateRun: () => new Run(),
    CreateInlineLvlSdt: () => new Sdt(),
    CreateImage: () => new Drawing(),
  };
  const stub = () => ({
    addEventListener(_ev, h) { this.click = h; },
    style: {},
    set textContent(v) { this.text = v; },
    get textContent() { return this.text; },
    setAttribute() {},
  });
  const els = {};
  ctx.document = {
    getElementById: (id) => (els[id] = els[id] || stub()),
    createElement: () => ({
      getContext: () => ({ clearRect() {}, fillRect() {}, fillText() {} }),
      toDataURL: () => "data:image/png;base64,AAAA",
      style: {},
      setAttribute() {},
    }),
    body: { appendChild() {}, removeChild() {} },
  };
  ctx.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve(mapping) });
  vm.createContext(ctx);
  for (const f of ["exportCore.js", null]) {
    const file = f ? path.join(root, "scripts", f) : kaeritenPath;
    vm.runInContext(fs.readFileSync(file, "utf8"), ctx, { filename: file });
  }
  return {
    els,
    setParagraphs(p) { paragraphs = p; },
    async init() {
      ctx.Asc.plugin.init();
      await new Promise((r) => setTimeout(r, 20));
    },
    async click(id) {
      els[id].click();
      await new Promise((r) => setTimeout(r, 20));
    },
    status: () => els["status"] && els["status"].text,
  };
}

// ---------------------------------------------------------------- helpers

const isView = (e) =>
  (e instanceof Sdt && e.tag.startsWith("MARINAMOJI:source=")) ||
  (e instanceof Run &&
    e.children.some((c) => c.GetName && c.GetName().startsWith("MARINAMOJI:source=")));

const viewMarks = (e) => {
  const tag = e instanceof Sdt ? e.tag : e.children[0].GetName();
  return tag.slice("MARINAMOJI:source=".length).split(";")[0];
};

function build() {
  // 學而時習㆑之。有朋自遠方來㆒㆑者。 — 時習 bold, 有朋 hyperlink, 來 red
  return new Paragraph([
    run("學而"),
    run("時習", { bold: true }),
    run("㆑之。"),
    new Hyperlink("有朋", "https://example.org/"),
    run("自遠方"),
    run("來", { color: "ff0000" }),
    run("㆒㆑者。"),
  ]);
}

function assertIntact(para, label) {
  const links = para.elements.filter((e) => e instanceof Hyperlink);
  assert.strictEqual(links.length, 1, label + ": hyperlink kept");
  assert.strictEqual(links[0].GetDisplayedText(), "有朋", label + ": hyperlink text");
  const bold = para.elements.find((e) => e instanceof Run && e.text === "時習");
  assert(bold && bold.bold, label + ": bold run kept");
  const red = para.elements.find((e) => e instanceof Run && e.text === "來");
  assert(red && red.color === "ff0000", label + ": red run kept");
  const views = para.elements.filter(isView);
  assert.deepStrictEqual(views.map(viewMarks), ["㆑", "㆒㆑"], label + ": two views, in order");
}

// ---------------------------------------------------------------- tests

const results = [];
async function test(name, fn) {
  try {
    await fn();
    results.push(["ok", name]);
  } catch (e) {
    results.push(["FAIL", name + "\n      " + (e && e.message)]);
  }
}

const modes = {
  image: undefined,
  control: (m) => { m.rendering.onlyoffice_primary = "inline_content_control"; },
};

(async () => {
  for (const [mode, override] of Object.entries(modes)) {
    await test(`[${mode}] Render, Render keeps hyperlink and run formatting`, async () => {
      const h = loadPlugin(override);
      const para = build();
      h.setParagraphs([para]);
      await h.init();
      await h.click("btn-render");
      assertIntact(para, "after Render 1");
      await h.click("btn-render");
      assertIntact(para, "after Render 2");
      await h.click("btn-render");
      assertIntact(para, "after Render 3");
    });

    await test(`[${mode}] Render, Unrender restores marks and keeps the hyperlink`, async () => {
      const h = loadPlugin(override);
      const para = build();
      h.setParagraphs([para]);
      await h.init();
      await h.click("btn-render");
      await h.click("btn-render");
      await h.click("btn-unrender");
      assert.strictEqual(para.elements.filter(isView).length, 0, "no views left");
      assert.strictEqual(para.GetText(), "學而時習㆑之。有朋自遠方來㆒㆑者。");
      assert.strictEqual(para.elements.filter((e) => e instanceof Hyperlink).length, 1);
    });

    await test(`[${mode}] a plain paragraph still refreshes (no hyperlink)`, async () => {
      const h = loadPlugin(override);
      const para = new Paragraph([run("說㆒㆑者")]);
      h.setParagraphs([para]);
      await h.init();
      await h.click("btn-render");
      await h.click("btn-render");
      const views = para.elements.filter(isView);
      assert.deepStrictEqual(views.map(viewMarks), ["㆒㆑"]);
      assert.strictEqual(para.elements[0].text, "說");
      assert.strictEqual(para.elements[para.elements.length - 1].text, "者");
    });
  }

  await test("raw marks inside a hyperlink never cost the hyperlink", async () => {
    const h = loadPlugin(modes.control);
    const para = new Paragraph([run("說"), new Hyperlink("有朋㆒㆑", "https://example.org/"), run("者")]);
    h.setParagraphs([para]);
    await h.init();
    await h.click("btn-render");
    const links = para.elements.filter((e) => e instanceof Hyperlink);
    assert.strictEqual(links.length, 1);
    assert.strictEqual(links[0].GetDisplayedText(), "有朋㆒㆑");
  });

  let failed = 0;
  for (const [status, name] of results) {
    console.log(status === "ok" ? "ok  " : "FAIL", name);
    if (status !== "ok") failed++;
  }
  console.log(failed ? `${failed} failed` : "all passed");
  process.exit(failed ? 1 : 0);
})();
