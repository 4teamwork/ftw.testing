from ftw.testing.layer import TEMP_DIRECTORY
from unittest2 import TestCase



class TestTempDirectoryLayer(TestCase):
    layer = TEMP_DIRECTORY

    def test_temp_directory_is_writeable(self):
        file_path = self.layer['temp_directory'].joinpath('file.txt')
        file_path.write_text('something')
        self.assertEqual('something', file_path.text())

        dir_path = self.layer['temp_directory'].joinpath('directory')
        dir_path.mkdir()
        self.assertTrue(dir_path.isdir(), 'Directory was not created.')

    def test_directory_is_cleaned_up_after_every_test(self):
        dir_path = self.layer['temp_directory'].joinpath('the-directory')
        file_path = dir_path.joinpath('the-file.txt')
        self.assertFalse(dir_path.exists(), 'Directory was not cleaned up after test.')
        self.assertFalse(file_path.exists(), 'File was not cleaned up after test.')

        dir_path.mkdir()
        file_path.write_text('something')

    # This makes sure that the test is run twice, so that it would fail when
    # the directory wouldn't be cleaned up properly.
    test_directory_is_cleaned_up_after_every_test2 = \
        test_directory_is_cleaned_up_after_every_test
