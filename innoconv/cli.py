"""Command line interface for the innoConv document converter."""

import logging
import os
import sys

import click
import coloredlogs
import yaml

from innoconv.constants import (
    DEFAULT_EXTENSIONS,
    DEFAULT_OUTPUT_DIR_BASE,
    EXIT_CODES,
    LOG_FORMAT,
)
from innoconv.ext import EXTENSIONS
from innoconv.manifest import Manifest
from innoconv.metadata import __author__, __description__, __url__, __version__
from innoconv.runner import InnoconvRunner


def _get_epilog():
    max_length = len(max(EXTENSIONS.keys(), key=len))
    extlist = [f" {e:<{max_length}} - {v.helptext()}" for e, v in EXTENSIONS.items()]
    extlist = "\n".join(extlist)
    return f"""Available extensions:
{extlist}

Author: {__author__}
Web: {__url__}

Copyright (C) 2018 innoCampus, TU Berlin

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
"""


def _parse_extensions(_, __, value):
    extensions = value.split(",")
    for ext in extensions:
        if ext not in EXTENSIONS.keys():
            raise click.BadOptionUsage("-e", f"Extension not found: {ext}")
    return extensions


class CustomEpilogCommand(click.Command):
    """Format epilog in a custom way."""

    def format_epilog(self, _, formatter):
        """Format epilog while preserving newlines."""
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split("\n"):
                formatter.write_text(line)


@click.command(cls=CustomEpilogCommand, help=__description__, epilog=_get_epilog())
@click.argument(
    "source_dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.option(
    "-o",
    "--output-dir",
    help="Set output directory.",
    type=click.Path(writable=True, resolve_path=True),
    default=DEFAULT_OUTPUT_DIR_BASE,
    show_default=True,
)
@click.option(
    "-e",
    "--extensions",
    help="Enable extensions (comma-separated).",
    default=",".join(DEFAULT_EXTENSIONS),
    show_default=True,
    metavar="EXTS",
    callback=_parse_extensions,
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force overwriting of output.",
    default=False,
)
@click.option("-v", "--verbose", is_flag=True, help="Print verbose messages.")
@click.version_option(__version__)
def cli(verbose, force, extensions, output_dir, source_dir):
    """Instantiate and start an InnoconvRunner."""
    log_level = logging.INFO if verbose else logging.WARNING
    coloredlogs.install(level=log_level, fmt=LOG_FORMAT)

    # check output directory
    if os.path.exists(output_dir) and not force:
        msg = f"Output directory {output_dir} already exists. To overwrite use --force."
        raise click.FileError(output_dir, msg)

    # read course manifest
    try:
        manifest = Manifest.from_directory(source_dir)
    except yaml.YAMLError:
        logging.critical("Could not parse manifest file!")
        sys.exit(EXIT_CODES["MANIFEST_ERROR"])
    except FileNotFoundError:
        logging.critical("Could not find manifest file in source directory!")
        sys.exit(EXIT_CODES["MANIFEST_ERROR"])
    except RuntimeError as exc:
        logging.critical(exc)
        sys.exit(EXIT_CODES["MANIFEST_ERROR"])

    # start runner
    try:
        runner = InnoconvRunner(source_dir, output_dir, manifest, extensions)
        runner.run()
    except RuntimeError as error:
        logging.critical("Something went wrong: %s", error)
        sys.exit(EXIT_CODES["RUNNER_ERROR"])
    logging.info("Build finished!")
    sys.exit(EXIT_CODES["SUCCESS"])
