/**
 * Compare hosted version.json to the versions baked into this build.
 * Failures are silent — never block Render.
 */

/* global __MM_WORD_VERSION__, __MM_WORD_MANIFEST__, __MM_VERSION_JSON_URL__ */

export const DEFAULT_VERSION_JSON_URL =
  "https://marinamoji.github.io/plugin/version.json";

export function localWordVersion() {
  return typeof __MM_WORD_VERSION__ !== "undefined"
    ? __MM_WORD_VERSION__
    : "0.1.3";
}

export function localWordManifest() {
  return typeof __MM_WORD_MANIFEST__ !== "undefined"
    ? __MM_WORD_MANIFEST__
    : "0.1.3.0";
}

export function versionJsonUrl() {
  if (typeof window !== "undefined" && window.__MM_VERSION_JSON_URL__) {
    return window.__MM_VERSION_JSON_URL__;
  }
  return typeof __MM_VERSION_JSON_URL__ !== "undefined"
    ? __MM_VERSION_JSON_URL__
    : DEFAULT_VERSION_JSON_URL;
}

/** Parse dotted version strings (e.g. 0.1.3 or 0.1.3.0) into number parts. */
export function parseVersionParts(v) {
  if (v == null || v === "") return [];
  return String(v)
    .trim()
    .split(/[.+-]/)
    .filter((p) => p.length)
    .map((p) => {
      const n = parseInt(p, 10);
      return Number.isFinite(n) ? n : 0;
    });
}

/** Return 1 if a > b, -1 if a < b, 0 if equal. */
export function compareVersions(a, b) {
  const pa = parseVersionParts(a);
  const pb = parseVersionParts(b);
  const len = Math.max(pa.length, pb.length);
  for (let i = 0; i < len; i++) {
    const x = pa[i] || 0;
    const y = pb[i] || 0;
    if (x > y) return 1;
    if (x < y) return -1;
  }
  return 0;
}

/**
 * @param {object} remote - parsed version.json
 * @param {{ word?: string, word_manifest?: string }} local
 * @returns {{ show: boolean, codeNewer: boolean, manifestNewer: boolean, releaseUrl: string, remoteWord: string }}
 */
export function evaluateUpdate(remote, local = {}) {
  const wordLocal = local.word != null ? local.word : localWordVersion();
  const manifestLocal =
    local.word_manifest != null ? local.word_manifest : localWordManifest();
  const remoteWord = remote && remote.word != null ? String(remote.word) : "";
  const remoteManifest =
    remote && remote.word_manifest != null
      ? String(remote.word_manifest)
      : "";
  const codeNewer =
    remoteWord.length > 0 && compareVersions(remoteWord, wordLocal) > 0;
  const manifestNewer =
    remoteManifest.length > 0 &&
    compareVersions(remoteManifest, manifestLocal) > 0;
  const releaseUrl =
    (remote && remote.release_url) ||
    "https://github.com/marinaMoji/plugin/releases/latest";
  return {
    show: codeNewer || manifestNewer,
    codeNewer,
    manifestNewer,
    releaseUrl,
    remoteWord: remoteWord || wordLocal,
  };
}

/**
 * Fetch version.json and decide whether to show a banner.
 * @returns {Promise<ReturnType<typeof evaluateUpdate>|null>}
 */
export async function fetchUpdateInfo(url = versionJsonUrl()) {
  try {
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) return null;
    const remote = await res.json();
    return evaluateUpdate(remote);
  } catch {
    return null;
  }
}

/**
 * Show a dismissible update banner in the task pane (once per session).
 * @param {HTMLElement|null} host
 * @param {ReturnType<typeof evaluateUpdate>} info
 */
export function showUpdateBanner(host, info) {
  if (!host || !info || !info.show) return;
  if (typeof sessionStorage !== "undefined") {
    try {
      if (sessionStorage.getItem("mmUpdateBannerDismissed") === "1") return;
    } catch {
      /* ignore */
    }
  }
  if (host.querySelector(".update-banner")) return;

  const banner = document.createElement("div");
  banner.className = "update-banner";
  banner.setAttribute("role", "status");

  let body;
  if (info.manifestNewer) {
    body =
      "A newer Word add-in registration is available. Download the Mac installer or production manifest from the release page, install it, then quit and reopen Word.";
  } else {
    body =
      "A newer Word add-in build is available. Quit and reopen Word (online) to load the latest code from GitHub Pages.";
  }

  const text = document.createElement("p");
  text.className = "update-banner-text";
  text.textContent = body;

  const meta = document.createElement("p");
  meta.className = "update-banner-meta";
  meta.textContent = `Remote ${info.remoteWord} · local ${localWordVersion()}`;

  const actions = document.createElement("div");
  actions.className = "update-banner-actions";

  const link = document.createElement("a");
  link.href = info.releaseUrl;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = "Release notes";

  const dismiss = document.createElement("button");
  dismiss.type = "button";
  dismiss.className = "update-banner-dismiss";
  dismiss.textContent = "Dismiss";
  dismiss.addEventListener("click", () => {
    banner.remove();
    try {
      sessionStorage.setItem("mmUpdateBannerDismissed", "1");
    } catch {
      /* ignore */
    }
  });

  actions.appendChild(link);
  actions.appendChild(dismiss);
  banner.appendChild(text);
  banner.appendChild(meta);
  banner.appendChild(actions);

  const header = host.querySelector("header");
  if (header && header.nextSibling) {
    host.insertBefore(banner, header.nextSibling);
  } else {
    host.insertBefore(banner, host.firstChild);
  }
}
