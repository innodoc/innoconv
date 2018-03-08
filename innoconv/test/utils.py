"""Util functions for tests."""

import subprocess
import os
from contextlib import contextmanager
from io import StringIO
import sys
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..', '..')


def get_pandoc_soup(filename, filters=None):
    """Run Pandoc with filters and parse output using BeautifulSoup."""
    tex_source = os.path.join(SCRIPT_DIR, 'files', filename)
    env = os.environ.copy()
    env['PYTHONPATH'] = ROOT_DIR

    command = ['pandoc', '--from=latex+raw_tex', '--to=html5']

    for _filter in filters:
        command.append(
            '--filter=%s' %
            os.path.join(ROOT_DIR, '.panzer', 'filter', _filter))

    command.append(tex_source)

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, cwd=SCRIPT_DIR, env=env)
    html_output = proc.stdout.read()
    proc.communicate()

    return BeautifulSoup(html_output, 'html.parser')


@contextmanager
def captured_output():
    """Used in tests to easily capture stdout/stderr."""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
