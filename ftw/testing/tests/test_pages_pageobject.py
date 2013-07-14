from ftw.testing import browser
from ftw.testing.pages import PageObject
from ftw.testing.testing import PAGE_OBJECT_FUNCTIONAL
from unittest2 import TestCase


class TestPageObject(TestCase):

    layer = PAGE_OBJECT_FUNCTIONAL

    def test_portal_url(self):
        self.assertEquals(PageObject().portal_url, 'http://nohost/plone')

    def test_browser_driver(self):
        self.assertEquals(
            'zope.testbrowser',
            PageObject().browser_driver,
            'Expected browser driver to be "zope.testbrowser"')

    def test_concat_portal_url(self):
        self.assertEquals('http://nohost/plone',
                          PageObject().concat_portal_url())

        self.assertEquals('http://nohost/plone/foo',
                          PageObject().concat_portal_url('foo'))

        self.assertEquals('http://nohost/plone/foo/bar',
                          PageObject().concat_portal_url('foo', 'bar'))

    def test_no_javascript_support(self):
        self.assertFalse(
            PageObject().javascript_supported,
            'Expected zope.testbrowser to not support javascript'
            ' (Current driver is %s)' % PageObject().browser_driver)

    def test_iframes_supported(self):
        self.assertFalse(
            PageObject().iframes_supported,
            'Expected zope.testbrowser to not support iframes'
            ' (Current driver is %s)' % PageObject().browser_driver)

    def test_find_one_by_xpath(self):
        browser().visit(PageObject().portal_url)

        with self.assertRaises(AssertionError) as cm:
            PageObject().find_one_by_xpath('//novalidtag')
        self.assertEquals('No element found with xpath: //novalidtag',
                          str(cm.exception))

        with self.assertRaises(AssertionError) as cm:
            PageObject().find_one_by_xpath('//a')

        msg = str(cm.exception).split('\n')
        self.assertEquals('More than one element found with xpath: //a',
                          msg[0])

        element = PageObject().find_one_by_xpath('//a[text()="Plone"]')
        self.assertEquals(
            'ZopeTestBrowserLinkElement',
            type(element).__name__)

    def test_normalize_whitespace(self):
        self.assertEquals(
            'foo bar baz',
            PageObject().normalize_whitespace(
                '   foo\t \tbar \n  baz\n\n'))
