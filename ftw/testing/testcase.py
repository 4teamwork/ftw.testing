from Acquisition import aq_inner, aq_parent
from mocker import expect, ANY
from plone import mocktestcase
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import directlyProvides
import unittest2


class MockTestCase(mocktestcase.MockTestCase, unittest2.TestCase):
    """Advanced mock test case.
    """

    def providing_mock(self, interfaces, *args, **kwargs):
        """Creates a new mock, based on a dummy object providing
        `interfaces`. The first interface in `interfaces` is directly
        provided, the rest are also-provided.
        """
        dummy = self.create_dummy()

        if isinstance(interfaces, Interface):
            first_interface = interfaces
            interfaces = []
        else:
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
        expect(aq_parent(aq_inner(context))).result(
            parent_context).count(0, None)
        return context

    def assertRaises(self, *args, **kwargs):
        return unittest2.TestCase.assertRaises(self, *args, **kwargs)

    def mock_tool(self, mock, name):
        """Register a mock tool that will be returned when getToolByName()
        is called.
        """

        if self._getToolByName_mock is None:
            self._getToolByName_mock = self.mocker.replace('Products.CMFCore.utils.getToolByName')

        # patch: do not count.
        self.expect(self._getToolByName_mock(ANY, name)).result(mock).count(0, None)
