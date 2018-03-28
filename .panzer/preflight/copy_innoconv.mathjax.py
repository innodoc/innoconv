#!/usr/bin/env python3
"""
Copy innoconv.mathjax.js to build directory.
"""

import os
import shutil
import sys
sys.path.append(os.path.join(os.environ['PANZER_SHARED'], 'python'))
try:
    import panzertools  # pylint: disable=import-error
except Exception:
    raise


def main():
    """main function"""
    options = panzertools.read_options()
    output = options['pandoc']['output']
    if output != '-':
        src_file = os.path.join(
            os.environ['PANZER_SHARED'], 'javascript', 'innoconv.mathjax.js')
        build_path = os.path.dirname(output)
        shutil.copy(src_file, build_path)


if __name__ == '__main__':
    main()
