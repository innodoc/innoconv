#!/usr/bin/env python3

"""Main entry for Pandoc filter ``mintmod_filter``."""

import os
from panflute import run_filter
from innoconv.mintmod_filter.filter_action import MintmodFilterAction


def main():
    """Execute filter."""
    debug = True if os.environ.get('INNOCONV_DEBUG') else False
    filter_action = MintmodFilterAction(debug=debug)
    return run_filter(filter_action.filter)


if __name__ == '__main__':
    main()
