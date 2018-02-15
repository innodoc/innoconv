#!/usr/bin/env python3

"""Pandoc filter main entry."""

from panflute import run_filter
from mintmod_filter.filter_action import filter_action


def main(doc=None):
    """Execute filter."""
    return run_filter(filter_action, doc=doc)


if __name__ == '__main__':
    main()
