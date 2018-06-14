#!/usr/bin/env python3

"""Main entry for the innoconv document converter."""

import argparse

from innoconv.constants import DEFAULT_OUTPUT_DIR_BASE, DEFAULT_LANGUAGES
import innoconv.metadata as metadata
from innoconv.utils import log
from innoconv.runner import InnoconvRunner

INNOCONV_DESCRIPTION = '''
  Convert interactive educational content.

'''

INNOCONV_EPILOG = '''
Copyright (C) 2018 innoCampus, TU Berlin
Authors: {}
Web: {}

This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
'''.format(metadata.__author__, metadata.__url__)


def parse_cli_args():
    """Parse command line arguments."""
    innoconv_argparser = argparse.ArgumentParser(
        description=INNOCONV_DESCRIPTION,
        epilog=INNOCONV_EPILOG,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False)

    innoconv_argparser.add_argument('-h', '--help',
                                    action='help',
                                    help="show this help message and exit")

    innoconv_argparser.add_argument('source',
                                    help="content directory or file")

    languages_help = 'languages to convert (default: "{}")'.format(
        DEFAULT_LANGUAGES)
    innoconv_argparser.add_argument('-l', '--languages', nargs='+',
                                    default=DEFAULT_LANGUAGES,
                                    help=languages_help)

    output_help = 'output base directory (default: "{}")'.format(
        DEFAULT_OUTPUT_DIR_BASE)
    innoconv_argparser.add_argument('-o', '--output-dir-base',
                                    default=DEFAULT_OUTPUT_DIR_BASE,
                                    help=output_help)

    debug_help = 'debug mode'
    innoconv_argparser.add_argument('-d', '--debug',
                                    action='store_true',
                                    default=False,
                                    help=debug_help)

    return vars(innoconv_argparser.parse_args())


def main():
    """innoConv main entry point."""
    args = parse_cli_args()

    runner = InnoconvRunner(
        args['source'], args['output_dir_base'], args['languages'],
        debug=args['debug'])
    runner.run()
    log('Build finished!')


if __name__ == '__main__':
    main()
