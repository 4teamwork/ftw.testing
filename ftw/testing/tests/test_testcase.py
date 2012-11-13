from Acquisition import aq_inner, aq_parent
from ftw.testing.testcase import MockTestCase
from unittest2 import TestResult
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IFoo(Interface):
    pass


class IBar(Interface):
    pass


class TestMockTestCase(MockTestCase):
    """This test case may look a bit strange: we are testing the MockTestCase by
    inheriting it and just using it.
    """

    def test_providing_mock_with_multiple_interfaces(self):
        mock = self.providing_mock([IFoo, IBar])
        self.replay()
        self.assertTrue(IFoo.providedBy(mock))
        self.assertTrue(IBar.providedBy(mock))

    def test_providing_mock_with_single_interface(self):
        mock = self.providing_mock(IFoo)
        self.replay()
        self.assertTrue(IFoo.providedBy(mock))

    def test_stub_does_not_count(self):
        stub = self.stub()
        self.expect(stub.foo.bar)
        self.replay()
        stub.foo.bar
        stub.foo.bar

    def test_providing_stub_with_multiple_interfaces(self):
        mock = self.providing_stub([IFoo, IBar])
        self.expect(mock.foo.bar)
        self.replay()
        self.assertTrue(IFoo.providedBy(mock))
        self.assertTrue(IBar.providedBy(mock))
        mock.foo.bar
        mock.foo.bar

    def test_providing_stub_with_single_interfaces(self):
        mock = self.providing_stub(IFoo)
        self.expect(mock.foo.bar)
        self.replay()
        self.assertTrue(IFoo.providedBy(mock))
        mock.foo.bar
        mock.foo.bar

    def test_set_parent_sets_acquisition(self):
        parent = self.mocker.mock()
        child = self.mocker.mock()
        self.set_parent(child, parent)
        self.replay()
        self.assertEqual(aq_parent(aq_inner(child)), parent)
        self.assertEqual(aq_parent(child), parent)

    def test_assertRaises_from_unittest2(self):
        # unittest2.TestCase.assertRaises has "with"-support
        with self.assertRaises(Exception):
            raise Exception()

    def test_stub_request(self):
        html_request = self.stub_request()
        js_request = self.stub_request(
            content_type='text/javascript', status=401, interfaces=IFoo)
        iface_request = self.stub_request(interfaces=[IFoo, IBar])

        self.replay()

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

        self.replay()

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
                self.expect(mock.crack()).result(True)
                self.replay()
                mock.crack()

        result = TestResult()
        Test().run(result=result)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 1)
        self.assertIn('mock.crack()\n - Method not ' + \
                          'found in real specification',
                      result.failures[0][1])

    def test_mock_interface_raises_on_wrong_arguments(self):
        class Test(MockTestCase):
            def runTest(self):
                mock = self.mock_interface(ILocking)
                self.expect(mock.unlock(force=True)).result(True)
                self.replay()
                mock.unlock(force=True)

        result = TestResult()
        Test().run(result=result)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 1)
        self.assertIn('mock.unlock(force=True)\n - ' + \
                          'Specification is unlock(all=False): unknown kwargs: force',
                      result.failures[0][1])

    def test_mock_interface_passes_when_defined_function_is_called(self):
        mock = self.mock_interface(ILocking)
        self.expect(mock.lock()).result('already locked')
        self.replay()
        self.assertEqual(mock.lock(), 'already locked')

    def test_mock_interface_providing_addtional_interfaces(self):
        mock = self.mock_interface(ILocking, provides=[IFoo, IBar])
        self.replay()
        self.assertTrue(ILocking.providedBy(mock))
        self.assertTrue(IFoo.providedBy(mock))
        self.assertTrue(IBar.providedBy(mock))

    def test_stub_interface_does_not_count(self):
        mock = self.stub_interface(ILocking)
        self.expect(mock.lock()).result('already locked')
        self.replay()
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
