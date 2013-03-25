from ftw.testing import browser
from ftw.testing import javascript
from ftw.testing.pages import PageObject
from ftw.testing.testing import PAGE_OBJECT_FUNCTIONAL
from unittest2 import TestCase


class TestPageObject(TestCase):

    layer = PAGE_OBJECT_FUNCTIONAL

    def test_portal_url__ZOPE_TESTBROWSER(self):
        self.assertEquals(PageObject().portal_url, 'http://nohost/plone')

    @javascript
    def test_portal_url__JAVASCRIPT(self):
        url = PageObject().portal_url

        self.assertTrue(
            url.endswith('/plone'),
            'Wrong plone site id in url "%s", should be /plone' % (
                url))

        self.assertNotIn(
            'nohost', url,
            'Javascript browser should not use internal hostname "nohost"')

    def test_browser_driver__ZOPE_TESTBROWSER(self):
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

    @javascript
    def test_browser_driver__PHANTOMS(self):
        self.assertEquals(
            'phantomjs',
            PageObject().browser_driver,
            'Expected browser driver to be "phantomjs", because this'
            ' is the default @javascript browser.')

    def test_javascript_support__ZOPE_TESTBROWSER(self):
        self.assertFalse(
            PageObject().javascript_supported,
            'Expected zope.testbrowser to not support javascript'
            ' (Current driver is %s)' % PageObject().browser_driver)

    @javascript
    def test_javascript_support__PHANTOMJS(self):
        self.assertTrue(
            PageObject().javascript_supported,
            'Expected phantomjs to support javascript'
            ' (Current driver is %s)' % PageObject().browser_driver)

    def test_iframes_supported__ZOPE_TESTBROWSER(self):
        self.assertFalse(
            PageObject().iframes_supported,
            'Expected zope.testbrowser to not support iframes'
            ' (Current driver is %s)' % PageObject().browser_driver)

    @javascript
    def test_iframes_supported__PHANTOMS(self):
        self.assertFalse(
            PageObject().iframes_supported,
            'Expected phantomjs to not support iframes'
            ' (Current driver is %s)' % PageObject().browser_driver)

    def test_find_one_by_xpath__ZOPE_TESTBROWSER(self):
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

    @javascript
    def test_find_one_by_xpath__PHANTOMJS(self):
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
            'WebDriverElement',
            type(element).__name__)

    def test_normalize_whitespace(self):
        self.assertEquals(
            'foo bar baz',
            PageObject().normalize_whitespace(
                '   foo\t \tbar \n  baz\n\n'))
