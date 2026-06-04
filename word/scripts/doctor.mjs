#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import {
  resolveCertPaths,
  probeTrust,
  mkcertInstalledInSystem,
} from "./https-probe.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");
const home = process.env.HOME || "";
const wef = path.join(
  home,
  "Library/Containers/com.microsoft.Word/Data/Documents/wef"
);

let ok = true;
function line(title, good, detail) {
  console.log(`[${good ? "OK" : "FAIL"}] ${title}`);
  if (detail) console.log(`      ${detail}`);
  if (!good) ok = false;
}

console.log("marinaMoji Word add-in — doctor\n");

const paths = resolveCertPaths();
line(
  "Certificate mode",
  true,
  paths.source === "mkcert"
    ? "mkcert (certs/)"
    : "office-addin-dev-certs"
);

if (paths.source === "mkcert") {
  line(
    "mkcert -install (system trust)",
    mkcertInstalledInSystem(),
    mkcertInstalledInSystem()
      ? "Word can load https://127.0.0.1:3000"
      : "Run in Terminal.app:  mkcert -install"
  );
}

const taskpane = path.join(rootDir, "dist", "taskpane.html");
line("Built dist/taskpane.html", fs.existsSync(taskpane), taskpane);

const manifests = fs.existsSync(wef)
  ? fs.readdirSync(wef).filter((f) => f.endsWith(".xml"))
  : [];
line(
  "Word sideload manifest",
  manifests.length > 0,
  manifests.length ? manifests.join(", ") : "Run: ./install-mac.sh"
);

const url = "https://127.0.0.1:3000/taskpane.html";
const serverOk = await probeTrust(url, paths.source);
line(
  "Dev server + HTTPS",
  serverOk,
  serverOk
    ? url
    : "Run: npm run serve  (in another terminal), then npm run doctor again"
);

console.log("");
if (!ok) {
  if (paths.source === "mkcert" && !mkcertInstalledInSystem()) {
    console.log("Most likely fix:");
    console.log("  mkcert -install");
    console.log("  npm run serve");
    console.log("  npm run reset-word");
    console.log("  Quit Word (Cmd+Q), reopen Compléments → marinaMoji Kaeriten");
  }
  console.log("Run:  npm run diagnose");
  process.exit(1);
}
console.log("All checks passed.");
