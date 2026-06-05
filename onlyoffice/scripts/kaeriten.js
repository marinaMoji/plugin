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
      compoundLayout: oo.compound_layout || "stack",
      stackStepHps: Number(oo.stack_step_hps ?? 0),
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
    const plan = [];
    for (const para of paragraphs) {
      const segments = MarinaMojiExport.buildSegments(para.text, byChar).map((seg) => {
        if (seg.type !== "kaeriten") return seg;
        return {
          ...seg,
          glyphLines: MarinaMojiExport.glyphLinesForMarks(seg.marks, byChar),
        };
      });
      const hasKaeriten = segments.some((s) => s.type === "kaeriten");
      if (hasKaeriten) plan.push({ index: para.index, segments });
    }
    return plan;
  }

  function applyRenderPlan(plan, fontSizePt, compoundLayout, stackStepHps) {
    return new Promise((resolve, reject) => {
      Asc.scope.plan = JSON.stringify(plan);
      Asc.scope.fontSizePt = fontSizePt;
      Asc.scope.compoundLayout = compoundLayout || "stack";
      Asc.scope.stackStepHps = stackStepHps || 0;
      Asc.scope.sourcePrefix = SOURCE_PREFIX;
      window.Asc.plugin.callCommand(
        function () {
          var plan = JSON.parse(Asc.scope.plan);
          var fontSizePt = Asc.scope.fontSizePt || 8;
          var compoundLayout = Asc.scope.compoundLayout || "stack";
          var stackStepHps = Asc.scope.stackStepHps || 0;
          var sourcePrefix = Asc.scope.sourcePrefix || "MARINAMOJI:source=";
          var doc = Api.GetDocument();

          function stackStep() {
            if (stackStepHps > 0) return stackStepHps;
            return Math.max(8, Math.round(fontSizePt * 1.4));
          }

          /** Vertical compound stack without AddLineBreak (breaks escape the inline SDT). */
          function fillPositionStack(sdt, glyphLines) {
            var n = glyphLines.length;
            var step = stackStep();
            var backTwips = -Math.round(fontSizePt * 20 * 0.92);
            var mid = (n - 1) / 2.0;
            for (var i = 0; i < n; i++) {
              var gr = Api.CreateRun();
              gr.SetFontSize(fontSizePt);
              gr.SetPosition(Math.round(step * (n - 1 - i - mid)));
              if (i > 0 && gr.SetSpacing) gr.SetSpacing(backTwips);
              gr.AddText(glyphLines[i]);
              sdt.AddElement(gr);
            }
          }

          function fillInlineSdtGlyphs(sdt, glyphLines) {
            var n = sdt.GetElementsCount ? sdt.GetElementsCount() : 0;
            for (var k = n - 1; k >= 0; k--) {
              sdt.RemoveElement(k);
            }
            if (!glyphLines || !glyphLines.length) return;

            if (glyphLines.length === 1) {
              var one = Api.CreateRun();
              one.AddText(glyphLines[0]);
              one.SetFontSize(fontSizePt);
              sdt.AddElement(one);
              return;
            }

            if (compoundLayout === "horizontal") {
              var hRun = Api.CreateRun();
              hRun.AddText(glyphLines.join(""));
              hRun.SetFontSize(fontSizePt);
              sdt.AddElement(hRun);
              return;
            }

            if (compoundLayout === "soft_break") {
              var sRun = Api.CreateRun();
              sRun.AddText(glyphLines.join("\u000b"));
              sRun.SetFontSize(fontSizePt);
              sdt.AddElement(sRun);
              return;
            }

            fillPositionStack(sdt, glyphLines);
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
                fillInlineSdtGlyphs(sdt, seg.glyphLines);
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
        return applyRenderPlan(plan, fontSizePt, opts.compoundLayout, opts.stackStepHps).then((n) => {
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
    Asc.scope.stackStepHps = opts.stackStepHps;
    Asc.scope.fontSizePt = Math.max(opts.minFontSizePt, 8);
    window.Asc.plugin.callCommand(
      function () {
        var prefix = Asc.scope.prefix;
        var byChar = JSON.parse(Asc.scope.byCharJson || "{}");
        var compoundLayout = Asc.scope.compoundLayout || "stack";
        var stackStepHps = Asc.scope.stackStepHps || 0;
        var fontSizePt = Asc.scope.fontSizePt || 8;
        var doc = Api.GetDocument();

        function stackStep() {
          if (stackStepHps > 0) return stackStepHps;
          return Math.max(8, Math.round(fontSizePt * 1.4));
        }

        function glyphLinesForMarksInline(marks) {
          var chars = marks.split("");
          chars.sort(function (a, b) {
            var oa = Number(byChar[a] ? byChar[a].stack_order : 0);
            var ob = Number(byChar[b] ? byChar[b].stack_order : 0);
            if (oa !== ob) return oa - ob;
            return marks.indexOf(a) - marks.indexOf(b);
          });
          return chars.map(function (c) {
            return byChar[c] ? byChar[c].display_glyph : c;
          });
        }

        function fillPositionStack(cc, glyphLines) {
          var n = glyphLines.length;
          var step = stackStep();
          var backTwips = -Math.round(fontSizePt * 20 * 0.92);
          var mid = (n - 1) / 2.0;
          for (var i = 0; i < n; i++) {
            var gr = Api.CreateRun();
            gr.SetFontSize(fontSizePt);
            gr.SetPosition(Math.round(step * (n - 1 - i - mid)));
            if (i > 0 && gr.SetSpacing) gr.SetSpacing(backTwips);
            gr.AddText(glyphLines[i]);
            cc.AddElement(gr);
          }
        }

        function fillControlGlyphs(cc, glyphLines) {
          var n = cc.GetElementsCount ? cc.GetElementsCount() : 0;
          for (var k = n - 1; k >= 0; k--) {
            cc.RemoveElement(k);
          }
          if (!glyphLines || !glyphLines.length) return;

          if (glyphLines.length === 1) {
            var one = Api.CreateRun();
            one.AddText(glyphLines[0]);
            one.SetFontSize(fontSizePt);
            cc.AddElement(one);
            return;
          }

          if (compoundLayout === "horizontal") {
            var hRun = Api.CreateRun();
            hRun.AddText(glyphLines.join(""));
            hRun.SetFontSize(fontSizePt);
            cc.AddElement(hRun);
            return;
          }

          if (compoundLayout === "soft_break") {
            var sRun = Api.CreateRun();
            sRun.AddText(glyphLines.join("\u000b"));
            sRun.SetFontSize(fontSizePt);
            cc.AddElement(sRun);
            return;
          }

          fillPositionStack(cc, glyphLines);
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
          fillControlGlyphs(cc, glyphLinesForMarksInline(marks));
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

  function getTextForExport() {
    return scanExportModel().then((model) => {
      return new Promise((resolve) => {
        window.Asc.plugin.executeMethod("GetSelectedText", [], function (sel) {
          const selectedDisplay = sel && String(sel).length > 0 ? String(sel) : "";
          resolve(
            MarinaMojiExport.resolveExportText(
              model.segments,
              model.docCanonical,
              selectedDisplay
            )
          );
        });
      });
    });
  }

  /** Walk paragraph elements; use control tags for canonical marks, not display glyphs. */
  function scanExportModel() {
    return new Promise((resolve, reject) => {
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

          function paragraphParts(para) {
            var parts = [];
            var ec = para.GetElementsCount();
            for (var e = 0; e < ec; e++) {
              var el = para.GetElement(e);
              if (!el || !el.GetClassType) continue;
              if (el.GetClassType() === "inlineLvlSdt") {
                var marks = marksFromControl(el);
                var display = el.GetText ? el.GetText() || "" : "";
                parts.push({
                  canonical: marks || display,
                  display: display || marks || "",
                });
              } else if (el.GetText) {
                var text = el.GetText() || "";
                parts.push({ canonical: text, display: text });
              }
            }
            return parts;
          }

          var segments = [];
          var pn = doc.GetElementsCount();
          for (var p = 0; p < pn; p++) {
            var para = doc.GetElement(p);
            if (!para || !para.GetClassType || para.GetClassType() !== "paragraph") {
              continue;
            }
            if (segments.length) {
              segments.push({ canonical: "\n", display: "\n" });
            }
            var parts = paragraphParts(para);
            for (var i = 0; i < parts.length; i++) {
              segments.push(parts[i]);
            }
          }

          var docCanonical = "";
          for (var s = 0; s < segments.length; s++) {
            docCanonical += segments[s].canonical;
          }
          return JSON.stringify({ docCanonical: docCanonical, segments: segments });
        },
        false,
        true,
        function (result) {
          try {
            resolve(JSON.parse(result || '{"docCanonical":"","segments":[]}'));
          } catch (e) {
            reject(e);
          }
        }
      );
    });
  }

  function runCopyPlain() {
    setStatus("Copying…");
    getTextForExport()
      .then(({ text }) => copyToClipboard(MarinaMojiExport.exportPlainText(text)))
      .then(() => setStatus("Copied plain text.", false))
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
      })
      .catch((err) => setStatus(String(err.message || err), true));
  };

  window.Asc.plugin.button = function () {};
})();
