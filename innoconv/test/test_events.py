"""Unit tests for innoconv.modules.maketoc"""

# pylint: disable=missing-docstring

import io
import unittest
import unittest.mock

# supress linting until tests are implemented
# pylint: disable=W0611,invalid-name

from innoconv.modules import AbstractModule, ALL_EVENTS
from innoconv.runner import InnoconvRunner

SOURCE = "SOURCE"
TARGET = "TARGET"


class VerboseMod(AbstractModule):
    """a Test Module"""

    def __init__(self):
        super(VerboseMod, self).__init__()
        self.events.extend(ALL_EVENTS)
        self.value = True

    def __getattr__(self, name):
        def _missing(*args, **kwargs):
            # pylint: disable=unused-argument
            print(name)
        return _missing


def walk_side_effect(path):
    lang = path[-2:]
    return iter([
        (
            '/{}/{}'.format(SOURCE, lang),
            ['A'],
            ['content.md'],
        ),
        (
            '/{}/{}'.format(SOURCE, lang),
            ['B'],
            ['content.md'],
        )
    ])


AST = (
    'content_ast',
    {'c': [{'t': 'Str', 'c': 'A'}]}
)


class TestEvents(unittest.TestCase):

    def __init__(self, arg):
        super(TestEvents, self).__init__(arg)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    @unittest.mock.patch('json.dump')
    @unittest.mock.patch('innoconv.runner.to_ast', return_value=AST)
    @unittest.mock.patch('builtins.open')
    @unittest.mock.patch('innoconv.runner.walk', side_effect=walk_side_effect)
    @unittest.mock.patch('innoconv.runner.makedirs')
    @unittest.mock.patch('innoconv.runner.isdir', return_value=True)
    def test_events(self, *args):
        mock_stdout = args[-1]
        mod = VerboseMod()
        runner = InnoconvRunner(source_dir=SOURCE,
                                output_dir_base=TARGET,
                                languages=['de'],
                                modules=[mod])
        runner.run()
        for event in ALL_EVENTS:
            self.assertTrue(event in mock_stdout.getvalue())
