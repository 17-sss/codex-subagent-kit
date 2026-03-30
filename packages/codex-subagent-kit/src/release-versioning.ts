const SEMVER_PATTERN = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/;
const RELEASE_LABELS = ["release:major", "release:minor", "release:patch", "release:none"] as const;

export type SemverBump = "major" | "minor" | "patch";
export type ReleaseDecision = SemverBump | "none";

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

export function classifyReleaseLabels(labels: Iterable<string>): ReleaseDecision {
  const normalized = [...labels]
    .map((label) => label.trim())
    .filter(Boolean);
  const recognized = [...new Set(normalized.filter((label): label is (typeof RELEASE_LABELS)[number] =>
    (RELEASE_LABELS as readonly string[]).includes(label),
  ))];

  if (recognized.length === 0) {
    return "none";
  }
  if (recognized.length > 1) {
    throw new Error(`conflicting release labels: ${recognized.join(", ")}`);
  }

  const [label] = recognized;
  if (label === "release:none") {
    return "none";
  }
  if (label === "release:major") {
    return "major";
  }
  if (label === "release:minor") {
    return "minor";
  }
  return "patch";
}

export function computeNextVersionFromLabels(
  baseVersion: string,
  labels: Iterable<string>,
  options?: { initialRelease?: boolean },
): string | null {
  const decision = classifyReleaseLabels(labels);
  if (decision === "none") {
    return null;
  }
  if (options?.initialRelease) {
    return baseVersion;
  }
  return bumpSemver(baseVersion, decision);
}
