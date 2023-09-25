# -*- coding: utf-8 -*-
"""CLI for AiiDA registry."""
import click

from aiida_registry.make_pages import make_pages
from aiida_registry.test_install import test_install_all


@click.group()
def cli():
    """CLI for AiiDA registry."""


@cli.command()
@click.argument("package", nargs=-1, required=False)
def fetch(package):
    """Fetch data from PyPI and write to JSON file."""
    make_pages(package)


@cli.command()
@click.option(
    "--container-image",
    # should use aiidateam/aiida-core-with-services:lastest after the version is released
    # default="aiidateam/aiida-core-with-services:edge",
    default="aiidateam/aiida-core:latest",
    help="Container image to use for the install",
)
def test_install(container_image):
    """Test installing all plugins in a Docker container."""
    test_install_all(container_image)


if __name__ == "__main__":
    cli()
