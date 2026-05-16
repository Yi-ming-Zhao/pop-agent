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
const pathSeparator = process.platform === "win32" ? ";" : ":";
const pythonPath = [root, process.env.PYTHONPATH].filter(Boolean).join(pathSeparator);

let result;
let selectedPython;
for (const python of pythonCandidates) {
  selectedPython = python;
  result = spawnSync(
    python,
    ["-m", "pop_agent", ...process.argv.slice(2)],
    {
      cwd: root,
      stdio: "inherit",
      env: { ...process.env, PYTHONPATH: pythonPath },
    },
  );
  if (!result.error) break;
}

if (result?.error) {
  console.error(`Failed to run ${selectedPython}: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
