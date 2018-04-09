"""Util functions for tests."""

import subprocess
import os
from contextlib import contextmanager
from io import StringIO
from json.decoder import JSONDecodeError
import sys
import panflute as pf

from innoconv.constants import PANZER_SUPPORT_DIR, ENCODING
from innoconv.utils import log

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..', '..')


def get_doc_from_markup(markup):
    """Run panzer on markup and return Doc."""

    cmd = [
        'panzer',
        '---panzer-support', PANZER_SUPPORT_DIR,
        '--metadata=style:innoconv-debug',
        '--metadata=lang:de',
        '--from=latex+raw_tex',
        '--to=json',
        '--standalone',
    ]

    env = os.environ.copy()
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    proc.stdin.write(markup.encode(ENCODING))
    try:
        outs, errs = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    errout = errs.decode(ENCODING).strip()
    if errout:
        pf.debug(errout)

    if proc.returncode != 0:
        raise RuntimeError("Failed to run panzer!")

    json_raw = outs.decode(ENCODING)
    try:
        return pf.load(StringIO(json_raw))
    except JSONDecodeError:
        log("Couldn't decode JSON: {}".format(json_raw))


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
