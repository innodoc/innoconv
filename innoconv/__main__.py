#!/usr/bin/env python3

"""Main entry for the innoconv document converter."""

import argparse
from panflute import debug

from innoconv.utils import get_panzer_bin
from innoconv.constants import (DEFAULT_OUTPUT_DIR_BASE, DEFAULT_OUTPUT_FORMAT,
                                OUTPUT_FORMAT_CHOICES, DEFAULT_INPUT_FORMAT,
                                INPUT_FORMAT_CHOICES, DEFAULT_LANGUAGE_CODE,
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
    innoconv_argparser.add_argument('source',
                                    help="content directory or file")

    output_help = 'output base directory (default: "{}")'.format(
        DEFAULT_OUTPUT_DIR_BASE)
    innoconv_argparser.add_argument('-o', '--output-dir-base',
                                    default=DEFAULT_OUTPUT_DIR_BASE,
                                    help=output_help)

    input_format_help = 'input format'
    innoconv_argparser.add_argument('-f', '--from',
                                    dest='input_format',
                                    choices=INPUT_FORMAT_CHOICES,
                                    default=DEFAULT_INPUT_FORMAT,
                                    help=input_format_help)

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

    ign_exercises_help = "don't show logs for unknown exercise commands/envs"
    innoconv_argparser.add_argument('-i', '--ignore-exercises',
                                    action='store_true',
                                    help=ign_exercises_help)

    rem_exercises_help = "remove all exercise commands/envs"
    innoconv_argparser.add_argument('-r', '--remove-exercises',
                                    action='store_true',
                                    help=rem_exercises_help)

    split_sections_help = "split sections"
    innoconv_argparser.add_argument('-s', '--split-sections',
                                    action='store_true',
                                    help=split_sections_help)

    return vars(innoconv_argparser.parse_args())


def main():
    """innoConv main entry point."""
    args = parse_cli_args()

    if args['remove_exercises'] and not args['ignore_exercises']:
        debug(
            "Warning: Setting --remove-exercises implies --ignore-exercises.")
        args['ignore_exercises'] = True

    if args['split_sections'] and args['output_format'] != 'json':
        debug("Warning: Setting output format to 'json' when splitting.")
        args['output_format'] = 'json'

    runner = InnoconvRunner(
        args['source'], args['output_dir_base'], args['language_code'],
        ignore_exercises=args['ignore_exercises'],
        remove_exercises=args['remove_exercises'],
        split_sections=args['split_sections'],
        input_format=args['input_format'],
        output_format=args['output_format'],
        debug=args['debug'])
    filename_out = runner.run()
    debug('Build finished: {}'.format(filename_out))


if __name__ == '__main__':
    main()
