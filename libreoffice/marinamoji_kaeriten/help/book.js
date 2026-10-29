/* Lightweight page navigation for The Little Book of Japanese Typography */
(function () {
  "use strict";

  var pages = Array.prototype.slice.call(
    document.querySelectorAll(".book-page[data-page]")
  );
  if (!pages.length) return;

  pages.sort(function (a, b) {
    return Number(a.getAttribute("data-page")) - Number(b.getAttribute("data-page"));
  });

  var total = pages.length;
  var indicator = document.querySelector(".page-indicator");
  var btnPrev = document.querySelector(".nav-prev");
  var btnNext = document.querySelector(".nav-next");
  var root = document.documentElement;
  var index = 0;

  function pad(n) {
    return (n < 10 ? "0" : "") + n;
  }

  function fmt(template, title) {
    if (!template) return title || "";
    return template.replace("%s", title || "");
  }

  function prevTemplate() {
    return root.getAttribute("data-nav-prev") || "← %s";
  }

  function nextTemplate() {
    return root.getAttribute("data-nav-next") || "Next: %s →";
  }

  function labelFor(pageEl) {
    if (!pageEl) return "";
    return pageEl.getAttribute("data-nav-title") || "";
  }

  function show(i) {
    if (i < 0) i = 0;
    if (i > total - 1) i = total - 1;
    index = i;
    pages.forEach(function (el, n) {
      var on = n === index;
      el.classList.toggle("is-active", on);
      el.setAttribute("aria-hidden", on ? "false" : "true");
    });
    if (indicator) {
      indicator.textContent = pad(index + 1) + " / " + pad(total);
    }
    if (btnPrev) {
      btnPrev.disabled = index === 0;
      if (index === 0) {
        btnPrev.textContent = "";
      } else {
        btnPrev.textContent = fmt(prevTemplate(), labelFor(pages[index - 1]));
      }
    }
    if (btnNext) {
      btnNext.disabled = index === total - 1;
      if (index === total - 1) {
        btnNext.textContent = "";
      } else if (index === 0) {
        btnNext.textContent =
          pages[0].getAttribute("data-begin-label") || "Begin reading →";
      } else {
        btnNext.textContent = fmt(nextTemplate(), labelFor(pages[index + 1]));
      }
    }
    try {
      window.scrollTo(0, 0);
    } catch (e) {}
  }

  if (btnPrev) {
    btnPrev.addEventListener("click", function () {
      show(index - 1);
    });
  }
  if (btnNext) {
    btnNext.addEventListener("click", function () {
      show(index + 1);
    });
  }

  document.addEventListener("keydown", function (ev) {
    var tag = (ev.target && ev.target.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") {
      return;
    }
    if (ev.key === "ArrowLeft") {
      ev.preventDefault();
      show(index - 1);
    } else if (ev.key === "ArrowRight") {
      ev.preventDefault();
      show(index + 1);
    }
  });

  var start = 0;
  pages.forEach(function (el, n) {
    if (el.classList.contains("is-active")) start = n;
  });
  show(start);

  // Dev / smoke helpers (optional)
  try {
    window.__marinamojiBookShow = show;
  } catch (e) {}
})();
