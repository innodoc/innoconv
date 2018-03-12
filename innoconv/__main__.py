#!/usr/bin/env python3

"""Main entry for the innoconv document converter."""

import argparse
from panflute import debug

from innoconv.utils import get_panzer_bin
from innoconv.constants import (DEFAULT_OUTPUT_DIR, DEFAULT_LANGUAGE_CODE,
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

    output_help = 'output directory (default: "%s")' % DEFAULT_OUTPUT_DIR
    innoconv_argparser.add_argument('-o', '--output-dir',
                                    default=DEFAULT_OUTPUT_DIR,
                                    help=output_help)

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
    output_format = 'html5' if args['debug'] else 'json'

    runner = InnoconvRunner(
        args['source_dir'], args['output_dir'], args['language_code'],
        output_format=output_format, debug=args['debug'])
    filename_out = runner.run()
    debug('Build finished: {}'.format(filename_out))


if __name__ == '__main__':
    main()
