const SEMVER_PATTERN = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/;
const BREAKING_SUBJECT_PATTERN = /^[a-zA-Z]+(?:\([^)]+\))?!:/;
const FEATURE_SUBJECT_PATTERN = /^feat(?:\([^)]+\))?:/;

export type SemverBump = "major" | "minor" | "patch";

export function parseSemver(value: string): [number, number, number] {
  const match = value.trim().match(SEMVER_PATTERN);
  if (!match) {
    throw new Error(`invalid semantic version: ${value}`);
  }
  return [Number(match[1]), Number(match[2]), Number(match[3])];
}

export function bumpSemver(version: string, bump: SemverBump): string {
  const [major, minor, patch] = parseSemver(version);
  if (bump === "major") {
    return `${major + 1}.0.0`;
  }
  if (bump === "minor") {
    return `${major}.${minor + 1}.0`;
  }
  return `${major}.${minor}.${patch + 1}`;
}

export function classifyBump(commitMessages: Iterable<string>): SemverBump {
  const normalized = [...commitMessages].map((message) => message.trim()).filter(Boolean);
  if (normalized.length === 0) {
    return "patch";
  }

  for (const message of normalized) {
    const subject = message.split(/\r?\n/, 1)[0].trim();
    if (message.includes("BREAKING CHANGE:") || BREAKING_SUBJECT_PATTERN.test(subject)) {
      return "major";
    }
  }

  for (const message of normalized) {
    const subject = message.split(/\r?\n/, 1)[0].trim();
    if (FEATURE_SUBJECT_PATTERN.test(subject)) {
      return "minor";
    }
  }

  return "patch";
}

export function computeNextVersion(baseVersion: string, commitMessages: Iterable<string>): string {
  return bumpSemver(baseVersion, classifyBump(commitMessages));
}
