from ftw.testing import browser
from ftw.testing.pages import Plone
from ftw.testing.pages import PloneControlPanel
from ftw.testing.testing import PAGE_OBJECT_FUNCTIONAL
from mechanize._mechanize import BrowserStateError
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from unittest2 import TestCase
from zExceptions import Unauthorized


class TestPloneControlPanelPageObject(TestCase):

    layer = PAGE_OBJECT_FUNCTIONAL

    def test_open_control_panel(self):
        # Unauthorized
        with self.assertRaises(Unauthorized):
            PloneControlPanel().open()

        with self.assertRaises(BrowserStateError):
            PloneControlPanel().assert_on_control_panel()

        # Authorized
        Plone().login(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        PloneControlPanel().open()
        PloneControlPanel().assert_on_control_panel()

    def test_get_control_panel_links(self):
        Plone().login(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        PloneControlPanel().open()

        self.assertIn('Calendar',
                      PloneControlPanel().get_control_panel_links(),
                      'Could not find control panel link')

        link = PloneControlPanel().get_control_panel_link('Calendar')
        self.assertTrue(link, 'Could not get control panel link')

        link.click()
        self.assertEquals(
            Plone().concat_portal_url('@@calendar-controlpanel'),
            browser().url,
            'On wrong url after click "Calendar" control panel link.')
