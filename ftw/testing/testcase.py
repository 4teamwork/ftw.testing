from Acquisition import aq_inner, aq_parent
from mocker import expect
from plone import mocktestcase
from zope.interface import alsoProvides
from zope.interface import directlyProvides


class MockTestCase(mocktestcase.MockTestCase):
    """Advanced mock test case.
    """

    def providing_mock(self, interfaces, *args, **kwargs):
        """Creates a new mock, based on a dummy object providing
        `interfaces`. The first interface in `interfaces` is directly
        provided, the rest are also-provided.
        """
        dummy = self.create_dummy()

        first_interface = interfaces.pop(0)
        directlyProvides(dummy, first_interface)

        for iface in interfaces:
            alsoProvides(dummy, iface)

        return self.mocker.proxy(dummy, False, *args, **kwargs)

    def stub(self, *args, **kwargs):
        kwargs['count'] = False
        return self.mocker.mock(*args, **kwargs)

    def providing_stub(self, interfaces, *args, **kwargs):
        kwargs['count'] = False
        return self.providing_mock(interfaces, *args, **kwargs)

    def set_parent(self, context, parent_context):
        expect(aq_parent(aq_inner(expect))).result(
            parent_context).count(0, None)
