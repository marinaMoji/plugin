#!/usr/bin/env node
/**
 * Print HTTPS / certificate diagnostics for Word dev (run anytime).
 */
import { execSync } from "node:child_process";
import fs from "node:fs";
import https from "node:https";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  resolveCertPaths,
  probeTrust,
  mkcertInstalledInSystem,
  probeRequestOptions,
} from "./https-probe.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");
const url = "https://127.0.0.1:3000/taskpane.html";

function line(label, value) {
  console.log(`${label.padEnd(28)} ${value}`);
}

function whichMkcert() {
  try {
    return execSync("which mkcert", { encoding: "utf8", shell: "/bin/bash" }).trim();
  } catch {
    return "(not found)";
  }
}

function realMkcertPath() {
  for (const p of [
    process.env.MKCERT_PATH,
    "/opt/homebrew/bin/mkcert",
    "/usr/local/bin/mkcert",
  ]) {
    if (p && fs.existsSync(p)) {
      try {
        execSync(`"${p}" -CAROOT`, { encoding: "utf8", shell: "/bin/bash" });
        return p;
      } catch {
        /* not real mkcert */
      }
    }
  }
  return null;
}

console.log("marinaMoji Word — HTTPS diagnose\n");

line("Node", process.version);
line("NODE_OPTIONS", process.env.NODE_OPTIONS || "(not set)");

const paths = resolveCertPaths();
line("Certificate mode", paths.source);
line("Cert file", paths.cert);
line("Key file", paths.key);
line("Cert exists", String(fs.existsSync(paths.cert)));

const w = whichMkcert();
const real = realMkcertPath();
line("which mkcert", w);
line("Real mkcert (brew)", real || "(install: brew install mkcert)");

if (w && w.includes("node_modules") && w.includes("mkcert")) {
  console.log("");
  console.log("⚠️  PATH points at npm’s unrelated “mkcert” package, not FiloSottile/mkcert.");
  console.log("   Our scripts use Homebrew’s mkcert only. Run:");
  console.log("     brew install mkcert");
  console.log("     /opt/homebrew/bin/mkcert -install");
  console.log("     npm run setup:certs");
}

line("mkcert in keychain", mkcertInstalledInSystem() ? "yes" : "no");

const caroot = path.join(
  process.env.HOME || "",
  "Library/Application Support/mkcert/rootCA.pem"
);
line("mkcert rootCA.pem", fs.existsSync(caroot) ? caroot : "missing");

const probeOpts = probeRequestOptions(paths.source);
line("Probe uses mkcert CA file", probeOpts.ca ? "yes" : "no");

const trusted = await probeTrust(url, paths.source);
line("HTTPS probe", trusted ? "OK" : "FAIL");
line("URL", url);

if (!trusted) {
  console.log("");
  console.log("Fix order:");
  console.log("  1. brew install mkcert");
  console.log("  2. /opt/homebrew/bin/mkcert -install   (Terminal.app, Mac password)");
  console.log("  3. npm run setup:certs");
  console.log("  4. npm run serve:stop && npm run serve");
  console.log("  5. npm run doctor");
  console.log("");
  console.log("Open in Safari — should load with no “not secure” warning:");
  console.log(`  ${url}`);
} else {
  console.log("");
  console.log("HTTPS looks good from Node. If Word is still blank:");
  console.log("  • Accueil → Kaeriten → Kaeriten pane (not Compléments preview only)");
  console.log("  • npm run reset-word, quit Word (Cmd+Q), reopen");
}
