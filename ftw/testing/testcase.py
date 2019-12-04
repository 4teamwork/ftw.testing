from ftw.testing.implementer import Implementer
from ftw.testing.patch import patch_refs
from Products.CMFCore import utils as cmf_utils
from zope.interface import alsoProvides
from zope.interface import classImplements
from zope.interface import directlyProvides
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import six
import unittest
import zope.component
import zope.proxy

if six.PY2:
    from mock import create_autospec
    from mock import Mock
else:
    from unittest.mock import create_autospec
    from unittest.mock import Mock


class Dummy(object):
    """Dummy object with arbitrary attributes
    """

    def __init__(self, **kw):
        self.__dict__.update(kw)


class ComponentProxy(zope.proxy.ProxyBase):

    @property
    def __component_name__(self):
        raise AttributeError('mock attribute error')


class BaseMockTestCase(unittest.TestCase):
    """Base class for Plone mock tests.

       Copied over from plone.mocktestcase which is no longer maintained.
       Uses unittest.mock instead of mocker.
    """

    def __init__(self, methodName='runTest'):
        super(BaseMockTestCase, self).__init__(methodName=methodName)
        self._mocked_tools = {}
        self.__patch_refs__ = False

    def setUp(self):
        super(BaseMockTestCase, self).setUp()

        def getToolByName(context, name, default=cmf_utils._marker):
            if name in self._mocked_tools:
                return self._mocked_tools[name]
            return self._original_getToolByName(context, name, default)
        self._original_getToolByName = cmf_utils.getToolByName
        patch_refs(cmf_utils, 'getToolByName', getToolByName)

    def tearDown(self):
        super(BaseMockTestCase, self).tearDown()
        self._mocked_tools = {}
        patch_refs(cmf_utils, 'getToolByName', self._original_getToolByName)

    def create_dummy(self, **kw):
        return Dummy(**kw)

    def mock(self):
        return Mock()

    def mock_utility(self, mock, provides, name=u""):
        """Register the mock as a utility providing the given interface
        """
        if not name:
            mock = ComponentProxy(mock)
        zope.component.provideUtility(
            provides=provides, component=mock, name=name)

    def mock_adapter(self, mock, provides, adapts, name=u""):
        """Register the mock as an adapter providing the given interface
        and adapting the given interface(s)
        """
        if not name:
            mock = ComponentProxy(mock)
        zope.component.provideAdapter(
            factory=mock, adapts=adapts, provides=provides, name=name)

    def mock_subscription_adapter(self, mock, provides, adapts):
        """Register the mock as a utility providing the given interface
        """
        zope.component.provideSubscriptionAdapter(
            factory=mock, provides=provides, adapts=adapts)

    def mock_handler(self, mock, adapts):
        """Register the mock as a utility providing the given interface
        """
        zope.component.provideHandler(factory=mock, adapts=adapts)

    def mock_tool(self, mock, name):
        """Register a mock tool that will be returned when getToolByName()
        is called.
        """
        self._mocked_tools[name] = mock


class MockTestCase(BaseMockTestCase):
    """Advanced mock test case.
    """

    def setUp(self):
        super(MockTestCase, self).setUp()
        self._MockTestCase_setup = True

    def tearDown(self):
        self._check_super_setup()
        super(MockTestCase, self).tearDown()

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
        mock = Mock()

        if isinstance(interfaces, (list, tuple, set)):
            first_interface = interfaces.pop(0)

        elif issubclass(interfaces, Interface):
            first_interface = interfaces
            interfaces = []

        directlyProvides(mock, first_interface)

        for iface in interfaces:
            alsoProvides(mock, iface)

        return mock

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
        return create_autospec(spec)

    def stub(self, *args, **kwargs):
        """Creates a stub object, which does not assert the applied
        expectations.
        """
        self._check_super_setup()
        kwargs['count'] = False
        return self.mock()

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
        context.__parent__ = parent_context
        context.aq_parent = parent_context
        context.aq_inner = context

        return context

    def mock_tool(self, mock, name):
        """Register a mock tool that will be returned when getToolByName()
        is called.
        """
        self._check_super_setup()
        return super(MockTestCase, self).mock_tool(mock, name)

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
        request.debug = False

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
            request.response = response
            request.RESPONSE = response

        response.getStatus.return_value = status

        def getHeader(name):
            return {'Content-Type': content_type}.get(name)
        response.getHeader.side_effect = getHeader

        return response
