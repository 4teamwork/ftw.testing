from Acquisition import aq_inner, aq_parent
from ftw.testing.testcase import MockTestCase
from zope.interface import Interface


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
