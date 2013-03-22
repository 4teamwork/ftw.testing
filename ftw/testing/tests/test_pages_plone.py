from ftw.testing import browser
from ftw.testing import javascript
from ftw.testing.pages import Plone
from ftw.testing.testing import PAGE_OBJECT_FUNCTIONAL
from mechanize._mechanize import BrowserStateError
from unittest2 import TestCase


class TestPlonePageObject(TestCase):

    layer = PAGE_OBJECT_FUNCTIONAL

    def test_visit_portal(self):
        with self.assertRaises(BrowserStateError):
            browser().url

        self.assertTrue(
            Plone().visit_portal(),
            'visit_portal call should return the Plone object itself')

        self.assertEquals(browser().url, 'http://nohost/plone')

    def test_login__ZOPE_TESTBROWSER(self):
        Plone().visit_portal()

        self.assertTrue(browser().find_link_by_text('Log in'),
                        'Could not find login link.')

        Plone().login()

        self.assertFalse(browser().find_link_by_text('Log in'),
                        'Found Log in link - assuming not logged in.')

    @javascript
    def test_login__PHANTOMJS(self):
        Plone().visit_portal()

        self.assertTrue(browser().find_link_by_text('Log in'),
                        'Could not find login link.')

        Plone().login()

        self.assertFalse(browser().find_link_by_text('Log in'),
                        'Found Log in link - assuming not logged in.')

    def test_get_first_heading__TESTBROWSER(self):
        Plone().visit_portal()
        self.assertEquals('Plone site', Plone().get_first_heading())

    @javascript
    def test_get_first_heading__JAVASCRIPT(self):
        Plone().visit_portal()
        self.assertEquals('Plone site', Plone().get_first_heading())
