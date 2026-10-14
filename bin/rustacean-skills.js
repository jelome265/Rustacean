#!/usr/bin/env node
// Thin launcher for tools/install_skills.py. The Python installer is the single
// source of truth: it validates the suite, computes a full plan, dry-runs by
// default, and verifies content hashes after --apply. This file only finds a
// Python 3 interpreter and forwards arguments and the exit code unchanged.
"use strict";

const { spawnSync } = require("node:child_process");
const path = require("node:path");

const installer = path.join(__dirname, "..", "tools", "install_skills.py");

// RUSTACEAN_PYTHON overrides discovery (useful in CI and on unusual setups).
const candidates = process.env.RUSTACEAN_PYTHON
  ? [process.env.RUSTACEAN_PYTHON]
  : process.platform === "win32"
    ? ["py", "python", "python3"]
    : ["python3", "python"];

function findPython() {
  for (const cmd of candidates) {
    const probe = spawnSync(cmd, ["-c", "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)"], {
      stdio: "ignore",
      windowsHide: true,
    });
    if (probe.status === 0) return cmd;
  }
  return null;
}

const python = findPython();
if (python === null) {
  process.stderr.write(
    "rustacean-skills: Python 3 was not found on PATH.\n" +
      "Install Python 3, or set RUSTACEAN_PYTHON to the interpreter to use.\n",
  );
  process.exit(2);
}

const args = process.argv.slice(2);
const result = spawnSync(python, [installer, ...args], { stdio: "inherit", windowsHide: true });

if (result.error) {
  process.stderr.write(`rustacean-skills: failed to start ${python}: ${result.error.message}\n`);
  process.exit(2);
}
process.exit(result.status === null ? 1 : result.status);
