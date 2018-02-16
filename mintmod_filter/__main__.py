#!/usr/bin/env python3

"""Pandoc filter main entry."""

from panflute import run_filter
from mintmod_filter.filter_action import FilterAction


def main(doc=None):
    """Execute filter."""
    filter_action = FilterAction()
    return run_filter(filter_action.filter, doc=doc)


if __name__ == '__main__':
    main()
