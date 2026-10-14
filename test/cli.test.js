"use strict";

const { test } = require("node:test");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const BIN = path.join(__dirname, "..", "bin", "rustacean-skills.js");
const SUITE = [
  "rust-enterprise-best-practices",
  "rust-enterprise-implement",
  "rust-enterprise-harden",
  "rust-enterprise-audit",
  "rust-enterprise-frameworks",
];

function run(args, env = {}) {
  return spawnSync(process.execPath, [BIN, ...args], {
    encoding: "utf8",
    env: { ...process.env, ...env },
  });
}

function tempProject() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "rustacean-skills-test-"));
}

test("--list prints supported agents and exits 0", () => {
  const r = run(["--list"]);
  assert.equal(r.status, 0, r.stderr);
  assert.match(r.stdout, /claude-code/);
  assert.match(r.stdout, /codex/);
});

test("default run is a dry run: exits 0 and writes nothing", () => {
  const project = tempProject();
  const r = run(["--agent", "codex", "--project-root", project]);
  assert.equal(r.status, 0, r.stderr + r.stdout);
  assert.match(r.stdout, /DRY RUN/);
  assert.equal(fs.existsSync(path.join(project, ".agents")), false);
});

test("--apply installs and verifies all five skills", () => {
  const project = tempProject();
  const r = run(["--agent", "codex", "--project-root", project, "--apply"]);
  assert.equal(r.status, 0, r.stderr + r.stdout);
  assert.match(r.stdout, /INSTALLED AND VERIFIED/);
  for (const name of SUITE) {
    assert.ok(
      fs.existsSync(path.join(project, ".agents", "skills", name, "SKILL.md")),
      `missing ${name}`,
    );
  }
});

test("a refused target exits 1 and writes nothing", () => {
  const project = tempProject();
  const r = run(["--agent", "kimi", "--project-root", project, "--apply"]);
  assert.equal(r.status, 1, r.stdout);
  assert.match(r.stdout + r.stderr, /REFUSED/);
  assert.equal(fs.existsSync(path.join(project, ".agents")), false);
});

test("an unknown agent is a usage error (non-zero)", () => {
  const r = run(["--agent", "no-such-agent", "--project-root", tempProject()]);
  assert.notEqual(r.status, 0);
});

test("a missing Python interpreter fails with a clear message and exit 2", () => {
  const r = run(["--list"], { RUSTACEAN_PYTHON: "/nonexistent/python-for-test" });
  assert.equal(r.status, 2);
  assert.match(r.stderr, /Python 3 was not found/);
});
