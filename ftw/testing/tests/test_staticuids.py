from ftw.testing import staticuid
from ftw.testing.testing import FTW_TESTING_FUNCTIONAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.uuid.interfaces import IUUID
from unittest import TestCase
from zope.component.hooks import getSite


class TestStaticUIDS(TestCase):
    layer = FTW_TESTING_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    @staticuid()
    def test_uid_generation(self):
        doc = self.portal.get(
            self.portal.invokeFactory('Document', 'the-document'))
        self.assertEquals('testuidgeneration000000000000001', IUUID(doc))

    @staticuid('MyUIDS')
    def test_uid_generation_with_custom_prefix(self):
        doc = self.portal.get(
            self.portal.invokeFactory('Document', 'the-document'))
        self.assertEquals('MyUIDS00000000000000000000000001', IUUID(doc))

    @staticuid()
    def test_that_a_very_long_method_name_used_as_prefix_is_cropped(self):
        doc = self.portal.get(
            self.portal.invokeFactory('Document', 'the-document'))
        self.assertEquals('testthataverylongmethodnam000001', IUUID(doc))

    @staticuid()
    def test_site_hook_is_set(self):
        self.assertTrue(getSite(), 'The site hook (getSite) is not set.')

    def test_staticuid_may_be_used_as_context_manager(self):
        with staticuid('foo'):
            one = self.portal.get(self.portal.invokeFactory('Document', 'one'))
        self.assertEquals('foo00000000000000000000000000001', IUUID(one))

    def test_context_manager_requires_prefix(self):
        with self.assertRaises(ValueError) as cm:
            with staticuid():
                pass
        self.assertEquals(
            'A prefix must be defined when using staticuid as a context manager.',
            str(cm.exception))
