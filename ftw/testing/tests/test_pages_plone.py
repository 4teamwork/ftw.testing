from ftw.testing import browser
from ftw.testing.pages import Plone
from ftw.testing.testing import PAGE_OBJECT_FUNCTIONAL
from mechanize._mechanize import BrowserStateError
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
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

        Plone().visit_portal('login')
        self.assertIn(browser().url, [
                # Plone <= 4.0
                'http://nohost/plone/login_form?came_from=localhost',
                # Plone >= 4.1
                'http://nohost/plone/login',
                ])

    def test_login(self):
        Plone().visit_portal()

        self.assertTrue(browser().find_link_by_text('Log in'),
                        'Could not find login link.')

        Plone().login()
        Plone().visit_portal()

        self.assertFalse(browser().find_link_by_text('Log in'),
                         'Found Log in link - assuming not logged in.')

    def test_get_first_heading(self):
        Plone().visit_portal()
        self.assertEquals('Plone site', Plone().get_first_heading())

    def test_get_body_classes(self):
        Plone().visit_portal()
        self.assertIn('portaltype-plone-site',
                      set(Plone().get_body_classes()),
                      'Expected portaltype-plone-site to be a body class.')

    def test_assert_body_class(self):
        Plone().visit_portal()

        Plone().assert_body_class('portaltype-plone-site')

        with self.assertRaises(AssertionError):
            Plone().assert_body_class('some-class')

    def test_get_template_class(self):
        Plone().visit_portal()

        self.assertEquals(
            'template-folder_listing',
            Plone().get_template_class(),
            'Expected template class on body to be template-folder_listing')

    def test_portal_messages(self):
        Plone().visit_portal('test_rendering')

        message_count = dict((type_, len(msgs)) for (type_, msgs)
                             in Plone().portal_messages().items())

        self.assertEquals({'info': 2,
                           'warning': 0,
                           'error': 0}, message_count)

    def test_portal_text_messages(self):
        Plone().visit_portal('test_rendering')

        self.assertEquals(
            {'info': ['The portalMessage class, can also contain links'
                      ' - used to give the user temporary status messages.'],
             'warning': [],
             'error': []},

            Plone().portal_text_messages())

    def test_assert_portal_message(self):
        Plone().visit_portal('test_rendering')

        Plone().assert_portal_message(
            'info',
            'The portalMessage class, can also contain links'
            ' - used to give the user temporary status messages.')

        with self.assertRaises(AssertionError) as cm:
            Plone().assert_portal_message('error', 'Something')

        self.assertEquals(
            'Portal message "Something" of kind error is not visible.'
            ' Got {\'info\': [\'The portalMessage class, can'
            ' also contain links - used to give the user temporary'
            ' status messages.\'], \'warning\': [], \'error\': []}',

            str(cm.exception))

    def test_open_add_form(self):
        Plone().login(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        Plone().visit_portal()

        page = Plone().open_add_form('Folder')
        self.assertEquals('Add Folder', Plone().get_first_heading())

        self.assertEquals(
            'ATFormPage', type(page).__name__,
            'Expected to get a ATFormPage object.')

    def test_create_object(self):
        Plone().login(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        Plone().visit_portal()

        text = 'Some contents for Foo.'
        Plone().create_object('Page', {
                'Title': 'Foo',
                'Body Text': '<strong>%s</strong>' % text})

        self.assertEquals('%s/foo' % Plone().portal_url, browser().url)
        self.assertEquals('Foo', Plone().get_first_heading(),
                          'Title of newly created page is wrong.')
        self.assertTrue(browser().is_text_present(text),
                        'Body Text of newly create page not visible.')

        bold = browser().find_by_xpath('//strong[text()="%s"]' % text).first
        self.assertEquals(text, bold.text,
                          'Insert HTML strong tag could not be found.')

    def test_DEXTERITY_create_object_ZOPE_TESTBROWSER(self):
        Plone().login(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        Plone().visit_portal()

        Plone().create_object('DXType', {'Title': 'Bar'})

        self.assertEquals('%s/bar/view' % Plone().portal_url, browser().url)
        self.assertEquals('Bar', Plone().get_first_heading(),
                          'Title of newly created page is wrong.')

    def test_no_portal_messages(self):
        Plone().visit_portal()
        Plone().assert_no_portal_messages()

        Plone().visit_portal('test_rendering')
        with self.assertRaises(AssertionError) as cm:
            Plone().assert_no_portal_messages()

        self.assertEquals(
            str(cm.exception),
            "Expected no portal messages but got:"
            " {'info': ['The portalMessage class, can also contain"
            " links - used to give the user temporary status messages.'],"
            " 'warning': [],"
            " 'error': []}")

    def test_assert_no_error_messages(self):
        Plone().visit_portal('test_rendering')
        Plone().assert_no_error_messages()
