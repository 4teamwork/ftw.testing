from Acquisition import aq_inner, aq_parent
from ftw.testing.testcase import BaseMockTestCase
from ftw.testing.testcase import MockTestCase
from Products.CMFCore.utils import getToolByName
from unittest import TestResult
from zope.component import getAdapter
from zope.component import getUtility
from zope.component import handle
from zope.component import subscribers
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IFoo(Interface):
    pass


class IBar(Interface):
    pass


class TestBaseMockTestCase(BaseMockTestCase):

    def test_mock_utility(self):
        mock = self.mock()
        self.mock_utility(mock, IFoo)
        self.assertEqual(getUtility(IFoo), mock)

    def test_mock_named_utility(self):
        mock = self.mock()
        self.mock_utility(mock, IFoo, name='foo-util')
        self.assertEqual(getUtility(IFoo, name='foo-util'), mock)

    def test_mock_adapter(self):
        factory = self.mock()
        factory.return_value = self.mock()
        self.mock_adapter(factory, IFoo, [IBar])
        adaptable = self.mock()
        alsoProvides(adaptable, IBar)
        self.assertEqual(getAdapter(adaptable, IFoo), factory())

    def test_mock_named_adapter(self):
        factory = self.mock()
        factory.return_value = self.mock()
        self.mock_adapter(factory, IFoo, [IBar], name='foo-adapter')
        adaptable = self.mock()
        alsoProvides(adaptable, IBar)
        self.assertEqual(
            getAdapter(adaptable, IFoo, name='foo-adapter'), factory())

    def test_mock_subscription_adapter(self):
        factory = self.mock()
        factory.return_value = self.mock()
        self.mock_subscription_adapter(factory, IFoo, [IBar])
        adaptable = self.mock()
        alsoProvides(adaptable, IBar)
        self.assertEqual(subscribers([adaptable], IFoo), [factory()])

    def test_mock_handler(self):
        handler = self.mock()
        self.mock_handler(handler, [IFoo])
        foo_event = self.mock()
        directlyProvides(foo_event, IFoo)
        handle(foo_event)
        handler.assert_called()

    def test_mock_tool(self):
        tool = self.mock()
        self.mock_tool(tool, 'portal_catalog')
        self.assertEqual(getToolByName(None, 'portal_catalog'), tool)
        self.assertEquals(getToolByName(None, 'foobar', 'default'), 'default')
        with self.assertRaises(AttributeError):
            self.assertEquals(getToolByName(None, 'foobar'))


class TestMockTestCase(MockTestCase):
    """This test case may look a bit strange: we are testing the MockTestCase by
    inheriting it and just using it.
    """

    def test_providing_mock_with_multiple_interfaces(self):
        mock = self.providing_mock([IFoo, IBar])
        self.assertTrue(IFoo.providedBy(mock))
        self.assertTrue(IBar.providedBy(mock))

    def test_providing_mock_with_single_interface(self):
        mock = self.providing_mock(IFoo)
        self.assertTrue(IFoo.providedBy(mock))

    def test_stub_does_not_count(self):
        stub = self.stub()
        stub.foo.bar
        stub.foo.bar

    def test_providing_stub_with_multiple_interfaces(self):
        mock = self.providing_stub([IFoo, IBar])
        self.assertTrue(IFoo.providedBy(mock))
        self.assertTrue(IBar.providedBy(mock))
        mock.foo.bar
        mock.foo.bar

    def test_providing_stub_with_single_interfaces(self):
        mock = self.providing_stub(IFoo)
        self.assertTrue(IFoo.providedBy(mock))
        mock.foo.bar
        mock.foo.bar

    def test_set_parent_sets_acquisition(self):
        parent = self.mock()
        child = self.mock()
        self.set_parent(child, parent)
        self.assertEqual(aq_parent(aq_inner(child)), parent)
        self.assertEqual(aq_parent(child), parent)

    def test_assertRaises_from_unittest(self):
        # unittest.TestCase.assertRaises has "with"-support
        with self.assertRaises(Exception):
            raise Exception()

    def test_stub_request(self):
        html_request = self.stub_request()
        js_request = self.stub_request(
            content_type='text/javascript', status=401, interfaces=IFoo)
        iface_request = self.stub_request(interfaces=[IFoo, IBar])

        self.assertTrue(IDefaultBrowserLayer.providedBy(html_request))
        self.assertTrue(IBrowserRequest.providedBy(html_request))
        self.assertEqual(html_request.debug, False)
        self.assertEqual(html_request.response.getHeader(
                'Content-Type'), 'text/html')
        self.assertEqual(html_request.response.getStatus(), 200)

        self.assertTrue(IDefaultBrowserLayer.providedBy(js_request))
        self.assertTrue(IBrowserRequest.providedBy(js_request))
        self.assertTrue(IFoo.providedBy(js_request))
        self.assertEqual(js_request.debug, False)
        self.assertEqual(js_request.response.getHeader(
                'Content-Type'), 'text/javascript')
        self.assertEqual(js_request.response.getStatus(), 401)

        self.assertTrue(IFoo.providedBy(iface_request))
        self.assertTrue(IBar.providedBy(iface_request))
        self.assertTrue(IDefaultBrowserLayer.providedBy(iface_request))
        self.assertTrue(IBrowserRequest.providedBy(iface_request))
        self.assertEqual(html_request.debug, False)
        self.assertEqual(html_request.response.getHeader(
                'Content-Type'), 'text/html')
        self.assertEqual(html_request.response.getStatus(), 200)

    def test_stub_response(self):
        temp_request = self.stub()
        html_response = self.stub_response()

        js_response = self.stub_response(
            request=temp_request, content_type='text/javascript', status=401)

        self.assertEqual(html_response.getHeader('Content-Type'), 'text/html')
        self.assertEqual(html_response.getStatus(), 200)

        self.assertEqual(js_response.getHeader('Content-Type'), 'text/javascript')
        self.assertEqual(
            temp_request.response.getHeader('Content-Type'), 'text/javascript')
        self.assertEqual(js_response.getStatus(), 401)
        self.assertEqual(temp_request.response.getStatus(), 401)


class ILocking(Interface):

    def lock():
        pass

    def unlock(all=False):
        pass


class TestInterfaceMocking(MockTestCase):

    def test_mock_interface_raises_when_function_not_known(self):
        class Test(MockTestCase):
            def runTest(self):
                mock = self.mock_interface(ILocking)
                mock.crack()

        result = TestResult()
        Test().run(result=result)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("Mock object has no attribute 'crack'",
                      result.errors[0][1])

    def test_mock_interface_raises_on_wrong_arguments(self):
        class Test(MockTestCase):
            def runTest(self):
                mock = self.mock_interface(ILocking)
                mock.unlock(force=True)

        result = TestResult()
        Test().run(result=result)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("TypeError: ",
                      result.errors[0][1])

    def test_mock_interface_passes_when_defined_function_is_called(self):
        mock = self.mock_interface(ILocking)
        mock.lock.return_value = 'already locked'
        self.assertEqual(mock.lock(), 'already locked')

    def test_mock_interface_providing_addtional_interfaces(self):
        mock = self.mock_interface(ILocking, provides=[IFoo, IBar])
        self.assertTrue(ILocking.providedBy(mock))
        self.assertTrue(IFoo.providedBy(mock))
        self.assertTrue(IBar.providedBy(mock))

    def test_stub_interface_does_not_count(self):
        mock = self.stub_interface(ILocking)
        mock.lock.return_value = 'already locked'
        self.assertEqual(mock.lock(), 'already locked')
        self.assertEqual(mock.lock(), 'already locked')
        self.assertEqual(mock.lock(), 'already locked')


class TestSetUpError(MockTestCase):

    def setUp(self):
        # super setUp call is missing here
        pass

    def tearDown(self):
        # disables the check on tear down, otherwise we cannot test it..
        pass

    def test_providing_mock(self):
        with self.assertRaises(RuntimeError) as cm:
            self.providing_mock(ILocking)

        self.assertEqual(
            str(cm.exception),
            'TestSetUpError.setUp does not call superclass setUp().')

    def test_mock_interface(self):
        with self.assertRaises(RuntimeError):
            self.mock_interface(ILocking)

    def test_stub(self):
        with self.assertRaises(RuntimeError):
            self.stub()

    def test_providing_stub(self):
        with self.assertRaises(RuntimeError):
            self.providing_mock(ILocking)

    def test_stub_interface(self):
        with self.assertRaises(RuntimeError):
            self.stub_interface(ILocking)

    def test_set_parent(self):
        with self.assertRaises(RuntimeError):
            self.set_parent(None, None)

    def test_mock_tool(self):
        with self.assertRaises(RuntimeError):
            self.mock_tool(None, None)

    def test_stub_request(self):
        with self.assertRaises(RuntimeError):
            self.stub_request()

    def test_stub_response(self):
        with self.assertRaises(RuntimeError):
            self.stub_response()
