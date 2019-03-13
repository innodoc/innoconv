#!/usr/bin/env python3
"""Main entry for the innoconv document converter."""

import argparse
import logging
import os
import sys

from innoconv.constants import (
    DEFAULT_OUTPUT_DIR_BASE, DEFAULT_EXTENSIONS, MANIFEST_BASENAME, LOG_FORMAT)
from innoconv.extensions import EXTENSIONS
from innoconv.manifest import Manifest
from innoconv.metadata import __author__, __url__
from innoconv.runner import InnoconvRunner

INNOCONV_DESCRIPTION = """
  Convert interactive educational content.

"""

INNOCONV_EPILOG = """
{}

Copyright (C) 2018 innoCampus, TU Berlin
Authors: {}
Web: {}

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
"""


def get_arg_parser():
    """Get CLI arguments."""
    def _format_default(msg, val):
        return "{} (default: {})".format(msg, val)

    extlist = ["  {} - {}".format(ext, EXTENSIONS[ext].helptext())
               for ext in EXTENSIONS]
    ext_help = "available extensions:\n{}".format("\n".join(extlist))

    innoconv_argparser = argparse.ArgumentParser(
        description=INNOCONV_DESCRIPTION,
        epilog=INNOCONV_EPILOG.format(ext_help, __author__, __url__),
        formatter_class=argparse.RawTextHelpFormatter)

    output_dir_help = _format_default(
        "Output directory", DEFAULT_OUTPUT_DIR_BASE)
    innoconv_argparser.add_argument('-o', '--output-dir',
                                    default=DEFAULT_OUTPUT_DIR_BASE,
                                    help=output_dir_help)

    verbose_default = False
    verbose_help = _format_default("Print verbose messages", verbose_default)
    innoconv_argparser.add_argument('-v', '--verbose',
                                    action='store_true',
                                    default=verbose_default,
                                    help=verbose_help)

    extensions_default = ','.join(DEFAULT_EXTENSIONS)
    extensions_help = _format_default("Enabled extensions", extensions_default)
    innoconv_argparser.add_argument('-e', '--extensions',
                                    default=extensions_default,
                                    help=extensions_help)

    innoconv_argparser.add_argument('source_dir',
                                    help="Content source directory")

    return innoconv_argparser


def main(args=None):
    """Read options and start the innoConv runner."""
    args = vars(get_arg_parser().parse_args())
    source_dir = os.path.abspath(args['source_dir'])
    output_dir = os.path.abspath(args['output_dir'])
    extensions = args['extensions'].split(',')
    log_level = logging.INFO if args['verbose'] else logging.WARNING
    logging.basicConfig(level=log_level, format=LOG_FORMAT)

    # read course manifest
    def _read_manifest_data(file_ext):
        filename = '{}.{}'.format(MANIFEST_BASENAME, file_ext)
        filepath = os.path.join(source_dir, filename)
        with open(filepath, 'r') as file:
            return file.read()
    try:
        manifest_data = _read_manifest_data('yml')
    except FileNotFoundError:
        try:
            manifest_data = _read_manifest_data('yaml')
        except FileNotFoundError:
            logging.critical("Could not find manifest.yml!")
            return -2
    try:
        manifest = Manifest.from_yaml(manifest_data)
    except RuntimeError as exc:
        logging.critical(exc)
        return -3

    try:
        runner = InnoconvRunner(source_dir, output_dir, manifest, extensions)
        runner.run()
    except RuntimeError as error:
        msg = "Something went wrong: {}".format(error)
        logging.critical(msg)
        return 1
    logging.info("Build finished!")
    return 0


def init():
    """Run main function and return exit code."""
    if __name__ == '__main__':
        sys.exit(main())


init()
