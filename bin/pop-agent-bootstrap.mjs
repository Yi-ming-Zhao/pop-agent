#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const pythonCandidates = [
  process.env.PYTHON,
  process.env.PYTHON3,
  process.platform === "win32"
    ? resolve(root, ".venv", "Scripts", "python.exe")
    : resolve(root, ".venv", "bin", "python"),
  "python3",
  "python",
].filter(Boolean);

let result;
let selectedPython;
for (const python of pythonCandidates) {
  selectedPython = python;
  result = spawnSync(
    python,
    ["bootstrap.py", ...process.argv.slice(2)],
    {
      cwd: root,
      stdio: "inherit",
    },
  );
  if (!result.error) break;
}

if (result?.error) {
  console.error(`Failed to run ${selectedPython}: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
