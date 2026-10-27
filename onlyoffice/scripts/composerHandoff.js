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
  var TARGET_HEIGHT_PX = 20; // inline height; the SVG is square
  var SUPERSAMPLE = 4;
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

  /** Rasterises |svg| to a PNG data URL; resolves {dataUrl, width, height} in CSS px. */
  function svgToPng(svg) {
    return new Promise(function (resolve, reject) {
      var size = svgSize(svg);
      var heightPx = TARGET_HEIGHT_PX;
      var widthPx = Math.round((heightPx * size.width) / size.height);
      var img = new Image();
      img.onload = function () {
        try {
          var canvas = document.createElement("canvas");
          canvas.width = widthPx * SUPERSAMPLE;
          canvas.height = heightPx * SUPERSAMPLE;
          var ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          resolve({
            dataUrl: canvas.toDataURL("image/png"),
            width: widthPx,
            height: heightPx,
          });
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

  function insertAtCursor(png) {
    var html =
      '<img src="' + png.dataUrl + '" width="' + png.width +
      '" height="' + png.height + '" alt="marinaMoji composed character"/>';
    window.Asc.plugin.executeMethod("PasteHtml", [html]);
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
        insertAtCursor(png);
        rememberId(id);
        setStatus("Inserted composed character.");
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
