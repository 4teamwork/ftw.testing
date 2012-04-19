from lettuce import Runner, Feature, fs
from unittest2 import TestCase, TestSuite
import os.path
import sys


def feature_suite(*paths):
    """Generate a feature suite.
    """
    frame = sys._getframe(1)
    module_path = os.path.dirname(frame.f_globals.get('__file__'))

    suite = TestSuite()

    for path in paths:
        load_feature_directory(suite, os.path.join(module_path, path))

    return suite


def load_feature_directory(suite, path):
    loader = fs.FeatureLoader(path)
    loader.find_and_load_step_definitions()

    filepaths = loader.find_feature_files()
    for filepath in filepaths:
        case = FeatureTestCase(filepath)
        suite.addTest(case)


class FeatureTestCase(TestCase):

    def __init__(self, filepath, **options):
        TestCase.__init__(self)
        self.filepath = filepath
        self.options = options

    def id(self):
        return os.path.basename(self.filepath)

    def runTest(self):
        print 'XXX', Runner(self.filepath, **self.options).run()
