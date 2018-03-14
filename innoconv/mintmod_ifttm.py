#!/usr/bin/env python3

r"""
Pre-processor that removes all \iftm commands.

It works by preserving the HTML part of the \ifttm command. The PDF part it
discarded.
"""

import sys
import re


def main():
    """Main entry point."""
    out = re.sub(r"\\ifttm(.*?)\\else.*?\\fi([%\s\\])", r"\1\2",
                 sys.stdin.read(), flags=re.DOTALL)
    sys.stdout.write(out)
    sys.stdout.flush()


if __name__ == '__main__':
    main()
