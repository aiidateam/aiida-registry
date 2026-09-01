#!/usr/bin/env python3
"""Detect plugins added or modified in this PR vs the base branch.

Reads the proposed entries from the working-tree `plugins.yaml`, which the
workflow has replaced with the one the PR would merge, and the baseline from
`REGISTRY_BASE_REF`, the base that merge sits on, so both sides come from the
same merge. Both are set by `.github/actions/fetch-pr-plugins-yaml`, and the
working-tree file is the one `aiida-registry` itself reads, so every job in
the workflow judges one copy of the proposed entries.

Prints the list of plugin keys that were added or whose entry differs, and
writes the same list plus a count to GITHUB_OUTPUT for downstream jobs to
consume.

Plugin keys must match a conservative allow-list — anything else is dropped
with a warning so we don't pass adversarial strings into shell commands later.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

PLUGINS_FILE = Path(__file__).resolve().parents[2] / "plugins.yaml"
# Outside the workflow there is no merge ref, so compare against the remote.
BASE_REF = os.environ.get("REGISTRY_BASE_REF") or "origin/master"
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


def load_yaml_file(path):
    return yaml.safe_load(path.read_text(encoding="utf8")) or {}


def main():
    base = load_yaml_at(BASE_REF)
    head = load_yaml_file(PLUGINS_FILE)

    if not base:
        # Carrying on would call every registered plugin changed and send all
        # of them through the install check.
        print(
            f"::error::No baseline entries at {BASE_REF}. If this is the "
            "workflow, the merge ref was not fetched deep enough to reach it."
        )
        return 1

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
