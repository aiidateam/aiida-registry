# -*- coding: utf-8 -*-
"""Utility functions."""
import os
import traceback

import requests
import requests_cache

from . import REPORTER

if os.environ.get("CACHE_REQUESTS"):
    # Set environment variable CACHE_REQUESTS to cache requests for 1 day for faster testing
    # e.g.: export CACHE_REQUESTS=1
    requests_cache.install_cache("demo_cache", expire_after=60 * 60 * 24)


def fetch_file(file_url: str, file_type: str = "plugin info", warn=True) -> str:
    """Fetch plugin info from a URL to a file."""
    try:
        response = requests.get(file_url, timeout=60)
        # raise an exception for all 4xx/5xx errors
        response.raise_for_status()
    except Exception:  # pylint: disable=broad-except
        if warn:
            REPORTER.error(
                f"Unable to retrieve {file_type} from: {file_url}."
                "Please check the URL of your plugin in the registry yaml."
            )
            REPORTER.debug(traceback.format_exc())
        return None
    return response.content.decode(response.encoding or "utf8")


def add_registry_checks(metadata):
    """Add fetch warnings/errors to the data object."""
    for name, error_list in REPORTER.plugins_errors.items():
        if "errors" not in metadata[name]:
            metadata[name]["errors"] = []
        metadata[name]["errors"] += error_list

    for name, warning_list in REPORTER.plugins_warnings.items():
        if "warnings" not in metadata[name]:
            metadata[name]["warnings"] = []
        metadata[name]["warnings"] += warning_list

    return metadata
