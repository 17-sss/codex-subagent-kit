import { readFileSync } from "node:fs";

import { computeNextVersion } from "./release-versioning";

function main(): number {
  const baseVersion = process.env.BASE_VERSION;
  const commitsFile = process.env.COMMITS_FILE;

  if (!baseVersion) {
    console.error("missing BASE_VERSION");
    return 1;
  }
  if (!commitsFile) {
    console.error("missing COMMITS_FILE");
    return 1;
  }

  const rawMessages = readFileSync(commitsFile, "utf8");
  const messages = rawMessages
    .split("---commit-boundary---")
    .map((chunk) => chunk.trim())
    .filter(Boolean);

  console.log(computeNextVersion(baseVersion, messages));
  return 0;
}

if (require.main === module) {
  process.exitCode = main();
}
