"""Runner module"""

import os
import subprocess

from innoconv.constants import (PANZER_SUPPORT_DIR, PANZER_TIMEOUT,
                                DEFAULT_OUTPUT_FORMAT, OUTPUT_FORMAT_EXT_MAP,
                                DEFAULT_INPUT_FORMAT)


class InnoconvRunner():
    """innoConv runner that spawns a panzer instance."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, source, output_dir_base, language_code,
                 ignore_exercises=False, remove_exercises=False,
                 split_sections=False, input_format=DEFAULT_INPUT_FORMAT,
                 output_format=DEFAULT_OUTPUT_FORMAT, debug=False):
        # pylint: disable=too-many-arguments
        self.source = source
        self.output_dir_base = output_dir_base
        self.language_code = language_code
        self.ignore_exercises = ignore_exercises
        self.remove_exercises = remove_exercises
        self.split_sections = split_sections
        self.input_format = input_format
        self.output_format = output_format
        self.debug = debug

    def run(self):
        """Setup paths and options and run the panzer command.

        :rtype: str
        :returns: output filename
        """

        if os.path.isdir(self.source):
            source_dir = os.path.join(self.source, self.language_code)
            filename = 'index.{}'.format(
                OUTPUT_FORMAT_EXT_MAP[self.output_format])
            source_file = 'index.tex'
            output_dir = os.path.join(self.output_dir_base, self.language_code)
        elif os.path.isfile(self.source):
            source_dir = os.path.dirname(os.path.abspath(self.source))
            filename = '{}.{}'.format(
                os.path.splitext(self.source)[0],
                OUTPUT_FORMAT_EXT_MAP[self.output_format])
            source_file = self.source
            output_dir = self.output_dir_base

        # create output directory
        os.makedirs(output_dir, exist_ok=True)

        # output filename
        filename_path = os.path.join(output_dir, filename)

        # set debug mode
        env = os.environ.copy()
        if self.debug and self.split_sections:
            env['INNOCONV_DEBUG'] = '1'
            style = 'innoconv-debug-split'
        elif self.debug:
            env['INNOCONV_DEBUG'] = '1'
            style = 'innoconv-debug'
        elif self.split_sections:
            style = 'innoconv-split'
        else:
            style = 'innoconv'

        if self.ignore_exercises:
            env['INNOCONV_IGNORE_EXERCISES'] = '1'

        if self.remove_exercises:
            env['INNOCONV_REMOVE_EXERCISES'] = '1'

        cmd = [
            'panzer',
            '---panzer-support', PANZER_SUPPORT_DIR,
            '--metadata=style:{}'.format(style),
            '--metadata=lang:{}'.format(self.language_code),
            '--from={}'.format(self.input_format),
            '--to={}'.format(self.output_format),
            '--standalone',
            '--output={}'.format(filename_path),
            source_file,
        ]

        proc = subprocess.Popen(
            cmd, cwd=source_dir, stderr=subprocess.STDOUT, env=env)

        return_code = proc.wait(timeout=PANZER_TIMEOUT)
        if return_code != 0:
            raise RuntimeError("Failed to run panzer!")

        return filename_path
