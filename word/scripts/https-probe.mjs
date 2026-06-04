/**
 * HTTPS probe that matches how we trust certs for local Word dev.
 * Node 25+ does not use the macOS keychain unless --use-system-ca;
 * mkcert certs are verified using mkcert's rootCA.pem.
 */
import { execSync } from "node:child_process";
import fs from "node:fs";
import https from "node:https";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");

export function resolveCertPaths() {
  const mkcertCert = path.join(rootDir, "certs", "cert.pem");
  const mkcertKey = path.join(rootDir, "certs", "key.pem");
  if (fs.existsSync(mkcertCert) && fs.existsSync(mkcertKey)) {
    return { cert: mkcertCert, key: mkcertKey, source: "mkcert" };
  }
  const certDir = path.join(process.env.HOME || "", ".office-addin-dev-certs");
  return {
    cert: path.join(certDir, "localhost.crt"),
    key: path.join(certDir, "localhost.key"),
    source: "office-addin-dev-certs",
  };
}

function findMkcert() {
  if (process.env.MKCERT_PATH && fs.existsSync(process.env.MKCERT_PATH)) {
    return process.env.MKCERT_PATH;
  }
  for (const p of ["/opt/homebrew/bin/mkcert", "/usr/local/bin/mkcert"]) {
    if (fs.existsSync(p)) return p;
  }
  try {
    const p = execSync("which mkcert", { encoding: "utf8", shell: "/bin/bash" }).trim();
    if (p && fs.existsSync(p)) return p;
  } catch {
    /* ignore */
  }
  return null;
}

function mkcertRootCaPem() {
  const caroot = path.join(
    process.env.HOME || "",
    "Library",
    "Application Support",
    "mkcert"
  );
  const root = path.join(caroot, "rootCA.pem");
  if (fs.existsSync(root)) return fs.readFileSync(root);
  const mkcert = findMkcert();
  if (!mkcert) return null;
  try {
    const dir = execSync(`"${mkcert}" -CAROOT`, {
      encoding: "utf8",
      shell: "/bin/bash",
    }).trim();
    const root2 = path.join(dir, "rootCA.pem");
    if (fs.existsSync(root2)) return fs.readFileSync(root2);
  } catch {
    /* ignore */
  }
  return null;
}

export function probeRequestOptions(certSource) {
  const opts = { rejectUnauthorized: true };
  if (certSource === "mkcert") {
    const ca = mkcertRootCaPem();
    if (ca) opts.ca = ca;
  }
  return opts;
}

export function probeTrust(url, certSource) {
  return new Promise((resolve) => {
    const req = https.get(url, probeRequestOptions(certSource), (res) => {
      res.resume();
      resolve(Boolean(res.statusCode && res.statusCode < 500));
    });
    req.on("error", () => resolve(false));
    req.setTimeout(4000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

/** True if mkcert root is in the system trust store (Word needs this). */
export function mkcertInstalledInSystem() {
  try {
    execSync('security find-certificate -c "mkcert" -a', { stdio: "pipe" });
    return true;
  } catch {
    try {
      execSync('security find-certificate -c "mkcert development CA" -a', {
        stdio: "pipe",
      });
      return true;
    } catch {
      return false;
    }
  }
}
