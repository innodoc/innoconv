#!/usr/bin/env python3

"""Main entry for the innoconv document converter."""

import argparse
import os
import sys

from innoconv.constants import (
    DEFAULT_OUTPUT_DIR_BASE, DEFAULT_LANGUAGES, DEFAULT_EXTENSIONS)
from innoconv.metadata import __author__, __url__
from innoconv.utils import log
from innoconv.runner import InnoconvRunner
from innoconv.extensions import EXTENSIONS

INNOCONV_DESCRIPTION = """
  Convert interactive educational content.

"""

INNOCONV_EPILOG = """
Copyright (C) 2018 innoCampus, TU Berlin
Authors: {}
Web: {}

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
""".format(__author__, __url__)


def get_args():
    """Get CLI arguments."""
    innoconv_argparser = argparse.ArgumentParser(
        description=INNOCONV_DESCRIPTION,
        epilog=INNOCONV_EPILOG,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False)

    innoconv_argparser.add_argument('-h', '--help',
                                    action='help',
                                    help="show this help message and exit")

    innoconv_argparser.add_argument('-l', '--languages',
                                    default=','.join(DEFAULT_LANGUAGES),
                                    help="Languages to convert")

    innoconv_argparser.add_argument('-o', '--output-dir',
                                    default=DEFAULT_OUTPUT_DIR_BASE,
                                    help="Output directory")

    innoconv_argparser.add_argument('-d', '--debug',
                                    action='store_true',
                                    default=False,
                                    help="Enable debug mode")

    innoconv_argparser.add_argument('source_dir',
                                    help="content directory or file")

    extlist = ["- {} ({})".format(ext, EXTENSIONS[ext].helptext())
               for ext in EXTENSIONS]
    ext_help = "Available extensions:\n{}".format("\n".join(extlist))
    innoconv_argparser.add_argument('-e', '--extensions',
                                    default=','.join(DEFAULT_EXTENSIONS),
                                    help=ext_help)
    return vars(innoconv_argparser.parse_args())


def main(args=None):
    """innoConv main entry point."""
    args = get_args()
    source_dir = os.path.abspath(args['source_dir'])
    output_dir = os.path.abspath(args['output_dir'])
    languages = args['languages'].split(',')
    debug = args['debug']
    extensions = []
    try:
        for ext_name in args['extensions'].split(','):
            try:
                ext = EXTENSIONS[ext_name]()
            except (ImportError, KeyError) as exc:
                raise RuntimeError(
                    "Extension {} not found!".format(ext_name)) from exc
            extensions.append(ext)

        runner = InnoconvRunner(
            source_dir, output_dir, languages, extensions, debug=debug)
        runner.run()
        if debug:
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
