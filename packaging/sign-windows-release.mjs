#!/usr/bin/env node
// Authenticode-sign the Windows Word installer of a published plugins-v* release.
//
// Same flow as marinaMoji/scripts/sign-windows-release.mjs: download from the
// GitHub Release, sign with the maintainer's `sign-windows` command (Certum
// SimplySign via PKCS#11; SimplySign Desktop must be running and logged in),
// verify, rewrite the exe line in SHA256SUMS.txt, re-upload and re-verify.
//
// Usage: node packaging/sign-windows-release.mjs <tag> [--upload] [--work-dir DIR]
// Without --upload nothing on GitHub is modified; results are staged in <work-dir>/new.

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import process from 'node:process';

const REPO = 'marinaMoji/plugin';
const EXE = 'marinamoji-kaeriten-word-setup.exe';
const SUMS = 'SHA256SUMS.txt';

const args = process.argv.slice(2);
const upload = args.includes('--upload');
const workFlag = args.indexOf('--work-dir');
const tag = args.find((arg, i) => !arg.startsWith('--') && args[i - 1] !== '--work-dir');
if (!tag || !/^plugins-v\d/.test(tag)) {
  throw new Error('Usage: sign-windows-release.mjs <plugins-vX.Y.Z> [--upload] [--work-dir DIR]');
}
const workDir =
  workFlag >= 0 ? path.resolve(args[workFlag + 1]) : mkdtempSync(path.join(tmpdir(), 'sign-win-plugin-'));
const origDir = path.join(workDir, 'orig');
const newDir = path.join(workDir, 'new');
const liveDir = path.join(workDir, 'live');
for (const d of [origDir, newDir, liveDir]) mkdirSync(d, { recursive: true });

const run = (cmd, cmdArgs, options = {}) =>
  execFileSync(cmd, cmdArgs, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'], ...options });
const gh = (...a) => run('gh', [...a, '-R', REPO]);
const sha256 = (file) => createHash('sha256').update(readFileSync(file)).digest('hex');
const log = (m) => process.stdout.write(`${m}\n`);
const bundle = path.join(process.env.HOME, '.config/sign-windows/ca/verify-bundle.pem');
const verifySignature = (file) =>
  run('osslsigncode', ['verify', '-CAfile', bundle, '-TSA-CAfile', bundle, '-in', file]);

for (const tool of ['gh', 'sign-windows', 'osslsigncode']) {
  try {
    run('which', [tool]);
  } catch {
    throw new Error(`Required tool not found on PATH: ${tool}`);
  }
}

// Lines look like "<hash>  ./name", "<hash>  name" or (Windows sha256sum) "<hash> *name".
const parseSums = (text) =>
  text.trimEnd().split('\n').map((line) => {
    const [hash, name] = line.split(/\s+/);
    return { line, hash, name, base: name.replace(/^[*]/, '').replace(/^\.\//, '') };
  });

log(`Downloading ${tag} Windows installer to ${origDir}`);
gh('release', 'download', tag, '--dir', origDir, '--clobber', '-p', EXE, '-p', SUMS);

const sums = parseSums(readFileSync(path.join(origDir, SUMS), 'utf8'));
const entries = sums.filter((s) => s.base === EXE);
if (entries.length !== 1) throw new Error(`Expected one ${EXE} line in ${SUMS}, found ${entries.length}`);
if (entries[0].hash !== sha256(path.join(origDir, EXE))) {
  throw new Error(`${EXE} does not match ${SUMS}; refusing to continue`);
}
try {
  run('osslsigncode', ['extract-signature', '-in', path.join(origDir, EXE), '-out', path.join(workDir, 'probe.sig')]);
  throw new Error(`${EXE} is already signed; nothing to do`);
} catch (error) {
  if (error.message.includes('already signed')) throw error;
  // No signature present: expected.
}

log(`\nSigning ${EXE}`);
run('sign-windows', ['--force', '-n', 'marinaMoji', '-o', path.join(newDir, EXE), path.join(origDir, EXE)], {
  stdio: 'inherit',
});
verifySignature(path.join(newDir, EXE));

writeFileSync(
  path.join(newDir, SUMS),
  `${sums
    .map((s) => (s.base === EXE ? s.line.replace(s.hash, sha256(path.join(newDir, EXE))) : s.line))
    .join('\n')}\n`,
);
log('Staged signature verified.');
try {
  run('diff', ['-u', path.join(origDir, SUMS), path.join(newDir, SUMS)]);
} catch (error) {
  log(error.stdout);
}

if (!upload) {
  log(`\nDry run: nothing uploaded. Re-run with --upload to publish (originals in ${origDir}).`);
  process.exit(0);
}

for (const name of [EXE, SUMS]) {
  log(`Uploading ${name}`);
  gh('release', 'upload', tag, path.join(newDir, name), '--clobber');
}
gh('release', 'download', tag, '--dir', liveDir, '--clobber', '-p', EXE, '-p', SUMS);
const digests = new Map(
  JSON.parse(gh('release', 'view', tag, '--json', 'assets')).assets.map((a) => [a.name, a.digest]),
);
for (const name of [EXE, SUMS]) {
  const live = path.join(liveDir, name);
  if (sha256(live) !== sha256(path.join(newDir, name))) throw new Error(`Live ${name} differs from staged`);
  if (digests.get(name) !== `sha256:${sha256(live)}`) throw new Error(`GitHub digest mismatch for ${name}`);
}
verifySignature(path.join(liveDir, EXE));
const liveEntry = parseSums(readFileSync(path.join(liveDir, SUMS), 'utf8')).find((s) => s.base === EXE);
if (liveEntry.hash !== sha256(path.join(liveDir, EXE))) throw new Error(`Live ${SUMS} does not match live ${EXE}`);
log(`\nUploaded and verified. Originals kept in ${origDir}.`);
