from ftw.testing.implementer import Implementer
from unittest import TestCase
from zope.interface import Interface, Attribute
from zope.interface import implementer
import inspect


class IExample(Interface):

    foo = Attribute('An attribute.')

    def no_arguments():
        """A function without arguments.
        """

    def arguments(foo):
        """A function with an argument.
        """

    def defaults(foo, bar=True):
        """A function with defaults.
        """

    def magic_arguments(*args, **kwargs):
        """A function with wildcard arguments and
        keyword arguments.
        """

    def combined(foo, bar=True, *args, **kwargs):
        """A function combining some signatures.
        """


@implementer(IExample)
class Example(object):

    def no_arguments(self):
        pass

    def arguments(self, foo):
        pass

    def defaults(self, foo, bar=True):
        pass

    def magic_arguments(self, *args, **kwargs):
        pass

    def combined(self, foo, bar=True, *args, **kwargs):
        pass


class TestImplementer(TestCase):

    def test_implements_interface(self):
        generated = Implementer(IExample)()
        self.assertTrue(IExample.implementedBy(generated))

    def test_attributes(self):
        generated = Implementer(IExample)()
        self.assertTrue(hasattr(generated, 'foo'))

    def test_no_arguments(self):
        generated = Implementer(IExample)()
        self.assertEquals(inspect.getargspec(generated.no_arguments),
                          inspect.getargspec(Example.no_arguments))

        self.assertEquals(IExample.get('no_arguments').__doc__,
                          generated.no_arguments.__doc__)

    def test_arguments(self):
        generated = Implementer(IExample)()
        self.assertEquals(inspect.getargspec(generated.arguments),
                          inspect.getargspec(Example.arguments))

        self.assertEquals(IExample.get('arguments').__doc__,
                          generated.arguments.__doc__)

    def test_defaults(self):
        generated = Implementer(IExample)()
        self.assertEquals(inspect.getargspec(generated.defaults),
                          inspect.getargspec(Example.defaults))

        self.assertEquals(IExample.get('defaults').__doc__,
                          generated.defaults.__doc__)

    def test_magic_arguments(self):
        generated = Implementer(IExample)()
        self.assertEquals(inspect.getargspec(generated.magic_arguments),
                          inspect.getargspec(Example.magic_arguments))

        self.assertEquals(IExample.get('magic_arguments').__doc__,
                          generated.magic_arguments.__doc__)

    def test_combined(self):
        generated = Implementer(IExample)()
        self.assertEquals(inspect.getargspec(generated.combined),
                          inspect.getargspec(Example.combined))

        self.assertEquals(IExample.get('combined').__doc__,
                          generated.combined.__doc__)
