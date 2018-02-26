#!/usr/bin/env python3

"""Main entry for Pandoc filter ``mintmod_filter``."""

from panflute import run_filter
from innoconv.mintmod_filter.filter_action import MintmodFilterAction


def main():
    """Execute filter."""
    filter_action = MintmodFilterAction()
    return run_filter(filter_action.filter)


if __name__ == '__main__':
    main()
