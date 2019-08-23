from ftw.testing.layer import ConsoleScriptLayer
from unittest import TestCase


CONSOLE_SCRIPT_TESTING = ConsoleScriptLayer('ftw.testing')


class TestConsoleScriptLayer(TestCase):
    layer = CONSOLE_SCRIPT_TESTING

    def test_buildout_script_is_generated(self):
        self.assertTrue(self.layer['root_path'].joinpath('bin', 'buildout').isfile(),
                        'bin/buildout script was not generated.')

    def test_buildout_config_is_generated(self):
        self.assertTrue(self.layer['root_path'].joinpath('buildout.cfg').isfile(),
                        'buildout.cfg script was not generated.')

    def test_buildout_directory_is_isolated_for_each_test(self):
        path = self.layer['root_path'].joinpath('the-file.txt')
        self.assertFalse(path.exists(), 'Additionally created files in buildout'
                         ' directory are not removed on test tear down.')
        path.write_text('something')

    test_buildout_directory_is_isolated_for_each_test2 = \
        test_buildout_directory_is_isolated_for_each_test

    def test_python_script_with_environment_is_generated(self):
        code = "from ftw.testing import layer; print(layer.__name__)"
        exitcode, output = self.layer['execute_script']('py -c "{0}"'.format(code))
        self.assertEqual('ftw.testing.layer', output.splitlines()[0])
