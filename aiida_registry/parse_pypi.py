# -*- coding: utf-8 -*-
"""Parse metadata from PyPI."""
# pylint: disable=too-many-ancestors,too-many-locals,too-many-branches
import configparser
import json
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Optional

import requests
from poetry.core.version.requirements import Requirement

from . import REPORTER
from .utils import fetch_file


class PypiData(NamedTuple):
    """Data from PyPI."""

    metadata: dict
    aiida_version: Optional[str] = None
    entry_points: Optional[dict] = None


class CaseSensitiveConfigParser(configparser.ConfigParser):
    """Case sensitive config parser."""

    optionxform = staticmethod(str)


def get_pypi_metadata(package_name: str, parse_wheel=True) -> Optional[PypiData]:
    """Get metadata from PyPI."""
    metadata = {}
    aiida_version = None
    entry_points = None

    pypi_info = fetch_file(f"https://pypi.org/pypi/{package_name}/json")
    if pypi_info is None:
        return None

    pypi_data = json.loads(pypi_info)

    # get data from pypi JSON
    pypi_info_data = pypi_data.get("info", {})

    # Get the recent release date and convert it to YYYY-MM-DD format.
    version = pypi_info_data["version"]
    latest_version_release_date = pypi_data["releases"][version][0]["upload_time"]
    release_date_format = "%Y-%m-%dT%H:%M:%S"
    desired_date_format = "%Y-%m-%d"
    original_date = datetime.strptime(latest_version_release_date, release_date_format)
    desired_date_string = original_date.strftime(desired_date_format)
    metadata["release_date"] = desired_date_string
    # add required metadata
    for key_from, key_to in (
        ("summary", "description"),
        ("author", "author"),
        ("author_email", "author_email"),
        ("license", "license"),
        ("home_page", "home_page"),
        ("classifiers", "classifiers"),
        ("version", "version"),
    ):
        if pypi_info_data.get(key_from):
            metadata[key_to] = pypi_info_data[key_from]

    # find aiida-version
    # note if a bdist_wheel is not available,
    # then requires_dist will likely not be available
    if pypi_info_data.get("requires_dist"):
        for req in pypi_info_data["requires_dist"]:
            try:
                parsed = Requirement(req)
            except Exception:  # pylint: disable=broad-except
                continue
            if parsed.name in ["aiida-core", "aiida_core", "aiida"]:
                aiida_version = str(parsed.constraint)

    build_types = {}
    for data in pypi_data.get("urls"):
        if data.get("packagetype"):
            build_types[data.get("packagetype")] = data.get("url")
    if "bdist_wheel" not in build_types:
        REPORTER.warn(
            "<a href='https://github.com/aiidateam/aiida-registry#W019'>W019</a>: "
            "No <code>bdist_wheel</code> available for PyPI release."
        )

    # We cannot read 'entry_points' from PyPI JSON so must download the wheel file
    if not build_types.get("bdist_wheel") or not parse_wheel:
        return PypiData(metadata, aiida_version=aiida_version)

    try:
        with requests.get(
            build_types["bdist_wheel"], stream=True, timeout=120
        ) as download:
            download.raise_for_status()
            with tempfile.TemporaryDirectory() as tmpdirname:
                with Path(tmpdirname, "wheel.whl").open("wb") as handle:
                    for chunk in download.iter_content(chunk_size=8192):
                        handle.write(chunk)
                with zipfile.ZipFile(Path(tmpdirname, "wheel.whl")) as whl:
                    # see https://packaging.python.org/en/latest/specifications/entry-points/#file-format
                    entry_points_content = None
                    for name in whl.namelist():
                        if name.endswith(".dist-info/entry_points.txt"):
                            entry_points_content = whl.read(name).decode("utf-8")
                    if entry_points_content is None:
                        raise IOError("No entry_points.txt found in wheel")
                    parser = CaseSensitiveConfigParser()
                    parser.read_string(entry_points_content)
                    entry_points = {}
                    for key, value in parser.items():
                        if key == "DEFAULT":
                            continue
                        entry_points[key] = dict(value.items())

    except Exception as err:  # pylint: disable=broad-except
        REPORTER.warn(
            "<a href='https://github.com/aiidateam/aiida-registry#W020'>W020</a>: "
            "Unable to read wheel file from PyPI release: "
            f"<pre>{err}</pre>"
        )

    return PypiData(metadata, aiida_version=aiida_version, entry_points=entry_points)
