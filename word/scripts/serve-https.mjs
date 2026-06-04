#!/usr/bin/env node
/**
 * Serve plugin/word/dist over HTTPS on port 3000 (required by manifest.xml).
 */
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import httpServer from "http-server";
import {
  resolveCertPaths,
  probeTrust,
  mkcertInstalledInSystem,
} from "./https-probe.mjs";

const require = createRequire(import.meta.url);
const devCerts = require("office-addin-dev-certs");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const distDir = path.resolve(__dirname, "..", "dist");
const port = 3000;
const probeUrl = `https://127.0.0.1:${port}/taskpane.html`;

if (!fs.existsSync(distDir)) {
  console.error("dist/ not found. Run: npm run build");
  process.exit(1);
}

async function main() {
  const paths = resolveCertPaths();
  if (paths.source === "office-addin-dev-certs") {
    await devCerts.ensureCertificatesAreInstalled();
  } else {
    console.log("Using mkcert certificates from certs/");
    if (!mkcertInstalledInSystem()) {
      console.warn("");
      console.warn("WARNING: mkcert -install may not have finished.");
      console.warn("Word needs this once (in Terminal.app):");
      console.warn("  mkcert -install");
      console.warn("");
    }
  }

  const server = httpServer.createServer({
    root: distDir,
    cache: -1,
    cors: true,
    https: { cert: paths.cert, key: paths.key },
    headers: { "Access-Control-Allow-Origin": "*" },
  });

  server.server.on("error", async (err) => {
    if (err.code === "EADDRINUSE") {
      if (await probeTrust(probeUrl, paths.source)) {
        console.log(`HTTPS server already running on https://127.0.0.1:${port}/`);
        process.exit(0);
      }
      console.error("");
      console.error(`Port ${port} is in use but HTTPS probe to ${probeUrl} failed.`);
      console.error("Another program may be bound there (sometimes an old HTTP-only server).");
      console.error("Run:  npm run serve:stop");
      console.error("Then: npm run serve");
      console.error("Or:   npm run diagnose");
      process.exit(1);
    }
    console.error(err);
    process.exit(1);
  });

  server.listen(port, "127.0.0.1", async () => {
    const strict = await probeTrust(probeUrl, paths.source);
    if (!strict) {
      console.error("");
      console.error("Server started but HTTPS self-test failed.");
      console.error("Run:  npm run diagnose");
      console.error("      brew install mkcert && /opt/homebrew/bin/mkcert -install");
      console.error("      npm run setup:certs");
      console.error("Or:   npm run trust:fix   (Microsoft dev certs instead of mkcert)");
      process.exit(1);
    }

    console.log(`marinaMoji Word add-in: https://127.0.0.1:${port}/`);
    console.log(`Certificates: ${paths.source}`);
    if (paths.source === "mkcert" && !mkcertInstalledInSystem()) {
      console.log(
        "Server OK. Run: mkcert -install  then restart Word if the pane is blank."
      );
    } else {
      console.log("HTTPS trusted — OK for Word.");
    }
    console.log("Leave this running. Press Ctrl+C to stop.");
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
