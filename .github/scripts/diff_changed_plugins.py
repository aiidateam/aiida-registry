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


def as_plugin_mapping(text, source):
    """Return the plugin mapping in `text`, or None after reporting why not."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        print(f"::error::{source} is not valid YAML: {exc}")
        return None
    if not data:
        print(f"::error::{source} lists no plugins at all.")
        return None
    if not isinstance(data, dict):
        print(
            f"::error::{source} is a {type(data).__name__} at its top level. It "
            "must map each plugin name to that plugin's entry."
        )
        return None
    return data


def read_baseline(ref):
    """Return the plugin mapping at `ref`, or None after reporting why not."""
    proc = subprocess.run(
        ["git", "show", f"{ref}:plugins.yaml"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(f"::error::Could not read plugins.yaml at {ref}: {proc.stderr.strip()}")
        return None
    return as_plugin_mapping(proc.stdout, f"The baseline plugins.yaml at {ref}")


def read_proposed(path):
    """Return the plugin mapping at `path`, or None after reporting why not."""
    return as_plugin_mapping(
        path.read_text(encoding="utf8"), "The proposed plugins.yaml"
    )


def main():
    if os.environ.get("GITHUB_ACTIONS") and not os.environ.get("REGISTRY_BASE_REF"):
        # Without it BASE_REF falls back to the checked-out base branch, and the
        # comparison below reports no changes whatever the PR proposes.
        print(
            "::error::REGISTRY_BASE_REF is unset. The job must run "
            "./.github/actions/fetch-pr-plugins-yaml before this script."
        )
        return 1

    # An unusable baseline would make every registered plugin look changed and
    # send all of them through the install check.
    base = read_baseline(BASE_REF)
    head = read_proposed(PLUGINS_FILE)
    if base is None or head is None:
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
