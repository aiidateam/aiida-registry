#!/usr/bin/env python3
"""Detect plugins added or modified in this PR vs the base branch.

Reads `plugins.yaml` at `origin/master` and at `HEAD`, prints the list of
plugin keys that were added or whose entry differs, and writes the same list
plus a count to GITHUB_OUTPUT for downstream jobs to consume.

Plugin keys must match a conservative allow-list — anything else is dropped
with a warning so we don't pass adversarial strings into shell commands later.
"""

import os
import re
import subprocess
import sys

import yaml

SAFE_KEY = re.compile(r"^[A-Za-z0-9._-]+$")


def load_yaml_at(ref):
    proc = subprocess.run(
        ["git", "show", f"{ref}:plugins.yaml"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        # plugins.yaml may not exist at the base ref (brand-new repo etc.).
        print(f"::warning::Could not read plugins.yaml at {ref}: {proc.stderr.strip()}")
        return {}
    return yaml.safe_load(proc.stdout) or {}


def main():
    base = load_yaml_at("origin/master")
    head = load_yaml_at("HEAD")

    unsafe = sorted(k for k in head if not SAFE_KEY.match(str(k)))
    if unsafe:
        print(f"::warning::Skipping plugin keys with unsafe characters: {unsafe}")

    changed = sorted(
        key
        for key, value in head.items()
        if SAFE_KEY.match(str(key)) and (key not in base or base[key] != value)
    )

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf8") as fh:
            fh.write(f"changed={' '.join(changed)}\n")
            fh.write(f"changed_count={len(changed)}\n")

    print(f"Changed plugins ({len(changed)}): {' '.join(changed) or '(none)'}")


if __name__ == "__main__":
    sys.exit(main() or 0)
