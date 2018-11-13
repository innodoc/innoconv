#!/usr/bin/env python3

"""Main entry for the innoconv document converter."""

import argparse
import os
import sys

from innoconv.constants import DEFAULT_OUTPUT_DIR_BASE, DEFAULT_LANGUAGES
from innoconv.metadata import __author__, __url__
from innoconv.utils import log
from innoconv.runner import InnoconvRunner
from innoconv.extensions import EXTENSIONS

INNOCONV_DESCRIPTION = '''
  Convert interactive educational content.

'''

INNOCONV_EPILOG = '''
Copyright (C) 2018 innoCampus, TU Berlin
Authors: {}
Web: {}

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
'''.format(__author__, __url__)


def get_arg_parser():
    """Get argument parser."""
    innoconv_argparser = argparse.ArgumentParser(
        description=INNOCONV_DESCRIPTION,
        epilog=INNOCONV_EPILOG,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False)

    innoconv_argparser.add_argument('-h', '--help',
                                    action='help',
                                    help="show this help message and exit")

    argparse_default_languages = ','.join(DEFAULT_LANGUAGES)
    innoconv_argparser.add_argument('-l', '--languages',
                                    default=argparse_default_languages,
                                    help='Languages to convert')

    innoconv_argparser.add_argument('-o', '--output-dir-base',
                                    default=DEFAULT_OUTPUT_DIR_BASE,
                                    help='Output base directory')

    innoconv_argparser.add_argument('-d', '--debug',
                                    action='store_true',
                                    default=False,
                                    help='Enable debug mode')

    innoconv_argparser.add_argument('source_dir',
                                    help="content directory or file")

    extlist = ["- {} ({})".format(ext, EXTENSIONS[ext].helptext())
               for ext in EXTENSIONS]
    ext_help = "Available extensions:\n{}".format("\n".join(extlist))
    innoconv_argparser.add_argument('-e', '--extensions',
                                    action='append',
                                    default=[],
                                    help=ext_help)
    return innoconv_argparser


def main(args=None):
    """innoConv main entry point."""

    if not args:
        args = sys.argv[1:]
    args = vars(get_arg_parser().parse_args())

    source_dir = os.path.abspath(args['source_dir'])
    output_dir_base = os.path.abspath(args['output_dir_base'])
    languages = args['languages'].split(',')
    debug = args['debug']

    extensions = []

    try:
        for ext_name in args['extensions']:
            try:
                ext = EXTENSIONS[ext_name]()
            except (ImportError, KeyError) as exc:
                raise RuntimeError(
                    "Extension {} not found!".format(ext_name)) from exc
            extensions.append(ext)

        runner = InnoconvRunner(
            source_dir, output_dir_base, languages, extensions, debug=debug)
        runner.run()
        if debug:
            log('Build finished!')
        return 0
    except RuntimeError as error:
        log('Something went wrong: {}'.format(error))
        return 1


def init():
    """Module init function."""
    if __name__ == '__main__':
        sys.exit(main())


init()
