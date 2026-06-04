#!/usr/bin/env node
/** Wait for HTTPS server, then register add-in and optionally launch Word. */
import https from "node:https";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const url = "https://localhost:3000/commands.html";

function probe(attempt) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { rejectUnauthorized: false }, (res) => {
      res.resume();
      if (res.statusCode && res.statusCode < 500) resolve();
      else reject(new Error(`HTTP ${res.statusCode}`));
    });
    req.on("error", reject);
    req.setTimeout(2000, () => {
      req.destroy();
      reject(new Error("timeout"));
    });
  }).catch((err) => {
    if (attempt >= 30) throw err;
    return new Promise((r) => setTimeout(r, 500)).then(() => probe(attempt + 1));
  });
}

await probe(0);
console.log("Server is up; sideloading add-in…");
const child = spawn(
  "npx",
  ["office-addin-debugging", "start", "manifest.xml", "desktop"],
  { cwd: root, stdio: "inherit", shell: true }
);
child.on("exit", (code) => process.exit(code ?? 0));
