# -*- coding: utf-8 -*-
"""Generate HTML pages for plugin registry.

Reads plugin-metadata.json produced by fetch_metadata.
"""
# pylint: disable=missing-function-docstring,invalid-name,global-statement,consider-using-f-string

import copy
import json
import os
import string
from collections import defaultdict

from aiida_registry.fetch_metadata import fetch_metadata

from . import (
    OTHERCOLORCLASS,
    PLUGINS_METADATA,
    entrypoint_metainfo,
    entrypointtypes,
    main_entrypoints,
    status_dict,
    status_no_pip_url_allowed,
)

# Subfolders
OUT_FOLDER = "out"
STATIC_FOLDER = "static"
HTML_FOLDER = (
    "plugins"  # Name for subfolder where HTMLs for plugins are going to be sitting
)
TEMPLATES_FOLDER = "templates"

# Absolute paths
pwd = os.path.split(os.path.abspath(__file__))[0]
STATIC_FOLDER_ABS = os.path.join(pwd, STATIC_FOLDER)

entrypoints_count = defaultdict(list)
other_entrypoint_names = set()


def get_html_plugin_fname(plugin_name):
    valid_characters = set(string.ascii_letters + string.digits + "_-")

    simple_string = "".join(c for c in plugin_name if c in valid_characters)

    return "{}.html".format(simple_string)


def get_summary_info(entry_points):
    """Get info for plugin detail page.

    Note: this updates the global variables entrypoints_count and other_entrypoint_names.
    """
    summary_info = []
    ep = (entry_points or {}).copy()

    # Collect "main" entry points first
    for entrypoint_name in main_entrypoints:
        try:
            num = len(ep.pop(entrypoint_name))
            if num > 0:
                summary_info.append(
                    {
                        "colorclass": entrypoint_metainfo[entrypoint_name][
                            "colorclass"
                        ],
                        "text": entrypoint_metainfo[entrypoint_name]["shortname"],
                        "count": num,
                    }
                )
                entrypoints_count[entrypoint_name].append(num)
        except KeyError:
            # No specific entrypoints, pass
            pass

    # Check remaining non-empty entrypoints
    remaining = [ep_name for ep_name in ep if ep[ep_name]]
    remaining_count = [len(ep[ep_name]) for ep_name in ep if ep[ep_name]]
    total_count = sum(remaining_count)
    if total_count:
        other_elements = []
        for ep_name in remaining:
            try:
                other_elements.append(entrypoint_metainfo[ep_name]["shortname"])
            except KeyError:
                for strip_prefix in ["aiida."]:
                    if ep_name.startswith(strip_prefix):
                        ep_name = ep_name[len(strip_prefix) :]
                        break
                other_elements.append(
                    ep_name.replace("_", " ").replace(".", " ").capitalize()
                )

        summary_info.append(
            {
                "colorclass": OTHERCOLORCLASS,
                "text": "Other ({})".format(format_entry_points_list(other_elements)),
                "count": total_count,
            }
        )
        entrypoints_count["other"].append(total_count)
        other_entrypoint_names.update(other_elements)

    return summary_info


def format_entry_points_list(ep_list):
    """Return string of entry points, respecting some limit."""
    max_len = 3
    tmp = sorted(copy.copy(ep_list))
    if len(tmp) > max_len:
        tmp = tmp[:max_len] + ["..."]

    return ", ".join(tmp)


def global_summary():
    """Compute summary of plugin registry."""
    summary = []
    for entrypoint_name in main_entrypoints:
        summary.append(
            {
                "name": entrypoint_metainfo[entrypoint_name]["shortname"],
                "colorclass": entrypoint_metainfo[entrypoint_name]["colorclass"],
                "num_entries": len(entrypoints_count[entrypoint_name]),
                "total_num": sum(entrypoints_count[entrypoint_name]),
            }
        )

    summary.append(
        {
            "name": "Other",
            "tooltip": format_entry_points_list(other_entrypoint_names),
            "colorclass": OTHERCOLORCLASS,
            "num_entries": len(entrypoints_count["other"]),
            "total_num": sum(entrypoints_count["other"]),
        }
    )

    return summary


def get_pip_install_cmd(plugin_data):
    if (
        "pip_url" not in plugin_data
        and plugin_data["development_status"] in status_no_pip_url_allowed
    ):
        return "See source code repository."

    pip_url = plugin_data["pip_url"]

    if pip_url.startswith("http") or pip_url.startswith("git"):
        return "pip install {}".format(pip_url)

    # else, we assume it's a PyPI package and we would like to add the version
    try:
        version = plugin_data["metadata"]["version"]
        pre_releases = ["a", "b", "rc"]
        if any(version.find(p_id) != -1 for p_id in pre_releases):
            return "pip install --pre {}".format(pip_url)
        return "pip install {}".format(pip_url)
    except (KeyError, TypeError):
        return "pip install {}".format(pip_url)


def make_pages():
    """
    Add additional information to the JSON data like plugins summary,
    global summary, pip install command, and static data.
    """
    plugins_metadata = fetch_metadata()

    for plugin_name, plugin_data in plugins_metadata.items():
        print("  - {}".format(plugin_name))

        plugin_data["summaryinfo"] = get_summary_info(plugin_data["entry_points"])
        plugin_data["pip_install_cmd"] = get_pip_install_cmd(plugin_data)

    all_data = {}
    all_data["plugins"] = plugins_metadata
    all_data["globalsummary"] = global_summary()
    all_data["status_dict"] = status_dict
    all_data[
        "entrypointtypes"
    ] = entrypointtypes  # add a static entrypointtypes dictionary

    with open(PLUGINS_METADATA, "w", encoding="utf8") as handle:
        json.dump(all_data, handle, indent=2)
