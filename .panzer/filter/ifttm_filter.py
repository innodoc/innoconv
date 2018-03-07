#!/usr/bin/env python3

"""Main entry for Pandoc filter ``ifttm_filter``."""

from panflute import run_filter
from innoconv.ifttm_filter.filter_action import IfttmFilterAction


def main():
    """Execute filter."""
    filter_action = IfttmFilterAction()
    return run_filter(filter_action.filter)


if __name__ == '__main__':
    main()
