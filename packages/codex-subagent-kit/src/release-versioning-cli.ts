import { readFileSync } from "node:fs";

import { computeNextVersionFromLabels } from "./release-versioning";

function main(): number {
  const baseVersion = process.env.BASE_VERSION;
  const labelsFile = process.env.LABELS_FILE;
  const initialRelease = process.env.INITIAL_RELEASE === "1";

  if (!baseVersion) {
    console.error("missing BASE_VERSION");
    return 1;
  }
  if (!labelsFile) {
    console.error("missing LABELS_FILE");
    return 1;
  }

  const rawLabels = readFileSync(labelsFile, "utf8");
  const labels = rawLabels
    .split(/\r?\n/)
    .map((chunk) => chunk.trim())
    .filter(Boolean);

  const version = computeNextVersionFromLabels(baseVersion, labels, { initialRelease });
  console.log(version ?? "skip");
  return 0;
}

if (require.main === module) {
  process.exitCode = main();
}
