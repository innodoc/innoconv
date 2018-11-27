#!/usr/bin/env python3

"""Main entry for the innoconv document converter."""

import argparse
import os
import sys

from innoconv.constants import (
    DEFAULT_OUTPUT_DIR_BASE, DEFAULT_EXTENSIONS, MANIFEST_BASENAME)
from innoconv.extensions import EXTENSIONS
from innoconv.manifest import Manifest
from innoconv.metadata import __author__, __url__
from innoconv.runner import InnoconvRunner
from innoconv.utils import log, set_debug

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
    def _format_default(val):
        return " (default: {})".format(val)

    extlist = ["  {} - {}".format(ext, EXTENSIONS[ext].helptext())
               for ext in EXTENSIONS]
    ext_help = "available extensions:\n{}".format("\n".join(extlist))

    innoconv_argparser = argparse.ArgumentParser(
        description=INNOCONV_DESCRIPTION,
        epilog=INNOCONV_EPILOG.format(ext_help, __author__, __url__),
        formatter_class=argparse.RawTextHelpFormatter)

    output_dir_help = "Output directory{}".format(
        _format_default(DEFAULT_OUTPUT_DIR_BASE))
    innoconv_argparser.add_argument('-o', '--output-dir',
                                    default=DEFAULT_OUTPUT_DIR_BASE,
                                    help=output_dir_help)

    debug_help = "Enable debug mode{}".format(_format_default(False))
    innoconv_argparser.add_argument('-d', '--debug',
                                    action='store_true',
                                    default=False,
                                    help=debug_help)

    extensions_help = "Enabled extensions{}".format(
        _format_default(','.join(DEFAULT_EXTENSIONS)))
    innoconv_argparser.add_argument('-e', '--extensions',
                                    default=','.join(DEFAULT_EXTENSIONS),
                                    help=extensions_help)

    innoconv_argparser.add_argument('source_dir',
                                    help="Content source directory")

    return innoconv_argparser


def main(args=None):
    """innoConv main entry point."""
    args = vars(get_arg_parser().parse_args())
    source_dir = os.path.abspath(args['source_dir'])
    output_dir = os.path.abspath(args['output_dir'])
    extensions = args['extensions'].split(',')
    set_debug(args['debug'])

    # read course manifest
    filename = '{}.yml'.format(MANIFEST_BASENAME)
    filepath = os.path.join(source_dir, filename)
    try:
        with open(filepath, 'r') as file:
            manifest = Manifest.from_yaml(file.read())
    except FileNotFoundError as exc:
        log(exc)
        return -2

    try:
        # conversion
        runner = InnoconvRunner(source_dir, output_dir, manifest, extensions)
        runner.run()
        log("Build finished!")
        return 0
    except RuntimeError as error:
        log("Something went wrong: {}".format(error))
        return 1


def init():
    """Module init function."""
    if __name__ == '__main__':
        sys.exit(main())


init()
