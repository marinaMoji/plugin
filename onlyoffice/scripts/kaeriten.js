/**
 * marinaMoji Kaeriten — ONLYOFFICE Document Editor plugin
 */
(function () {
  const SOURCE_PREFIX = "MARINAMOJI:source=";
  let mappingData = null;
  let byChar = {};

  function setStatus(text, isErr) {
    const el = document.getElementById("status");
    if (!el) return;
    el.textContent = text || "";
    el.className = "status" + (isErr ? " err" : "");
  }

  function renderOptions() {
    const r = (mappingData && mappingData.rendering) || {};
    const oo = r.onlyoffice_inline || r.word_content_control || {};
    const lo = r.libreoffice_frame || {};
    return {
      fontSizeRatio: Number(oo.font_size_ratio ?? lo.font_size_ratio ?? 0.42),
      minFontSizePt: Number(oo.min_font_size_pt ?? 6),
      compoundLayout: oo.compound_layout || "soft_break",
    };
  }

  function loadMapping() {
    return fetch("mapping.json")
      .then((r) => {
        if (!r.ok) throw new Error("mapping.json not found");
        return r.json();
      })
      .then((data) => {
        mappingData = data;
        byChar = MarinaMojiExport.mappingByChar(data);
        return data;
      });
  }

  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise((resolve, reject) => {
      window.Asc.plugin.executeMethod("PasteText", [text], function (ok) {
        if (ok === false) reject(new Error("Clipboard failed"));
        else resolve();
      });
    });
  }

  /** Read paragraph texts from the document (callCommand). */
  function scanParagraphs() {
    return new Promise((resolve, reject) => {
      window.Asc.plugin.callCommand(
        function () {
          var doc = Api.GetDocument();
          var out = [];
          var n = doc.GetElementsCount();
          for (var i = 0; i < n; i++) {
            var el = doc.GetElement(i);
            if (el.GetClassType && el.GetClassType() === "paragraph") {
              out.push({ index: i, text: el.GetText() || "" });
            }
          }
          return JSON.stringify(out);
        },
        false,
        true,
        function (result) {
          try {
            resolve(JSON.parse(result || "[]"));
          } catch (e) {
            reject(e);
          }
        }
      );
    });
  }

  function buildRenderPlan(paragraphs) {
    const opts = renderOptions();
    const plan = [];
    for (const para of paragraphs) {
      const segments = MarinaMojiExport.buildSegments(para.text, byChar).map((seg) => {
        if (seg.type !== "kaeriten") return seg;
        return {
          ...seg,
          glyphs: MarinaMojiExport.glyphsForInlineSdt(
            seg.marks,
            byChar,
            opts.compoundLayout
          ),
        };
      });
      const hasKaeriten = segments.some((s) => s.type === "kaeriten");
      if (hasKaeriten) plan.push({ index: para.index, segments });
    }
    return plan;
  }

  function applyRenderPlan(plan, fontSizePt) {
    return new Promise((resolve, reject) => {
      Asc.scope.plan = JSON.stringify(plan);
      Asc.scope.fontSizePt = fontSizePt;
      Asc.scope.sourcePrefix = SOURCE_PREFIX;
      window.Asc.plugin.callCommand(
        function () {
          var plan = JSON.parse(Asc.scope.plan);
          var fontSizePt = Asc.scope.fontSizePt || 8;
          var sourcePrefix = Asc.scope.sourcePrefix || "MARINAMOJI:source=";
          var doc = Api.GetDocument();

          function fillInlineSdtGlyphs(sdt, glyphs) {
            var n = sdt.GetElementsCount ? sdt.GetElementsCount() : 0;
            for (var k = n - 1; k >= 0; k--) {
              sdt.RemoveElement(k);
            }
            // Glyphs use soft break (U+000B) between stacks — hard \n escapes the inline SDT.
            var gr = Api.CreateRun();
            gr.AddText(glyphs);
            gr.SetFontSize(fontSizePt);
            sdt.AddElement(gr);
          }

          function fillParagraph(oPara, segments) {
            var n = oPara.GetElementsCount();
            for (var k = n - 1; k >= 0; k--) {
              oPara.RemoveElement(k);
            }
            for (var s = 0; s < segments.length; s++) {
              var seg = segments[s];
              if (seg.type === "text" && seg.value) {
                var run = Api.CreateRun();
                run.AddText(seg.value);
                oPara.AddElement(run);
              } else if (seg.type === "kaeriten") {
                var sdt = Api.CreateInlineLvlSdt();
                fillInlineSdtGlyphs(sdt, seg.glyphs);
                oPara.AddInlineLvlSdt(sdt);
                sdt.SetTag(sourcePrefix + seg.marks);
                if (sdt.SetAlias) sdt.SetAlias(seg.marks);
              }
            }
          }

          for (var p = 0; p < plan.length; p++) {
            var item = plan[p];
            var oPara = doc.GetElement(item.index);
            if (oPara && oPara.GetClassType && oPara.GetClassType() === "paragraph") {
              fillParagraph(oPara, item.segments);
            }
          }
          return plan.length;
        },
        false,
        true,
        function (count) {
          if (typeof count === "number") resolve(count);
          else resolve(0);
        }
      );
    });
  }

  function runRender() {
    setStatus("Rendering…");
    scanParagraphs()
      .then((paragraphs) => {
        const plan = buildRenderPlan(paragraphs);
        if (!plan.length) {
          setStatus("No kaeriten marks found (說㆒㆑).", true);
          return;
        }
        const opts = renderOptions();
        const fontSizePt = Math.max(opts.minFontSizePt, 8);
        return applyRenderPlan(plan, fontSizePt).then((n) => {
          setStatus("Rendered " + n + " paragraph(s).", false);
        });
      })
      .catch((err) => {
        console.error(err);
        setStatus(String(err.message || err), true);
      });
  }

  function runUnrender() {
    setStatus("Unrendering…");
    Asc.scope.prefix = SOURCE_PREFIX;
    window.Asc.plugin.callCommand(
      function () {
        var prefix = Asc.scope.prefix;
        var doc = Api.GetDocument();

        function marksFromControl(cc) {
          var tag = cc.GetTag ? cc.GetTag() || "" : "";
          if (tag.indexOf(prefix) === 0) return tag.substring(prefix.length);
          var alias = cc.GetAlias ? cc.GetAlias() || "" : "";
          if (/^[\u3190-\u319f]+$/.test(alias)) return alias;
          return null;
        }

        /** Collect marinaMoji inline controls by walking paragraphs (reliable in Desktop). */
        function collectControls() {
          var found = [];
          var pn = doc.GetElementsCount();
          for (var p = 0; p < pn; p++) {
            var para = doc.GetElement(p);
            if (!para || !para.GetClassType || para.GetClassType() !== "paragraph") continue;
            var ec = para.GetElementsCount();
            for (var e = 0; e < ec; e++) {
              var child = para.GetElement(e);
              if (!child || !child.GetClassType) continue;
              if (child.GetClassType() !== "inlineLvlSdt") continue;
              var marks = marksFromControl(child);
              if (!marks) continue;
              found.push({ paraIndex: p, pos: e, marks: marks });
            }
          }

          found.sort(function (a, b) {
            if (a.paraIndex !== b.paraIndex) return b.paraIndex - a.paraIndex;
            return b.pos - a.pos;
          });
          return found;
        }

        function replaceControl(item) {
          var para = doc.GetElement(item.paraIndex);
          var pos = item.pos;
          if (!para || pos < 0) return false;

          var run = Api.CreateRun();
          run.AddText(item.marks);
          // Insert marks at the control position, then remove the wrapper.
          // Do not call cc.Delete(false) — ONLYOFFICE can spill display glyphs (レ) to line start.
          para.AddElement(run, pos);
          para.RemoveElement(pos + 1);
          return true;
        }

        var items = collectControls();
        var count = 0;
        for (var i = 0; i < items.length; i++) {
          if (replaceControl(items[i])) count++;
        }
        return count;
      },
      false,
      true,
      function (count) {
        setStatus(
          count ? "Restored source marks (" + count + ")." : "No kaeriten views found.",
          false
        );
      }
    );
  }

  function runRefresh() {
    setStatus("Refreshing…");
    const opts = renderOptions();
    Asc.scope.prefix = SOURCE_PREFIX;
    Asc.scope.byCharJson = JSON.stringify(byChar);
    Asc.scope.compoundLayout = opts.compoundLayout;
    Asc.scope.fontSizePt = Math.max(opts.minFontSizePt, 8);
    window.Asc.plugin.callCommand(
      function () {
        var prefix = Asc.scope.prefix;
        var byChar = JSON.parse(Asc.scope.byCharJson || "{}");
        var compoundLayout = Asc.scope.compoundLayout || "soft_break";
        var fontSizePt = Asc.scope.fontSizePt || 8;
        var doc = Api.GetDocument();

        function inlineGlyphs(marks) {
          var chars = marks.split("");
          chars.sort(function (a, b) {
            var oa = Number(byChar[a] ? byChar[a].stack_order : 0);
            var ob = Number(byChar[b] ? byChar[b].stack_order : 0);
            if (oa !== ob) return oa - ob;
            return marks.indexOf(a) - marks.indexOf(b);
          });
          var lines = chars.map(function (c) {
            return byChar[c] ? byChar[c].display_glyph : c;
          });
          if (lines.length <= 1) return lines.join("");
          if (compoundLayout === "horizontal") return lines.join("");
          return lines.join("\u000b");
        }

        function marksFromControl(cc) {
          var tag = cc.GetTag ? cc.GetTag() || "" : "";
          if (tag.indexOf(prefix) === 0) return tag.substring(prefix.length);
          var alias = cc.GetAlias ? cc.GetAlias() || "" : "";
          if (/^[\u3190-\u319f]+$/.test(alias)) return alias;
          return null;
        }

        function collectControls() {
          var found = [];
          var pn = doc.GetElementsCount();
          for (var p = 0; p < pn; p++) {
            var para = doc.GetElement(p);
            if (!para || !para.GetClassType || para.GetClassType() !== "paragraph") continue;
            var ec = para.GetElementsCount();
            for (var e = 0; e < ec; e++) {
              var child = para.GetElement(e);
              if (!child || !child.GetClassType) continue;
              if (child.GetClassType() !== "inlineLvlSdt") continue;
              var marks = marksFromControl(child);
              if (!marks) continue;
              found.push({ cc: child, marks: marks });
            }
          }
          return found;
        }

        var count = 0;
        var items = collectControls();
        for (var i = 0; i < items.length; i++) {
          var cc = items[i].cc;
          var marks = items[i].marks;
          var glyphs = inlineGlyphs(marks);
          var n = cc.GetElementsCount ? cc.GetElementsCount() : 0;
          for (var k = n - 1; k >= 0; k--) {
            cc.RemoveElement(k);
          }
          var gr = Api.CreateRun();
          gr.AddText(glyphs);
          gr.SetFontSize(fontSizePt);
          cc.AddElement(gr);
          count++;
        }
        return count;
      },
      false,
      true,
      function (count) {
        setStatus(
          count ? "Refreshed " + count + " view(s)." : "No kaeriten views found.",
          false
        );
      }
    );
  }

  function getSelectedOrDocText() {
    return new Promise((resolve) => {
      window.Asc.plugin.executeMethod("GetSelectedText", [], function (sel) {
        if (sel && String(sel).length > 0) {
          resolve({ text: String(sel), fullDocument: false });
          return;
        }
        scanParagraphs().then((paragraphs) => {
          resolve({
            text: paragraphs.map((p) => p.text).join("\n"),
            fullDocument: true,
          });
        });
      });
    });
  }

  function runCopyPlain() {
    setStatus("Copying…");
    getSelectedOrDocText()
      .then(({ text }) => copyToClipboard(MarinaMojiExport.exportPlainText(text)))
      .then(() => setStatus("Copied plain text.", false))
      .catch((err) => setStatus(String(err.message || err), true));
  }

  function runCopyTei() {
    setStatus("Copying TEI…");
    getSelectedOrDocText()
      .then(({ text, fullDocument }) =>
        copyToClipboard(MarinaMojiExport.exportTeiForClipboard(text, fullDocument))
      )
      .then(() => setStatus("Copied TEI. (Unrender first if views are shown.)", false))
      .catch((err) => setStatus(String(err.message || err), true));
  }

  function runCopyLatex() {
    setStatus("Copying LaTeX…");
    getSelectedOrDocText()
      .then(({ text, fullDocument }) =>
        copyToClipboard(
          MarinaMojiExport.exportLatexForClipboard(text, mappingData, fullDocument)
        )
      )
      .then(() => setStatus("Copied LaTeX. (Unrender first if views are shown.)", false))
      .catch((err) => setStatus(String(err.message || err), true));
  }

  function wire(id, fn) {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener("click", () => {
      btn.disabled = true;
      Promise.resolve(fn()).finally(() => {
        btn.disabled = false;
      });
    });
  }

  window.Asc.plugin.init = function () {
    loadMapping()
      .then(() => {
        setStatus("Ready — type 說㆒㆑者, then Render.", false);
        wire("btn-render", runRender);
        wire("btn-unrender", runUnrender);
        wire("btn-refresh", runRefresh);
        wire("btn-plain", runCopyPlain);
        wire("btn-tei", runCopyTei);
        wire("btn-latex", runCopyLatex);
      })
      .catch((err) => setStatus(String(err.message || err), true));
  };

  window.Asc.plugin.button = function () {};
})();
