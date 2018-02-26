"""Util functions for tests."""

import subprocess
import os
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
            os.path.join(ROOT_DIR, 'innoconv', _filter, '__main__.py'))

    command.append(tex_source)

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, cwd=SCRIPT_DIR, env=env)
    html_output = proc.stdout.read()
    proc.communicate()

    return BeautifulSoup(html_output, 'html.parser')
