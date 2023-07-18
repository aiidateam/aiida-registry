# -*- coding: utf-8 -*-
""""
Fetch information about plugins and print it in a human-readable format.

Adapted from `aiida.cmdline.commands.cmd_plugin`.

Note: This script should run inside the aiida-core docker container without requiring additional dependencies.
"""
# pylint: disable=missing-class-docstring,import-outside-toplevel
import inspect
import json
from dataclasses import asdict, dataclass
from typing import Dict, List

import click

ENTRY_POINT_GROUPS = [
    "aiida.calculations",
    "aiida.workflows",
]


@dataclass
class ProcessSpecEntry:
    name: str
    required: bool
    valid_types: list
    info: str


@dataclass
class ExitCode:
    status: str
    message: int


@dataclass
class ProcessSpec:
    inputs: List[ProcessSpecEntry]
    outputs: List[ProcessSpecEntry]
    exit_codes: List[ExitCode]


@dataclass
class ProcessInfo:
    description: str
    spec: ProcessSpec


def document_entry_point_group(entry_point_group) -> Dict[str, ProcessInfo]:
    """Extract metadata for each entry point in a group.

    :param entry_point_group: the entry point group
    :return: a dictionary with the entry point name as key and the entry point metadata as value
    """
    from aiida.plugins.entry_point import (  # pylint: disable=import-error
        get_entry_point_names,
    )

    entry_points = get_entry_point_names(entry_point_group)

    if not entry_points:
        return {}

    groups_dict = {}
    for entry_point in entry_points:
        process_info = document_entry_point(entry_point_group, entry_point)
        if process_info is not None:
            groups_dict[entry_point] = asdict(process_info)

    return groups_dict


def document_entry_point(entry_point_group: str, entry_point: str) -> ProcessInfo:
    """Extract metadata for an entry point.

    :param entry_point_group: the entry point group
    :param entry_point: the entry point name
    """
    # pylint: disable=import-outside-toplevel,import-error
    from aiida.common import EntryPointError
    from aiida.engine import Process
    from aiida.plugins.entry_point import load_entry_point

    try:
        plugin = load_entry_point(entry_point_group, entry_point)
    except EntryPointError as exception:
        print(str(exception))
    else:
        if (
            inspect.isclass(plugin) and issubclass(plugin, Process)
        ) or plugin.is_process_function:
            return document_process_info(plugin)
        print(f"Error: {plugin} is not a Process.")

    return None


def document_process_info(process):
    """Print detailed information about a process class and its process specification.

    :param process: a :py:class:`~aiida.engine.processes.process.Process` class
    """
    docstring = process.__doc__

    if docstring is not None:
        docstring = docstring.strip().split("\n")

    if not docstring:
        docstring = ["No description available"]

    return ProcessInfo(
        spec=document_process_spec(process.spec()), description=docstring
    )


def document_process_spec(process_spec):
    """Get the process spec in a human-readable formatted way.

    :param process_spec: a `ProcessSpec` instance
    """

    def build_entries(ports) -> List[ProcessSpecEntry]:
        """Build a list of entries to be printed for a `PortNamespace.

        :param ports: the port namespace
        :return: list of tuples with port name, required, valid types and info strings
        """
        result = []

        for name, port in sorted(
            ports.items(), key=lambda x: (not x[1].required, x[0])
        ):
            if name.startswith("_"):
                continue

            valid_types = (
                port.valid_type
                if isinstance(port.valid_type, (list, tuple))
                else (port.valid_type,)
            )
            valid_types = ", ".join(
                [
                    valid_type.__name__
                    for valid_type in valid_types
                    if valid_type is not None
                ]
            )
            required = port.required
            info = port.help if port.help is not None else ""
            result.append(
                ProcessSpecEntry(
                    name=name, required=required, valid_types=valid_types, info=info
                )
            )

        return result

    inputs = build_entries(process_spec.inputs)
    outputs = build_entries(process_spec.outputs)

    exit_codes = []
    for exit_code in sorted(
        process_spec.exit_codes.values(), key=lambda exit_code: exit_code.status
    ):
        message = exit_code.message
        exit_codes.append(ExitCode(status=exit_code.status, message=message))

    return ProcessSpec(inputs=inputs, outputs=outputs, exit_codes=exit_codes)


@click.command()
@click.option("--output", "-o", type=str, default=None, help="Output file")
def cli(output):
    """Fetch information about plugins and print it in a human-readable format."""
    result = {}
    for ep_group in ENTRY_POINT_GROUPS:
        result[ep_group] = document_entry_point_group(ep_group)

    if output is None:
        print(result)
    else:
        with open(output, "w", encoding="utf8") as handle:
            json.dump(result, handle, indent=4)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
