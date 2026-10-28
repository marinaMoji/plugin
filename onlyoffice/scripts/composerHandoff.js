/*
 * marinaMoji character composer -> ONLYOFFICE.
 *
 * Keep this panel open. On Insert the composer writes composer_result.js next
 * to index.html (and copies the SVG to the clipboard). The panel polls that
 * file (script tag, # cache-bust only — a ?query breaks file:// on Desktop)
 * and also checks the clipboard, then inserts an inline PNG at the caret.
 */
(function () {
  "use strict";

  var POLL_MS = 1000;
  var MAX_AGE_MS = 120000;
  var RASTER_HEIGHT_PX = 256;
  var DEFAULT_PT = 12;
  // Full-body IDS drawings fill the em square; do not apply the kaeriten drop.
  var INK_SCALE = 0.94;
  var DROP_EM = 0;
  var STORE_KEY = "marinamoji.composer.lastId";

  var busy = false;
  var memoryId = 0;
  var started = false;
  var lastClipboardHash = "";

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
    } catch (e) {}
    memoryId = id;
  }

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

  function hashText(text) {
    var h = 5381;
    for (var i = 0; i < text.length; i++) h = ((h << 5) + h) ^ text.charCodeAt(i);
    return (h >>> 0).toString(16);
  }

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
          canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
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

  function pasteHtml(png) {
    var heightPx = Math.round((DEFAULT_PT * 96) / 72);
    var html =
      '<img src="' +
      png.dataUrl +
      '" width="' +
      Math.round(heightPx * png.aspect) +
      '" height="' +
      heightPx +
      '" alt="marinaMoji composed character"/>';
    if (!window.Asc || !window.Asc.plugin || !window.Asc.plugin.executeMethod) {
      throw new Error("ONLYOFFICE plugin API is not ready");
    }
    window.Asc.plugin.executeMethod("PasteHtml", [html]);
  }

  function insertAtCursor(png, done) {
    var asc = window.Asc;
    if (!asc || !asc.plugin || !asc.plugin.callCommand) {
      try {
        pasteHtml(png);
        done(true);
      } catch (e) {
        done(false);
      }
      return;
    }
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
                  pt = el.GetFontSize
                    ? sizePt({
                        GetFontSize: function () {
                          return el.GetFontSize();
                        },
                      })
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
          if (run.SetPosition) run.SetPosition(0);
          run.AddDrawing(drawing);
          var para = Api.CreateParagraph();
          para.AddElement(run);
          var clean = Api.CreateRun();
          if (clean.SetPosition) clean.SetPosition(0);
          para.AddElement(clean);
          doc.InsertContent([para], true);
          return pt || true;
        },
        false,
        true,
        function (ok) {
          if (!ok) {
            try {
              pasteHtml(png);
              done(true);
            } catch (e) {
              done(false);
            }
          } else {
            done(ok);
          }
        }
      );
    } catch (e) {
      try {
        pasteHtml(png);
        done(true);
      } catch (e2) {
        done(false);
      }
    }
  }

  function insertSvg(svg, id) {
    if (typeof svg !== "string" || svg.indexOf("<svg") < 0) return false;
    id = Number(id) || Date.now();
    if (id <= Math.max(lastSeenId(), memoryId)) return false;
    if (Date.now() - id > MAX_AGE_MS) {
      rememberId(id);
      return false;
    }
    if (busy) return false;
    busy = true;
    setStatus("Inserting composed character…");
    svgToPng(svg)
      .then(function (png) {
        return new Promise(function (resolve) {
          insertAtCursor(png, resolve);
        });
      })
      .then(function (ok) {
        if (ok) {
          rememberId(id);
          setStatus(
            "Inserted composed character" +
              (typeof ok === "number" ? " at " + ok + " pt." : ".")
          );
        } else {
          setStatus("Insert failed. Click in the document, then try Insert composed.");
        }
      })
      .catch(function (e) {
        setStatus("Insert failed: " + (e && e.message ? e.message : e));
      })
      .then(function () {
        busy = false;
      });
    return true;
  }

  function composerResultUrl() {
    try {
      var href = String(window.location.href || "");
      var base = href.replace(/[#?].*$/, "").replace(/[^/]*$/, "");
      return base + "composer_result.js#" + Date.now();
    } catch (e) {
      return "composer_result.js#" + Date.now();
    }
  }

  function loadComposerResultScript() {
    return new Promise(function (resolve) {
      window.marinaMojiComposerResult = undefined;
      var old = document.getElementById("composer-result-script");
      if (old && old.parentNode) old.parentNode.removeChild(old);
      var s = document.createElement("script");
      s.id = "composer-result-script";
      s.charset = "utf-8";
      var settled = false;
      function finish() {
        if (settled) return;
        settled = true;
        resolve(window.marinaMojiComposerResult);
      }
      s.onload = finish;
      s.onerror = finish;
      s.src = composerResultUrl();
      document.head.appendChild(s);
      window.setTimeout(finish, 800);
    });
  }

  function readClipboardSvg() {
    if (!navigator.clipboard || !navigator.clipboard.readText) {
      return Promise.resolve(null);
    }
    return navigator.clipboard
      .readText()
      .then(function (text) {
        if (text && text.indexOf("<svg") >= 0) return text.trim();
        return null;
      })
      .catch(function () {
        return null;
      });
  }

  function poll() {
    if (busy) return;
    loadComposerResultScript().then(function (result) {
      if (result && insertSvg(result.svg, result.id)) return;
      return readClipboardSvg().then(function (svg) {
        if (!svg) return;
        var h = hashText(svg);
        if (h === lastClipboardHash) return;
        if (insertSvg(svg, Date.now())) lastClipboardHash = h;
      });
    });
  }

  function refreshSizes() {
    return new Promise(function (resolve) {
      var asc = window.Asc;
      if (!asc || !asc.plugin || !asc.plugin.callCommand) {
        resolve(0);
        return;
      }
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
                if (!drawing.GetName || drawing.GetName() !== "marinaMoji composed character") {
                  continue;
                }
                var para = drawing.GetParentParagraph();
                if (!para) continue;
                var pt = paragraphPt(para);
                var h = Math.round(pt * Asc.scope.composedInkScale * 12700);
                var oldH = drawing.GetHeight();
                var oldW = drawing.GetWidth();
                if (!oldH || Math.abs(h - oldH) < 1270) continue;
                drawing.SetSize(Math.round((oldW * h) / oldH), h);
                var run = drawing.GetParentRun ? drawing.GetParentRun() : null;
                if (run && run.SetPosition) {
                  run.SetPosition(-Math.round(pt * 2 * Asc.scope.composedDropEm));
                }
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

  function startPolling() {
    if (started) return;
    started = true;
    setStatus("Composer: waiting for a composed character.");
    poll();
    window.setInterval(poll, POLL_MS);
  }

  window.MarinaMojiComposer = {
    refreshSizes: refreshSizes,
    pollNow: poll,
    start: startPolling,
  };

  function arm() {
    if (!window.Asc || !window.Asc.plugin) {
      setStatus("Open this panel from Plugins → marinaMoji.");
      window.setTimeout(arm, 500);
      return;
    }
    var prev = window.Asc.plugin.init;
    window.Asc.plugin.init = function (data) {
      if (typeof prev === "function") prev.call(window.Asc.plugin, data);
      startPolling();
    };
    window.setTimeout(function () {
      if (!started) startPolling();
    }, 1500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", arm);
  } else {
    arm();
  }
})();
