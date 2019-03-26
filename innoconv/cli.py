"""Command line interface for the innoConv document converter."""

import logging
import os
import sys

import click
import yaml

from innoconv.constants import (
    DEFAULT_EXTENSIONS,
    DEFAULT_OUTPUT_DIR_BASE,
    LOG_FORMAT,
)
from innoconv.extensions import EXTENSIONS
from innoconv.manifest import Manifest
from innoconv.metadata import __author__, __description__, __url__, __version__
from innoconv.runner import InnoconvRunner


def _get_epilog():
    max_length = len(max(EXTENSIONS.keys(), key=len))
    fstr = " {{:<{}}} - {{}}".format(max_length)
    extlist = [fstr.format(e, v.helptext()) for e, v in EXTENSIONS.items()]
    return """Available extensions:
{}

Author: {}
Web: {}

Copyright (C) 2018 innoCampus, TU Berlin

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
""".format(
        "\n".join(extlist), __author__, __url__
    )


def _parse_extensions(_, __, value):
    extensions = value.split(",")
    for ext in extensions:
        if ext not in EXTENSIONS.keys():
            raise click.BadParameter("Extension not found: {}".format(ext))
    return extensions


class CustomEpilogCommand(click.Command):
    """Format epilog in a custom way."""

    def format_epilog(self, _, formatter):
        """Format epilog while preserving newlines."""
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split("\n"):
                formatter.write_text(line)


@click.command(
    cls=CustomEpilogCommand, help=__description__, epilog=_get_epilog()
)
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
    logging.basicConfig(level=log_level, format=LOG_FORMAT)

    # check output directory
    if os.path.exists(output_dir) and not force:
        raise click.BadParameter(
            "Output directory {} already exists. "
            "To overwrite use --force.".format(output_dir)
        )

    # read course manifest
    try:
        manifest = Manifest.from_directory(source_dir)
    except yaml.YAMLError:
        logging.critical("Could not parse manifest file!")
        sys.exit(-3)
    except FileNotFoundError:
        logging.critical("Could not find manifest file in source directory!")
        sys.exit(-3)
    except RuntimeError as exc:
        logging.critical(exc)
        sys.exit(-3)

    # start runner
    try:
        runner = InnoconvRunner(source_dir, output_dir, manifest, extensions)
        runner.run()
    except RuntimeError as error:
        msg = "Something went wrong: {}".format(error)
        logging.critical(msg)
        sys.exit(-4)
    logging.info("Build finished!")
    sys.exit(0)
