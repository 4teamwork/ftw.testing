from Acquisition import aq_inner, aq_parent
from ftw.testing.implementer import Implementer
from mocker import expect, ANY
from plone import mocktestcase
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import classImplements
from zope.interface import directlyProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import unittest2


class MockTestCase(mocktestcase.MockTestCase, unittest2.TestCase):
    """Advanced mock test case.
    """

    def setUp(self):
        super(mocktestcase.MockTestCase, self).setUp()
        self._MockTestCase_setup = True
        self._getToolByName_replacements = None

    def tearDown(self):
        self._check_super_setup()
        super(mocktestcase.MockTestCase, self).tearDown()
        self._getToolByName_replacements = None

    def _check_super_setup(self):
        # We need subclassing tests to execute our setUp
        if getattr(self, '_MockTestCase_setup', None) is None:
            raise RuntimeError('%s.setUp does not call superclass setUp().' % (
                    self.__class__.__name__))

    def providing_mock(self, interfaces, *args, **kwargs):
        """Creates a new mock, based on a dummy object providing
        `interfaces`. The first interface in `interfaces` is directly
        provided, the rest are also-provided.
        """
        self._check_super_setup()
        dummy = self.create_dummy()

        if isinstance(interfaces, (list, tuple, set)):
            first_interface = interfaces.pop(0)

        elif issubclass(interfaces, Interface):
            first_interface = interfaces
            interfaces = []

        directlyProvides(dummy, first_interface)

        for iface in interfaces:
            alsoProvides(dummy, iface)

        return self.mocker.proxy(dummy, False, *args, **kwargs)

    def mock_interface(self, interface, provides=None, *args, **kwargs):
        """Creates and returns a new mock object implementing `interface`.
        The interface is used as "spec" - the test fails when an undefined
        method is mocked or the method signature does not match the
        interface.
        """
        self._check_super_setup()
        spec = Implementer(interface)()
        if provides:
            classImplements(spec, provides)
        return self.mocker.mock(spec, *args, **kwargs)

    def stub(self, *args, **kwargs):
        """Creates a stub object, which does not assert the applied
        expectations.
        """
        self._check_super_setup()
        kwargs['count'] = False
        return self.mocker.mock(*args, **kwargs)

    def providing_stub(self, interfaces, *args, **kwargs):
        """Creates a stub object providing a list of interfaces.
        """
        self._check_super_setup()
        kwargs['count'] = False
        return self.providing_mock(interfaces, *args, **kwargs)

    def stub_interface(self, interface, provides=None, *args, **kwargs):
        """Creates a stub object, implementing `interface` and using it
        as spec.
        """
        self._check_super_setup()
        kwargs['count'] = False
        return self.mock_interface(interface, provides=None, *args, **kwargs)

    def set_parent(self, context, parent_context):
        """Set the acquisition parent of `context` to `parent_context`.
        """
        self._check_super_setup()
        expect(aq_parent(aq_inner(context))).result(
            parent_context).count(0, None)
        return context

    def assertRaises(self, *args, **kwargs):
        """Use assertRaises from unittest2. This allows us to use it
        with python (>=2.6) `with` statement.

        >>> with self.assertRaises(TypeError) as cm:
        ...     1 + 'foo'
        >>> self.assertEqual(
        ...     str(cm.exception),
        ...     "unsupported operand type(s) for +: 'int' and 'str'")
        """
        return unittest2.TestCase.assertRaises(self, *args, **kwargs)

    def mock_tool(self, mock, name):
        """Register a mock tool that will be returned when getToolByName()
        is called.
        """
        self._check_super_setup()

        if self._getToolByName_replacements is None:
            self._getToolByName_replacements = []
            self._getToolByName_replacements.append(self.mocker.replace(
                    'Products.CMFCore.utils.getToolByName'))

            import pkg_resources
            try:
                pkg_resources.get_distribution(
                    'Products.PloneHotfix20121106')
            except pkg_resources.DistributionNotFound:
                pass
            else:
                self._getToolByName_replacements.append(self.mocker.replace(
                        'Products.PloneHotfix20121106.gtbn.gtbn'))

        # patch: do not count.
        for replacement in self._getToolByName_replacements:
            self.expect(replacement(ANY, name)).result(
                mock).count(0, None)

    def stub_request(self, interfaces=[], stub_response=True,
                     content_type='text/html', status=200):
        """Returns a stub request providing IDefaultBrowserLayer with some
        headers and options required for rendering templates.

        Keyword arguments:
        interfaces -- all interfaces the request should provide additionaly.
        stub_respone -- option if the request should stub a response
        by him self.
        content_type -- response content_type (default 'text/html')
        status -- response http status code (default 200)
        """
        self._check_super_setup()

        default_interfaces = [IDefaultBrowserLayer, IBrowserRequest]
        if isinstance(interfaces, (list, tuple, set)):
            interfaces = default_interfaces + interfaces
        else:
            interfaces = default_interfaces + [interfaces]

        request = self.providing_stub(interfaces)
        self.expect(request.debug).result(False)

        if stub_response:
            self.stub_response(request=request, content_type=content_type,
                               status=status)

        return request

    def stub_response(self, request=None,
                      content_type='text/html', status=200):
        """Returns a stub response with some headers and options.
        An append it also to the given request.

        Keyword arguments:
        request = the request who the response should appent it.
        content_type -- response content_type (default 'text/html')
        status -- response http status code (default 200)
        """
        self._check_super_setup()

        response = self.stub()
        if request:
            self.expect(request.response).result(response)
            self.expect(request.RESPONSE).result(response)

        self.expect(response.getStatus()).result(status)
        self.expect(response.getHeader('Content-Type')).result(
            content_type)

        return response
