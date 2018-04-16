"""Runner module"""

import os
import subprocess

from innoconv.constants import (PANZER_SUPPORT_DIR, PANZER_TIMEOUT,
                                OUTPUT_FORMAT_EXT_MAP)


class InnoconvRunner():
    """innoConv runner that spawns a panzer instance."""

    def __init__(self, source_dir, output_dir, language_code,
                 ignore_exercises=False, output_format='json', debug=False):
        # pylint: disable=too-many-arguments
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.language_code = language_code
        self.ignore_exercises = ignore_exercises
        self.output_format = output_format
        self.debug = debug

    def run(self):
        """Setup paths and options and run the panzer command.

        :rtype: str
        :returns: output filename
        """
        source_lang_dir = os.path.join(self.source_dir, self.language_code)

        # output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # output filename
        filename = 'index.{}'.format(OUTPUT_FORMAT_EXT_MAP[self.output_format])
        filename_path = os.path.join(self.output_dir, filename)

        # set debug mode
        env = os.environ.copy()
        if self.debug:
            env['INNOCONV_DEBUG'] = '1'
            style = 'innoconv-debug'
        else:
            style = 'innoconv'

        if self.ignore_exercises:
            env['INNOCONV_IGNORE_EXERCISES'] = '1'

        cmd = [
            'panzer',
            '---panzer-support', PANZER_SUPPORT_DIR,
            '--metadata=style:{}'.format(style),
            '--metadata=lang:{}'.format(self.language_code),
            '--from=latex+raw_tex',
            '--to={}'.format(self.output_format),
            '--standalone',
            '--output={}'.format(filename_path),
            'index.tex'
        ]

        proc = subprocess.Popen(
            cmd, cwd=source_lang_dir, stderr=subprocess.STDOUT, env=env)

        return_code = proc.wait(timeout=PANZER_TIMEOUT)
        if return_code != 0:
            raise RuntimeError("Failed to run panzer!")

        return filename_path
