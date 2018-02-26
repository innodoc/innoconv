#!/usr/bin/env python3

"""Pandoc filter main entry."""

from panflute import run_filter
from innoconv.mintmod_filter.filter_action import FilterAction


def main():
    """Execute filter."""
    filter_action = FilterAction()
    return run_filter(filter_action.filter)


if __name__ == '__main__':
    main()
