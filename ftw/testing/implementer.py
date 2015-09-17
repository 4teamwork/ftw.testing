from zope.interface import Attribute
from zope.interface import classImplements
from zope.interface.interface import Method


class Implementer(object):
    """The implementer creates a class implementing an interface dynamically.
    """

    def __init__(self, interface):
        self.interface = interface

    def __call__(self):
        impl = self._generate_class()
        self._add_attributes(impl)
        self._generate_methods(impl)
        classImplements(impl, self.interface)
        return impl

    def _generate_class(self):
        class Implementation(object):
            pass

        Implementation.__name__ = 'Implementation: %s' % (
            self.interface.__name__)
        return Implementation

    def _add_attributes(self, impl):
        for name in self.interface.names():
            obj = self.interface.get(name)
            if isinstance(obj, Attribute):
                setattr(impl, name, None)

    def _generate_methods(self, impl):
        for name in self.interface.names():
            obj = self.interface.get(name)
            if isinstance(obj, Method):
                setattr(impl, name, self._generate_function(obj))

    def _generate_function(self, interface_function):
        signature = interface_function.getSignatureString()
        if signature == '()':
            signature = 'self'
        else:
            signature = 'self, %s' % signature[1:-1]

        function_str = 'lambda %s: None' % signature
        fun = eval(function_str)
        fun.__name__ = interface_function.getName()
        fun.__doc__ = interface_function.getDoc()

        return fun
