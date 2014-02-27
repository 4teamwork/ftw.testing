from plone.testing import Layer


class ClassFixtureLayer(Layer):

    def __init__(self, test_class, bases=None, name=None, module=None):
        super(ClassFixtureLayer, self).__init__(bases=bases, name=name,
                                                module=module)
        self.test_class = test_class

    def setUp(self):
        self.test_class.setUpClass()

    def tearDown(self):
        self.test_class.tearDownClass()


def classfixture(test_class):
    """Adds support for the unittest2 `setUpClass` and `tearDownClass'
    functions, which are not supported by the zope testrunner.

    See http://docs.python.org/2/library/unittest.html#setupclass-and-teardownclass

    Support is added by creating a testing layer which calls the methods.
    The setUpClass / tearDownClass methods are called by the testing layer.

    Example usage:

    @classfixture
    class Test(unittest2.TestCase):
        @classmethod
        def setUpClass(cls):
            cls._connection = createExpensiveConnectionObject()

        @classmethod
        def tearDownClass(cls):
            cls._connection.destroy()
    """

    dottedname = '.'.join((test_class.__module__, test_class.__name__))

    if getattr(test_class, 'layer', None) is None:
        bases = ()
        name = dottedname
    else:
        bases = (test_class.layer,)
        name = ':'.join((test_class.layer.__name__, dottedname))

    layer = ClassFixtureLayer(test_class, bases=bases,
                              name='%s:ClassFixtureLayer' % name)
    test_class.layer = layer

    return test_class
