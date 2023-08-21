# -*- coding: utf-8 -*-
"""Fetch metadata from plugins and dump it to temporary JSON file.

Data is primarily sourced from PyPI,
with a fallback to the repository build file (setup.json, setup.cfg, pyproject.toml).
"""
import json

# pylint: disable=consider-using-f-string
import os
import re
import subprocess
import sys
import traceback
import urllib
from collections import OrderedDict
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional

import requests
import yaml

from . import (
    PLUGINS_FILE_ABS,
    PLUGINS_METADATA,
    REPORTER,
    classifier_to_status,
    status_dict,
)
from .parse_build_file import get_data_parser, identify_build_tool
from .parse_pypi import PypiData, get_pypi_metadata
from .utils import fetch_file

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]


@lru_cache(maxsize=None)
def load_plugins_metadata(json_file_path):
    """Load the plugins file."""
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return None


def get_last_fetched_version(plugin_name):
    """
    Get the last fetched version of the plugin.

    Args:
        plugin_name (str): Name of the plugin.

    Returns:
        str or None: Version of the plugin if available, or None if not found.
    """
    json_file_path = "./cloned_plugins_metadata.json"
    metadata = load_plugins_metadata(json_file_path)

    if metadata is not None:
        try:
            return metadata["plugins"][plugin_name]["metadata"]["version"]
        except KeyError:
            print("No version for the plugin")

    return None


def get_hosted_on(url):
    """Get the hosting service from a URL."""
    try:
        requests.get(url, timeout=30)
    except Exception as exc:
        raise ValueError("Unable to open 'code_home' url: '{}'".format(url)) from exc

    netloc = urllib.parse.urlparse(url).netloc

    # Remove port (if any)
    netloc = netloc.partition(":")[0]

    # Remove subdomains (this only works for domain suffixes of length 1!)
    # TODO: fix it for domains like yyy.co.uk  # pylint: disable=fixme
    netloc = ".".join(netloc.split(".")[-2:])

    return netloc


def get_github_commits_count(repo_url):
    """
    Get the commits count on the default branch of the repository.
    """
    owner, repo = repo_url.split("/")[3:5]
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    today = datetime.today().date()
    last_twelve_months = today - timedelta(days=365)

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    params = {
        "since": last_twelve_months.isoformat(),
        "until": today.isoformat(),
        "per_page": 1,
        "page": 1,
    }

    response = requests.get(url, params=params, headers=headers, timeout=60)
    if response.status_code == 200:
        if len(response.json()) == 0:
            commits_count = 0
        else:
            # https://stackoverflow.com/a/70610670/1069467
            link_header = response.headers.get("Link")
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            commits_count = int(match.group(1))
    else:
        commits_count = -1

    return commits_count


def clone_repository(url, repo_name):
    """
    clone the plugin repository.
    """
    if not os.path.exists("installed_plugins"):
        os.makedirs("installed_plugins")
    subprocess.run(["git", "clone", url, f"installed_plugins/{repo_name}"], check=False)


def get_git_commits_count(repo_name):
    """
    get the number of commits in the last year.
    """
    last_twelve_months = datetime.now() - timedelta(days=365)
    git_command = [
        "git",
        "rev-list",
        "--count",
        f'--since="{last_twelve_months}"',
        "--all",
    ]
    commits_count = (
        subprocess.check_output(git_command, cwd=f"./installed_plugins/{repo_name}")
        .decode()
        .strip()
    )
    return int(commits_count)


def complete_plugin_data(
    plugin_data: dict, fetch_pypi=True, fetch_pypi_wheel=True
):  # pylint: disable=too-many-branches,too-many-statements
    """Update plugin data dictionary.

     * add metadata, aiida_version and entrypoints from plugin_info
     * add package_name if missing
     * add hosted_on
     & more
    used for rendering.
    """
    if "package_name" not in list(plugin_data.keys()):
        plugin_data["package_name"] = plugin_data["name"].replace("-", "_")

    REPORTER.info(f'{plugin_data["package_name"]}')

    plugin_data["hosted_on"] = get_hosted_on(plugin_data["code_home"])

    if plugin_data["hosted_on"] == "github.com" and GITHUB_TOKEN:
        commits_count = get_github_commits_count(plugin_data["code_home"])
    else:
        try:
            clone_repository(plugin_data["code_home"], plugin_data["name"])
            commits_count = get_git_commits_count(plugin_data["name"])
        except Exception as exc:  # pylint: disable=broad-except
            commits_count = -1
            print("Failed to clone the plugin repository:", str(exc))

    plugin_data.update(
        {
            "metadata": {},
            "aiida_version": None,
            "entry_points": None,
            "commits_count": commits_count,
        }
    )

    # First try to get metadata from PyPI
    pypi_metadata: Optional[PypiData] = None
    if fetch_pypi and is_pip_url_pypi(plugin_data.get("pip_url", "")):
        pypi_metadata = get_pypi_metadata(plugin_data["pip_url"], fetch_pypi_wheel)
    if pypi_metadata:
        plugin_data["metadata"] = pypi_metadata.metadata
        plugin_data["aiida_version"] = pypi_metadata.aiida_version
        plugin_data["entry_points"] = pypi_metadata.entry_points

    # Now get missing data from the source repository
    if pypi_metadata is None or pypi_metadata.entry_points is None:
        plugin_info_url = plugin_data.pop("plugin_info", None)
        if plugin_info_url is None:
            REPORTER.warn(
                "Cannot fetch all data from PyPI and missing plugin_info key!"
            )
        else:
            # retrieve content of build file
            plugin_info_content = fetch_file(plugin_info_url)

            if plugin_info_content:
                # Identify build system
                build_tool_name = identify_build_tool(
                    plugin_info_url,
                    plugin_info_content,
                )
                if pypi_metadata is not None:
                    # we only need to get the entry points
                    data = get_data_parser(build_tool_name)(
                        plugin_info_content, ep_only=True
                    )  # , entry_points_only=True
                    plugin_data["entry_points"] = data.entry_points
                else:
                    data = get_data_parser(build_tool_name)(
                        plugin_info_content, ep_only=False
                    )
                    plugin_data["metadata"] = data.metadata
                    plugin_data["aiida_version"] = data.aiida_version
                    plugin_data["entry_points"] = data.entry_points

    current_version = get_last_fetched_version(plugin_data["name"])
    if current_version:
        try:
            if current_version != plugin_data["metadata"]["version"]:
                plugin_data["metadata"]["release_date"] = datetime.today().strftime(
                    "%Y-%m-%d"
                )
        except KeyError:
            print("no version for the plugin")

    # ensure entry points are not None
    plugin_data["entry_points"] = plugin_data.get("entry_points") or {}

    # run validations

    if plugin_data["name"] == "aiida-core" and plugin_data["metadata"].get("version"):
        plugin_data["aiida_version"] = f'=={plugin_data["metadata"]["version"]}'
    if plugin_data.get("aiida_version") is None:
        REPORTER.warn("AiiDA version not found")

    validate_dev_status(plugin_data)

    if "documentation_url" in plugin_data:
        validate_doc_url(plugin_data["documentation_url"])

    validate_plugin_entry_points(plugin_data)

    return plugin_data


def validate_dev_status(plugin_data: dict):
    """Validate the development_status key, potentially sourcing from classifiers."""
    classifiers = (
        plugin_data["metadata"].get("classifiers", [])
        if plugin_data.get("metadata", None)
        else []
    )
    if plugin_data["metadata"] and "Framework :: AiiDA" not in classifiers:
        REPORTER.warn("Missing classifier 'Framework :: AiiDA'")

    # Read development status from plugin repo
    development_status = None
    for classifier in classifiers:
        if classifier in classifier_to_status:
            if development_status is not None:
                REPORTER.warn("Multiple development statuses found in classifiers")
            development_status = classifier_to_status[classifier]

    if (
        development_status
        and "development_status" in plugin_data
        and (development_status != plugin_data["development_status"])
    ):
        REPORTER.warn(
            f"Development status in classifiers ({development_status}) "
            f"does not match development_status in metadata ({plugin_data['development_status']})"
        )

    # prioritise development_status from plugins.yaml
    if "development_status" in plugin_data:
        REPORTER.warn(
            "`development_status` key is deprecated. "
            "Use PyPI Trove classifiers in the plugin repository instead."
        )
    else:
        plugin_data["development_status"] = development_status or "planning"

    # note: for more validation, it might be sensible to switch to voluptuous
    if plugin_data["development_status"] not in status_dict:
        REPORTER.warn(
            "Invalid development status '{}'".format(plugin_data["development_status"])
        )


def validate_doc_url(url):
    """Validate that documentation URL provides valid HTTP response."""
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()  # raise an exception for all 4xx/5xx errors
    except Exception:  # pylint: disable=broad-except
        REPORTER.warn("Unable to reach documentation URL: {}".format(url))
        REPORTER.debug(traceback.print_exc(file=sys.stdout))


def validate_plugin_entry_points(plugin_data):
    """Validate that all entry points registered by the plugin start with the registered entry point root."""
    if plugin_data["name"] == "aiida-core":
        return

    if "entry_point_prefix" in plugin_data:
        entry_point_root = plugin_data["entry_point_prefix"]
        if (
            not "aiida_" + plugin_data["entry_point_prefix"].lower()
            == plugin_data["package_name"].lower()
        ):
            REPORTER.warn(
                f"Prefix '{plugin_data['entry_point_prefix']}' does not follow naming convention."
            )
    else:
        # plugin should not specify any entry points
        entry_point_root = "MISSING"

    for ept_group, ept_list in (plugin_data["entry_points"] or {}).items():
        # we only restrict aiida's entry point groups
        if not ept_group.startswith("aiida."):
            continue

        for ept_string in ept_list:
            if not isinstance(ept_list, dict):
                ept_string, _path = ept_string.split("=")
                ept_string = ept_string.strip()
            if not ept_string.startswith(entry_point_root):
                REPORTER.warn(
                    f"Entry point '{ept_string}' does not start with prefix '{entry_point_root}.'"
                )


PYPI_NAME_RE = re.compile(r"^[a-zA-Z0-9-_]+$")


def is_pip_url_pypi(string: str) -> bool:
    """Check if the `pip_url` points to a PyPI package."""
    # for example git+https://... is not a PyPI package
    return PYPI_NAME_RE.match(string) is not None


def fetch_metadata(filter_list=None, fetch_pypi=True, fetch_pypi_wheel=True):
    """Fetch metadata from PyPI and AiiDA-Plugins."""
    with open(PLUGINS_FILE_ABS, encoding="utf8") as handle:
        plugins_raw_data: dict = yaml.safe_load(handle)

    plugins_metadata = OrderedDict()

    for plugin_name, plugin_data in sorted(plugins_raw_data.items()):
        if filter_list and plugin_name not in filter_list:
            continue
        REPORTER.set_plugin_name(plugin_name)
        plugin_data["name"] = plugin_name
        plugins_metadata[plugin_name] = complete_plugin_data(
            plugin_data, fetch_pypi=fetch_pypi, fetch_pypi_wheel=fetch_pypi_wheel
        )

    REPORTER.info(f"{PLUGINS_METADATA} dumped")

    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("::set-output name=error::" + "%0A".join(REPORTER.warnings))

    return plugins_metadata
