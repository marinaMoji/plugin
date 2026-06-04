#!/usr/bin/env node
/** Stop whatever is listening on port 3000 (dev add-in server). */
import { execSync } from "node:child_process";

const port = 3000;
let pids;
try {
  pids = execSync(`lsof -ti :${port}`, { encoding: "utf8" }).trim();
} catch {
  console.log(`Nothing listening on port ${port}.`);
  process.exit(0);
}
if (!pids) {
  console.log(`Nothing listening on port ${port}.`);
  process.exit(0);
}
for (const pid of pids.split(/\s+/)) {
  try {
    process.kill(Number(pid), "SIGTERM");
    console.log(`Stopped process ${pid} on port ${port}.`);
  } catch (err) {
    console.warn(`Could not stop PID ${pid}:`, err.message);
  }
}
