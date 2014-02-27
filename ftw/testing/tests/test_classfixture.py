from StringIO import StringIO
from ftw.testing.fixtures import classfixture
from ftw.testing.utils import capture_streams
from plone.testing import Layer
from unittest2 import TestCase
from zope.testing.testrunner.runner import Runner


def run(test_suite):
    stdout = StringIO()
    stderr = StringIO()
    with capture_streams(stdout, stderr):
        runner = Runner(found_suites=[test_suite])
        result = runner.run()
    return stdout, stderr, result


class ExampleLayer(Layer):

    def __init__(self, *args, **kwargs):
        super(ExampleLayer, self).__init__(*args, **kwargs)
        self['example_layer'] = False

    def setUp(self):
        self['example_layer'] = True

EXAMPLE_FIXTURE = ExampleLayer(name='EXAMPLE_FIXTURE')


class TestClassFixture(TestCase):

    def test_class_setup_is_executed_without_layer(self):
        @classfixture
        class Test(TestCase):
            @classmethod
            def setUpClass(cls):
                cls.setup_executed = True

            def foo(self):
                pass

        run(Test('foo'))
        self.assertEquals(True, getattr(Test, 'setup_executed', None))

    def test_class_teardown_is_executed_without_layer(self):
        @classfixture
        class Test(TestCase):
            @classmethod
            def tearDownClass(cls):
                cls.teardown_executed = True

            def foo(self):
                pass

        run(Test('foo'))
        self.assertEquals(True, getattr(Test, 'teardown_executed', None))

    def test_generated_layer_name_without_layer(self):
        @classfixture
        class Test(TestCase):
            pass

        self.assertEquals(
            '%s.Test:ClassFixtureLayer' % Test.__module__,
            Test.layer.__name__)

    def test_existing_layer_is_still_executed(self):
        @classfixture
        class Test(TestCase):
            layer = EXAMPLE_FIXTURE
            @classmethod
            def setUpClass(cls):
                cls.setup_executed = True

            def foo(self):
                pass

        self.assertFalse(Test.layer['example_layer'])
        run(Test('foo'))
        self.assertTrue(Test.layer['example_layer'],
                        'EXAMPLE_FIXTURE.setUp was not executed')

        run(Test('foo'))
        self.assertEquals(True, getattr(Test, 'setup_executed', None))

    def test_generated_layer_name_starts_with_previous_layer(self):
        """If a test class already has a layer which is wrapped, we want
        the wrapping layer to start with the layer name of the wrapped
        layer so that we do not mess up the layer oder.
        """
        @classfixture
        class Test(TestCase):
            layer = EXAMPLE_FIXTURE

        self.assertEquals(
            'EXAMPLE_FIXTURE:%s.Test:ClassFixtureLayer' % Test.__module__,
            Test.layer.__name__)
