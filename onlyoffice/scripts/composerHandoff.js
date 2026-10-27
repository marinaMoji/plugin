/*
 * marinaMoji character composer -> ONLYOFFICE.
 *
 * For a structure with no Unicode character the composer (macOS) writes a
 * drawing as SVG, and also composer_result.js next to this plugin's
 * index.html:
 *
 *   window.marinaMojiComposerResult = { id: <ms since epoch>, svg: "<svg…>" };
 *
 * While the panel is open it loads that file about once a second (a relative
 * <script src> works from file:// with no CORS or clipboard permission),
 * rasterises a fresh result and inserts it at the cursor. No button involved.
 */
(function () {
  "use strict";

  var POLL_MS = 1000;
  var MAX_AGE_MS = 120000; // ignore anything older, e.g. left over from a past session
  var RASTER_HEIGHT_PX = 256; // the picture's pixels; its size on the page is set at insert
  var DEFAULT_PT = 12; // used when the font size at the cursor cannot be read
  // The drawing fills its square; a font's ink is a little smaller and hangs a
  // little below the baseline. Measured against Arial/Mincho text in ONLYOFFICE.
  var INK_SCALE = 0.94;
  var DROP_EM = 0.19;
  var STORE_KEY = "marinamoji.composer.lastId";

  var busy = false;

  function lastSeenId() {
    try {
      return Number(window.localStorage.getItem(STORE_KEY)) || 0;
    } catch (e) {
      return 0;
    }
  }

  function rememberId(id) {
    try {
      window.localStorage.setItem(STORE_KEY, String(id));
    } catch (e) {
      /* in-memory guard below still applies */
    }
    memoryId = id;
  }

  var memoryId = 0;

  function setStatus(text) {
    var el = document.getElementById("composer-status");
    if (el) el.textContent = text;
  }

  function svgSize(svg) {
    var w = /<svg[^>]*\swidth="([\d.]+)"/.exec(svg);
    var h = /<svg[^>]*\sheight="([\d.]+)"/.exec(svg);
    var width = w ? Number(w[1]) : 100;
    var height = h ? Number(h[1]) : width;
    return { width: width || 100, height: height || 100 };
  }

  /** Rasterises |svg| to a PNG data URL; resolves {dataUrl, aspect} (width / height). */
  function svgToPng(svg) {
    return new Promise(function (resolve, reject) {
      var size = svgSize(svg);
      var aspect = size.width / size.height;
      var img = new Image();
      img.onload = function () {
        try {
          var canvas = document.createElement("canvas");
          canvas.height = RASTER_HEIGHT_PX;
          canvas.width = Math.max(1, Math.round(RASTER_HEIGHT_PX * aspect));
          var ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          resolve({ dataUrl: canvas.toDataURL("image/png"), aspect: aspect });
        } catch (e) {
          reject(e);
        }
      };
      img.onerror = function () {
        reject(new Error("SVG could not be rendered"));
      };
      img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    });
  }

  /** Pastes the picture as HTML: the fallback when the document API cannot. */
  function pasteHtml(png) {
    var heightPx = Math.round((DEFAULT_PT * 96) / 72);
    var html =
      '<img src="' + png.dataUrl + '" width="' + Math.round(heightPx * png.aspect) +
      '" height="' + heightPx + '" alt="marinaMoji composed character"/>';
    window.Asc.plugin.executeMethod("PasteHtml", [html]);
  }

  /**
   * Inserts the picture inline at the cursor through the document API, the way
   * Render places its pictures; falls back to PasteHtml if that fails.
   */
  function insertAtCursor(png, done) {
    var asc = window.Asc;
    asc.scope = asc.scope || {};
    asc.scope.composedPng = png.dataUrl;
    asc.scope.composedAspect = png.aspect;
    asc.scope.composedDefaultPt = DEFAULT_PT;
    asc.scope.composedInkScale = INK_SCALE;
    asc.scope.composedDropEm = DROP_EM;
    try {
      asc.plugin.callCommand(
        function () {
          var doc = Api.GetDocument();
          // Font size (pt) of the text at the cursor: the paragraph's last run
          // with text, else the paragraph, else the document default.
          function sizePt(textPr) {
            var hps = textPr && textPr.GetFontSize ? Number(textPr.GetFontSize()) : 0;
            return hps > 0 ? hps / 2 : 0;
          }
          var pt = 0;
          try {
            var cur = doc.GetCurrentParagraph ? doc.GetCurrentParagraph() : null;
            if (cur) {
              for (var i = cur.GetElementsCount() - 1; i >= 0 && !pt; i--) {
                var el = cur.GetElement(i);
                if (el && el.GetText && el.GetText()) {
                  pt = el.GetFontSize ? sizePt({ GetFontSize: function () { return el.GetFontSize(); } })
                                      : sizePt(el.GetTextPr && el.GetTextPr());
                }
              }
              if (!pt && cur.GetTextPr) pt = sizePt(cur.GetTextPr());
            }
          } catch (e) {}
          if (!pt && doc.GetDefaultTextPr) pt = sizePt(doc.GetDefaultTextPr());
          if (!pt) pt = Asc.scope.composedDefaultPt;
          var heightEmu = Math.round(pt * Asc.scope.composedInkScale * 12700);
          var drawing = Api.CreateImage(
            Asc.scope.composedPng,
            Math.round(heightEmu * Asc.scope.composedAspect),
            heightEmu
          );
          if (drawing.SetWrappingStyle) drawing.SetWrappingStyle("inline");
          if (drawing.SetName) drawing.SetName("marinaMoji composed character");
          var run = Api.CreateRun();
          // A CJK glyph's box reaches below the baseline; sit the picture there.
          if (run.SetPosition) run.SetPosition(-Math.round(pt * 2 * Asc.scope.composedDropEm));
          run.AddDrawing(drawing);
          var para = Api.CreateParagraph();
          para.AddElement(run);
          doc.InsertContent([para], true);
          return pt || true;
        },
        false,
        true,
        function (ok) {
          if (!ok) pasteHtml(png);
          done(ok);
        }
      );
    } catch (e) {
      pasteHtml(png);
      done(true);
    }
  }

  function handle(result) {
    var id = Number(result && result.id);
    var svg = result && result.svg;
    if (!id || typeof svg !== "string" || svg.indexOf("<svg") < 0) return;
    if (id <= Math.max(lastSeenId(), memoryId)) return;
    if (Date.now() - id > MAX_AGE_MS) {
      rememberId(id); // too old to be what the user just composed; do not retry
      return;
    }
    busy = true;
    svgToPng(svg)
      .then(function (png) {
        return new Promise(function (resolve) {
          insertAtCursor(png, resolve);
        });
      })
      .then(function (ok) {
        rememberId(id);
        setStatus("Inserted composed character" + (typeof ok === "number" ? " at " + ok + " pt." : "."));
      })
      .catch(function (e) {
        setStatus("Composer result could not be inserted: " + (e && e.message ? e.message : e));
      })
      .then(function () {
        busy = false;
      });
  }

  function poll() {
    if (busy) return;
    window.marinaMojiComposerResult = undefined;
    var old = document.getElementById("composer-result-script");
    if (old && old.parentNode) old.parentNode.removeChild(old);
    var s = document.createElement("script");
    s.id = "composer-result-script";
    s.charset = "utf-8";
    s.onload = function () {
      handle(window.marinaMojiComposerResult);
    };
    s.onerror = function () {
      /* no file yet: the composer has not produced a drawing */
    };
    s.src = "composer_result.js?_=" + Date.now();
    document.head.appendChild(s);
  }

  /**
   * Resizes every composed-character picture in the document to the font size
   * of its paragraph (aspect kept), so Render follows font and size changes.
   * Resolves with the number resized.
   */
  function refreshSizes() {
    return new Promise(function (resolve) {
      var asc = window.Asc;
      asc.scope = asc.scope || {};
      asc.scope.composedDefaultPt = DEFAULT_PT;
      asc.scope.composedInkScale = INK_SCALE;
      asc.scope.composedDropEm = DROP_EM;
      try {
        asc.plugin.callCommand(
          function () {
            var doc = Api.GetDocument();
            if (!doc.GetAllDrawingObjects) return 0;
            function sizePt(textPr) {
              var hps = textPr && textPr.GetFontSize ? Number(textPr.GetFontSize()) : 0;
              return hps > 0 ? hps / 2 : 0;
            }
            function paragraphPt(para) {
              var pt = 0;
              for (var i = para.GetElementsCount() - 1; i >= 0 && !pt; i--) {
                var el = para.GetElement(i);
                if (el && el.GetText && el.GetText() && el.GetTextPr) {
                  pt = sizePt(el.GetTextPr());
                }
              }
              if (!pt && para.GetTextPr) pt = sizePt(para.GetTextPr());
              if (!pt && doc.GetDefaultTextPr) pt = sizePt(doc.GetDefaultTextPr());
              return pt || Asc.scope.composedDefaultPt;
            }
            var drawings = doc.GetAllDrawingObjects();
            var count = 0;
            for (var d = 0; d < drawings.length; d++) {
              var drawing = drawings[d];
              try {
                if (!drawing.GetName || drawing.GetName() !== "marinaMoji composed character") continue;
                var para = drawing.GetParentParagraph();
                if (!para) continue;
                var pt = paragraphPt(para);
                var h = Math.round(pt * Asc.scope.composedInkScale * 12700);
                var oldH = drawing.GetHeight();
                var oldW = drawing.GetWidth();
                if (!oldH || Math.abs(h - oldH) < 1270) continue;
                drawing.SetSize(Math.round((oldW * h) / oldH), h);
                var run = drawing.GetParentRun ? drawing.GetParentRun() : null;
                if (run && run.SetPosition) run.SetPosition(-Math.round(pt * 2 * Asc.scope.composedDropEm));
                count++;
              } catch (e) {}
            }
            return count;
          },
          false,
          true,
          function (n) {
            resolve(typeof n === "number" ? n : 0);
          }
        );
      } catch (e) {
        resolve(0);
      }
    });
  }

  window.MarinaMojiComposer = { refreshSizes: refreshSizes };

  function start() {
    setStatus("Composer: waiting for a composed character.");
    window.setInterval(poll, POLL_MS);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
