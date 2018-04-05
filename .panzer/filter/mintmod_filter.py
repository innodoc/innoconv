#!/usr/bin/env python3

"""Main entry for Pandoc filter ``mintmod_filter``."""

import os
from panflute import run_filter
from innoconv.mintmod_filter.filter_action import MintmodFilterAction
from innoconv.utils import remove_empty_paragraphs


def main():
    """Execute filter and remove empty paragraphs."""
    debug = True if os.environ.get('INNOCONV_DEBUG') else False
    filter_action = MintmodFilterAction(debug=debug)
    run_filter(filter_action.filter, finalize=remove_empty_paragraphs)


if __name__ == '__main__':
    main()
