from ftw.testing import FTWIntegrationTestCase
from ftw.testing import IS_PLONE_5
from ftw.testing.testing import FTW_TESTING_INTEGRATION
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


class TestIntegrationTesting(FTWIntegrationTestCase):
    layer = FTW_TESTING_INTEGRATION

    def test_zodb_changes_are_isolated_1(self):
        """This test makes sure that changes applied within a test are not
        leaking to the next test but are isolated correctly.
        """
        self.login(SITE_OWNER_NAME)
        self.assertEquals('Plone site', self.get_site_title(),
                          'ZODB changes seem not to be isolated between tests.')
        self.set_site_title(u'New Site Title')
        self.assertEquals('New Site Title', self.get_site_title())

    # By duplicating the method pointer on the class this test will be
    # executed twice. The test is built so that it detects leaks from
    # a prior run when the isolation does not work.
    test_zodb_changes_are_isolated_2 = test_zodb_changes_are_isolated_1

    def test_rollback_nested_savepoints(self):
        """It should be possible to use savepoints in tests, although
        the testing layer uses savepoints for isolation.
        """
        self.login(SITE_OWNER_NAME)
        self.assertEquals('Plone site', self.get_site_title())
        savepoint = transaction.savepoint()
        self.set_site_title(u'Foo')
        self.assertEquals('Foo', self.get_site_title())
        savepoint.rollback()
        self.assertEquals('Plone site', self.get_site_title())

    def set_site_title(self, title):
        if IS_PLONE_5:
            getUtility(IRegistry)['plone.site_title'] = title
        else:
            self.portal.setTitle(title)

    def get_site_title(self):
        if IS_PLONE_5:
            return getUtility(IRegistry)['plone.site_title']
        else:
            return self.portal.Title()


class TestIntegrationTestCase(FTWIntegrationTestCase):
    layer = FTW_TESTING_INTEGRATION

    def test_serverside_default_user_is_anonymous(self):
        """We prefer creating new users with real roles for tests than
        reusing a testing user and granting additional roles.

        Use ftw.builder or a fixture.
        """
        self.assertTrue(api.user.is_anonymous())

    def test_login_with_userid(self):
        """Login accepts userids.
        """
        self.assertTrue(api.user.is_anonymous())
        self.login(TEST_USER_NAME)
        self.assertFalse(api.user.is_anonymous())
        self.assertEqual(TEST_USER_ID, api.user.get_current().getId())

    def test_login_with_user_object(self):
        """Login accepts a user object.
        """
        self.assertTrue(api.user.is_anonymous())
        self.login(api.user.get(TEST_USER_ID))
        self.assertFalse(api.user.is_anonymous())
        self.assertEqual(TEST_USER_ID, api.user.get_current().getId())

    def test_login_as_context_manager(self):
        """Login can be used as context manager.
        """
        self.assertTrue(api.user.is_anonymous())

        with self.login(TEST_USER_NAME):
            self.assertFalse(api.user.is_anonymous())
            self.assertEqual(TEST_USER_ID, api.user.get_current().getId())

            with self.login(SITE_OWNER_NAME):
                self.assertFalse(api.user.is_anonymous())
                self.assertEqual(SITE_OWNER_NAME, api.user.get_current().getId())

            self.assertFalse(api.user.is_anonymous())
            self.assertEqual(TEST_USER_ID, api.user.get_current().getId())

        self.assertTrue(api.user.is_anonymous())

    def test_observe_children(self):
        self.login(SITE_OWNER_NAME)

        container = api.content.create(self.portal, 'Folder', title=u'Container')
        old = api.content.create(container, 'Folder', title=u'Old')
        with self.observe_children(container) as children:
            self.assertEquals({'before': [old]}, children)
            new = api.content.create(container, 'Folder', title=u'New')
            api.content.delete(old)

        self.assertEquals(
            {'before': [old],
             'removed': {old},
             'added': {new},
             'after': [new]},
            children)
