# -*- coding: utf-8 -*-
"""Tests of `.github/scripts/diff_changed_plugins.py`.

The script is what `PR plugin checks` uses to decide which plugin entries a
pull request proposes, and so which ones get fetched and test-installed. It
runs under `pull_request_target`, where GitHub takes the workflow from the base
branch, so a pull request cannot exercise its own copy of it; these tests stand
in for that.

They drive the real script against a real git repository laid out like the
registry, because the two sides it compares come from two different places: the
baseline from a git ref, the proposed entries from the working-tree file that
`.github/actions/fetch-pr-plugins-yaml` overwrites.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCRIPT_REL = Path(".github") / "scripts" / "diff_changed_plugins.py"
SCRIPT = Path(__file__).parents[1] / SCRIPT_REL

BASE_ENTRIES = {
    "aiida-core": {"name": "aiida-core", "state": "stable"},
    "aiida-quantumespresso": {"name": "aiida-quantumespresso", "state": "stable"},
}


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def annotated(proc, message):
    """Whether the run emitted `message` as a GitHub Actions error annotation."""
    return any(
        line.startswith(f"::error::{message}") for line in proc.stdout.splitlines()
    )


@pytest.fixture
def registry_repo(tmp_path):
    """A git repo shaped like the registry, with `BASE_ENTRIES` committed."""
    repo = tmp_path / "registry"
    (repo / SCRIPT_REL.parent).mkdir(parents=True)
    shutil.copy(SCRIPT, repo / SCRIPT_REL)
    git(repo, "init", "-q", "-b", "master")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / "plugins.yaml").write_text(yaml.safe_dump(BASE_ENTRIES), encoding="utf8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "Base entries")
    return repo


@pytest.fixture
def run_script(registry_repo, tmp_path):
    """Run the script over a proposed `plugins.yaml`, as the workflow does.

    Returns the completed process and the parsed `GITHUB_OUTPUT` contents. An
    `env` value of None unsets the variable, so a case can drop the
    `REGISTRY_BASE_REF` the workflow would normally have provided.
    """

    def run(proposed, env=None):
        (registry_repo / "plugins.yaml").write_text(proposed, encoding="utf8")
        github_output = tmp_path / "github_output"
        github_output.touch()

        # Spelled out, so the result does not depend on whether the suite itself
        # happens to be running inside GitHub Actions.
        environ = dict(os.environ)
        environ["GITHUB_OUTPUT"] = str(github_output)
        environ["REGISTRY_BASE_REF"] = "HEAD"
        environ.pop("GITHUB_ACTIONS", None)
        for key, value in (env or {}).items():
            if value is None:
                environ.pop(key, None)
            else:
                environ[key] = value

        proc = subprocess.run(
            [sys.executable, str(SCRIPT_REL)],
            cwd=registry_repo,
            capture_output=True,
            text=True,
            env=environ,
        )
        outputs = dict(
            line.split("=", 1)
            for line in github_output.read_text(encoding="utf8").splitlines()
        )
        return proc, outputs

    return run


@pytest.mark.parametrize(
    "proposed, changed",
    [
        pytest.param(BASE_ENTRIES, "", id="untouched"),
        pytest.param(
            {**BASE_ENTRIES, "aiida-new": {"name": "aiida-new"}},
            "aiida-new",
            id="added",
        ),
        pytest.param(
            {**BASE_ENTRIES, "aiida-core": {"name": "aiida-core", "state": "beta"}},
            "aiida-core",
            id="modified",
        ),
        pytest.param(
            {"aiida-core": BASE_ENTRIES["aiida-core"]},
            "",
            id="removals-are-not-reported",
        ),
        pytest.param(
            {**BASE_ENTRIES, "aiida-bad;rm -rf /": {"name": "nope"}},
            "",
            id="keys-outside-the-allow-list-are-dropped",
        ),
        pytest.param(
            {
                **BASE_ENTRIES,
                "aiida-b": {"name": "aiida-b"},
                "aiida-a": {"name": "aiida-a"},
            },
            "aiida-a aiida-b",
            id="reported-alphabetically-whatever-the-file-order",
        ),
    ],
)
def test_changed_plugins(run_script, proposed, changed):
    """Only entries the PR adds or alters reach the fetch and install steps."""
    # `sort_keys=False` keeps the file in the order the case declares, the way a
    # hand-edited plugins.yaml arrives.
    proc, outputs = run_script(yaml.safe_dump(proposed, sort_keys=False))

    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert outputs == {"changed": changed, "changed_count": str(len(changed.split()))}


@pytest.mark.parametrize(
    "proposed, env, error",
    [
        pytest.param(
            "- aiida-core\n",
            {},
            "The proposed plugins.yaml is a list at its top level.",
            id="head-is-not-a-mapping",
        ),
        pytest.param(
            "",
            {},
            "The proposed plugins.yaml lists no plugins at all.",
            id="head-is-empty",
        ),
        pytest.param(
            "aiida-core:\n  name: aiida-core\n   state: stable\n",
            {},
            "The proposed plugins.yaml is not valid YAML: ",
            id="head-is-not-valid-yaml",
        ),
        pytest.param(
            yaml.safe_dump(BASE_ENTRIES),
            {"REGISTRY_BASE_REF": "refs/heads/no-such-branch"},
            "Could not read plugins.yaml at refs/heads/no-such-branch: ",
            id="baseline-ref-unreadable",
        ),
        pytest.param(
            yaml.safe_dump(BASE_ENTRIES),
            {"GITHUB_ACTIONS": "true", "REGISTRY_BASE_REF": None},
            "REGISTRY_BASE_REF is unset. The job must run",
            id="fetch-pr-plugins-yaml-was-not-run",
        ),
    ],
)
def test_refuses_to_guess(run_script, proposed, env, error):
    """Anything it cannot compare fails the check.

    Reporting zero would wave `warnings-check` and `install-check` past a pull
    request nobody has looked at, since both key off `changed_count`.
    """
    proc, outputs = run_script(proposed, env)

    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert annotated(proc, error), proc.stdout
    assert outputs == {}


def test_empty_baseline_is_told_apart_from_an_unreadable_one(registry_repo, run_script):
    """A baseline that reads fine and holds nothing gets its own message.

    `yaml.safe_load` returns None for an empty file, the same value
    `read_baseline` uses to mean it could not read the ref at all, so the two
    have to stay distinguishable or one of them exits without saying why.
    """
    (registry_repo / "plugins.yaml").write_text("", encoding="utf8")
    git(registry_repo, "commit", "-qam", "Empty the registry")

    proc, outputs = run_script(yaml.safe_dump(BASE_ENTRIES))

    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert annotated(proc, "The baseline plugins.yaml at HEAD lists no plugins at all.")
    assert outputs == {}
