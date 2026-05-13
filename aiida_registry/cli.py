# -*- coding: utf-8 -*-
"""CLI for AiiDA registry."""

import click

from aiida_registry.build_metadata import build_metadata
from aiida_registry.test_install import test_install_all


@click.group()
def cli():
    """CLI for AiiDA registry."""


@cli.command()
@click.argument("package", nargs=-1, required=False)
def fetch(package):
    """Fetch data from PyPI and write to JSON file."""
    build_metadata(package)


@cli.command()
@click.option(
    "--container-image",
    # should use aiidateam/aiida-core-with-services:lastest after the version is released
    default="ghcr.io/aiidateam/aiida-core-with-services:latest",
    help="Container image to use for the install",
)
@click.argument("package", nargs=-1, required=False)
def test_install(container_image, package):
    """Test installing plugins in a Docker container.

    If one or more PACKAGE names are given, only those plugins are tested;
    otherwise all plugins are tested.
    """
    test_install_all(container_image, packages=package or None)


if __name__ == "__main__":
    cli()
