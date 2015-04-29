from ftw.testing import staticuid
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase


class TestStaticUIDS(TestCase):
    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    @staticuid()
    def test_uid_generation(self):
        doc = self.portal.get(self.portal.invokeFactory('Document', 'the-document'))
        self.assertEquals('testuidgeneration000000000000001', IUUID(doc))

    @staticuid('MyUIDS')
    def test_uid_generation_with_custom_prefix(self):
        doc = self.portal.get(self.portal.invokeFactory('Document', 'the-document'))
        self.assertEquals('MyUIDS00000000000000000000000001', IUUID(doc))

    @staticuid()
    def test_that_a_very_long_method_name_used_as_prefix_is_cropped(self):
        doc = self.portal.get(self.portal.invokeFactory('Document', 'the-document'))
        self.assertEquals('testthataverylongmethodnam000001', IUUID(doc))
