#!/usr/bin/env python3

"""Pandoc filter main entry."""

from panflute import run_filter
from mintmod_filter import mintmod_filter

def main(doc=None):
    """Executes filter."""
    return run_filter(mintmod_filter, doc=doc)

if __name__ == '__main__':
    main()
