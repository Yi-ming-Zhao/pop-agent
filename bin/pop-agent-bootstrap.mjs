#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const python = process.env.PYTHON || process.env.PYTHON3 || "python3";

const result = spawnSync(
  python,
  ["bootstrap.py", ...process.argv.slice(2)],
  {
    cwd: root,
    stdio: "inherit",
  },
);

if (result.error) {
  console.error(`Failed to run ${python}: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
