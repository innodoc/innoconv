"""Command line interface for the innoConv document converter."""

from asyncio import CancelledError
import logging
import os
import sys

import click
import coloredlogs
import yaml

from innoconv.cli.validators import parse_extensions
from innoconv.constants import (
    DEFAULT_EXTENSIONS,
    DEFAULT_OUTPUT_DIR_BASE,
    EXIT_CODES,
    LOG_FORMAT,
)
from innoconv.ext import EXTENSIONS
from innoconv.manifest import Manifest
from innoconv.metadata import __author__, __description__, __url__, __version__
from innoconv.supervisor import Supervisor


EPILOG = """Available extensions:
{}

Author: {}
Web: {}

Copyright (C) 2018 innoCampus, TU Berlin

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
"""


def _get_epilog():
    max_length = len(max(EXTENSIONS.keys(), key=len))
    fstr = " {{:<{}}} - {{}}".format(max_length)
    extlist = [fstr.format(e, v.helptext()) for e, v in EXTENSIONS.items()]
    return EPILOG.format("\n".join(extlist), __author__, __url__)


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
    "source_dir", type=click.Path(exists=True, file_okay=False, resolve_path=True),
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
    callback=parse_extensions,
)
@click.option(
    "-f", "--force", is_flag=True, help="Force overwriting of output.", default=False,
)
@click.option("-v", "--verbose", is_flag=True, help="Print verbose messages.")
@click.version_option(__version__)
def cli(verbose, force, extensions, output_dir, source_dir):
    """Instantiate and start an InnoconvRunner."""
    log_level = logging.INFO if verbose else logging.WARNING
    coloredlogs.install(level=log_level, fmt=LOG_FORMAT)

    # check output directory
    if os.path.exists(output_dir) and not force:
        raise click.FileError(
            output_dir,
            "Output directory {} already exists. "
            "To overwrite use --force.".format(output_dir),
        )

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

    # start supervisor
    supervisor = Supervisor(source_dir, output_dir, manifest, extensions)
    try:
        supervisor.start()
    except CancelledError:
        sys.exit(EXIT_CODES["RUNNER_CANCELLED"])
    except Exception:
        logging.exception("Exception received from supervisor:")
        sys.exit(EXIT_CODES["RUNNER_ERROR"])
    logging.info("Build finished!")
    sys.exit(EXIT_CODES["SUCCESS"])

    # # start runner
    # try:
    #     runner = InnoconvRunner(source_dir, output_dir, manifest, extensions)
    #     runner.run()
    # except RuntimeError as error:
    #     msg = "Something went wrong: {}".format(error)
    #     logging.critical(msg)
    #     sys.exit(EXIT_CODES["RUNNER_ERROR"])
    # logging.info("Build finished!")
    # sys.exit(EXIT_CODES["SUCCESS"])
