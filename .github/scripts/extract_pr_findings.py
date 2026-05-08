#!/usr/bin/env python3
"""Render a PR comment summarising warnings/errors for changed plugins.

Reads `plugins_metadata.json`, extracts the `warnings` and `errors` lists for
each plugin key passed on the command line, renders a markdown body with a
sticky-comment marker, and writes the body plus a `has_findings` flag to
GITHUB_OUTPUT. Exits non-zero when any of the listed plugins has at least one
warning or error so the workflow check goes red.

Stages:
    --stage warnings  Comment only reflects W001-W020 (fetch step).
    --stage install   Comment additionally reflects E001-E004 (test-install).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

COMMENT_MARKER = "<!-- pr-plugin-checks -->"
README_LINK = (
    "https://github.com/aiidateam/aiida-registry"
    "#how-to-fix-registry-warnings-and-errors"
)


def render_message(raw):
    """Convert an HTML-tagged registry message into markdown."""
    pre_block = ""
    pre_match = re.match(r"^(.*?)<pre>(.*?)</pre>(.*)$", raw, re.DOTALL)
    if pre_match:
        raw = pre_match.group(1) + pre_match.group(3)
        pre_block = pre_match.group(2).strip()

    a_match = re.match(
        r"^<a\s+href=['\"]([^'\"]+)['\"]>([WE]\d+)</a>:\s*(.*)$",
        raw,
        re.DOTALL,
    )
    if a_match:
        head = f"`{a_match.group(2)}`: {a_match.group(3).strip()}"
    else:
        head = re.sub(r"<[^>]+>", "", raw).strip()

    if pre_block:
        # Keep error output to a reasonable size in PR comments.
        if len(pre_block) > 2000:
            pre_block = pre_block[:2000] + "\n... (truncated)"
        head += f"\n\n```\n{pre_block}\n```"
    return head


def write_outputs(body, has_findings):
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf8") as fh:
            fh.write(f"has_findings={'true' if has_findings else 'false'}\n")
            fh.write("body<<EOF_BODY\n")
            fh.write(body)
            fh.write("\nEOF_BODY\n")
    print(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("changed", nargs="*")
    parser.add_argument("--json", default="plugins_metadata.json")
    parser.add_argument("--stage", choices=["warnings", "install"], default="warnings")
    args = parser.parse_args()

    if not args.changed:
        body = (
            f"{COMMENT_MARKER}\n## Plugin checks\n\n"
            "No plugin entries changed in this PR."
        )
        write_outputs(body, has_findings=False)
        return 0

    try:
        data = json.loads(Path(args.json).read_text(encoding="utf8"))
    except (OSError, json.JSONDecodeError) as exc:
        body = (
            f"{COMMENT_MARKER}\n## Plugin checks\n\n"
            f"Internal error: could not read `{args.json}` ({exc.__class__.__name__}: {exc}). "
            "The metadata fetch step likely failed; check the workflow logs."
        )
        write_outputs(body, has_findings=True)
        return 1
    plugins = data.get("plugins", {})

    lines = [
        COMMENT_MARKER,
        "## Plugin checks",
        "",
        "Touched plugins: " + ", ".join(f"`{k}`" for k in args.changed),
        "",
    ]

    any_findings = False
    for key in args.changed:
        plugin = plugins.get(key)
        if plugin is None:
            lines.append(f"- ⚠️ `{key}` — not found in metadata after fetch")
            any_findings = True
            continue
        warnings = [render_message(w) for w in (plugin.get("warnings") or [])]
        errors = [render_message(e) for e in (plugin.get("errors") or [])]
        if not warnings and not errors:
            lines.append(f"- ✅ `{key}` — clean")
            continue
        any_findings = True
        lines.append(f"- ❌ `{key}`")
        for w in warnings:
            lines.append(f"   - ⚠️ {w}")
        for e in errors:
            lines.append(f"   - 🛑 {e}")

    lines.append("")
    if args.stage == "warnings":
        lines.append(
            "Install check waits for maintainer approval after warnings pass. "
            f"See [how to fix warnings and errors]({README_LINK})."
        )
    else:
        lines.append(f"See [how to fix warnings and errors]({README_LINK}).")

    body = "\n".join(lines)
    write_outputs(body, has_findings=any_findings)
    return 1 if any_findings else 0


if __name__ == "__main__":
    sys.exit(main())
