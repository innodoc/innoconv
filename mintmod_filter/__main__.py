#!/usr/bin/env python3

"""Pandoc filter main entry."""

from panflute import run_filter
from mintmod_filter.mintmod_filter_action import mintmod_filter_action

def main(doc=None):
    """Executes filter."""
    return run_filter(mintmod_filter_action, doc=doc)

if __name__ == '__main__':
    main()
