#!/usr/bin/env node
import { resolveCertPaths, probeTrust } from "./https-probe.mjs";

const url = "https://127.0.0.1:3000/taskpane.html";
const paths = resolveCertPaths();
const ok = await probeTrust(url, paths.source);
process.exit(ok ? 0 : 1);

