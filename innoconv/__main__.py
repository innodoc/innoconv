#!/usr/bin/env python3

"""Main entry for the innoconv document converter."""

import argparse
import os
from panflute import debug

from innoconv.utils import get_panzer_bin
from innoconv.constants import (DEFAULT_OUTPUT_DIR_BASE, DEFAULT_OUTPUT_FORMAT,
                                OUTPUT_FORMAT_CHOICES, DEFAULT_LANGUAGE_CODE,
                                LANGUAGE_CODES)
import innoconv.metadata as metadata
from innoconv.runner import InnoconvRunner

PANZER_BIN = get_panzer_bin()

INNOCONV_DESCRIPTION = '''
  Convert mintmod LaTeX content.

  Using panzer executable: "{}"
'''.format(PANZER_BIN)

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
    innoconv_argparser.add_argument('source_dir',
                                    help="content directory")

    output_help = 'output base directory (default: "{}")'.format(
        DEFAULT_OUTPUT_DIR_BASE)
    innoconv_argparser.add_argument('-o', '--output-dir-base',
                                    default=DEFAULT_OUTPUT_DIR_BASE,
                                    help=output_help)

    output_format_help = 'output format'
    innoconv_argparser.add_argument('-t', '--to',
                                    dest='output_format',
                                    choices=OUTPUT_FORMAT_CHOICES,
                                    default=DEFAULT_OUTPUT_FORMAT,
                                    help=output_format_help)

    language_help = 'two-letter language code (default: {})'.format(
        DEFAULT_LANGUAGE_CODE)
    innoconv_argparser.add_argument('-l', '--language-code',
                                    choices=LANGUAGE_CODES,
                                    default=DEFAULT_LANGUAGE_CODE,
                                    help=language_help)

    debug_help = 'debug mode (output HTML and highlight unknown commands)'
    innoconv_argparser.add_argument('-d', '--debug',
                                    action='store_true',
                                    help=debug_help)

    return vars(innoconv_argparser.parse_args())


def main():
    """innoConv main entry point."""
    args = parse_cli_args()

    if args['debug'] and args['output_format'] != 'html5':
        debug("Warning: Setting output format to 'html5' in debug mode.")
        args['output_format'] = 'html5'

    output_dir = os.path.join(args['output_dir_base'], args['language_code'])

    runner = InnoconvRunner(
        args['source_dir'], output_dir, args['language_code'],
        output_format=args['output_format'], debug=args['debug'])
    filename_out = runner.run()
    debug('Build finished: {}'.format(filename_out))


if __name__ == '__main__':
    main()
