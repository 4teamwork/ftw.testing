from ftw.testing import browser
from plone.app.testing import PLONE_SITE_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from splinter.browser import _DRIVERS
import os


class PageObject(object):

    @property
    def portal_url(self):
        """Returns the full URL to the plone site under test.
        The URL is different depending on the kind of browser which is
        used: zope.testbrowser uses a fake-url (e.g. http://nohost/plone),
        but when using phantomjs or a real browser we need to use
        a proper URL with the right port (e.g. http://localhost:5501/plone).

        The URL can be influenced by setting environment variables.
        This allows to connect to remote hosts (e.g. for CI servers with VMs)
        or to hook a varnish or similar in between.
        """

        if self.browser_driver == 'zope.testbrowser':
            return 'http://nohost/%s' % PLONE_SITE_ID

        host = os.environ.get('ZSERVER_HOST', 'localhost')
        port = int(os.environ.get('PLONE_TESTING_PORT',
                                  os.environ.get('ZSERVER_PORT', 55001)))

        return 'http://%s:%s/%s' % (host, port, PLONE_SITE_ID)

    @property
    def browser_driver(self):
        """Returns the name (string) of the browser driver currently in use.
        Known splinter drivers:
        - firefox
        - remote
        - chrome
        - phantomjs
        - zope.testbrowser
        """

        return next((name for name, klass in _DRIVERS.items()
                     if type(browser()) is klass))

    @property
    def javascript_supported(self):
        """Returns true if the current browser driver supports javascript.
        """

        return self.browser_driver != 'zope.testbrowser'

    @property
    def iframes_supported(self):
        """Returns true if the current browser driver supports iframes.
        """

        return self.browser_driver not in ('zope.testbrowser', 'phantomjs')

    def find_one_by_xpath(self, selector):
        """Finds one single element by xpath.
        If there is no element or more than one matching raise an error.
        """
        elements = browser().find_by_xpath(selector)

        assert len(elements) != 0, \
            'No element found with xpath: %s' % selector

        assert len(elements) == 1, \
            'More than one element found with xpath:%s\n%s' % (
            selector,
            str(map(lambda item: item.outer_html, elements)))

        return elements.first

    def normalize_whitespace(self, text):
        return ' '.join(text.split())


class Plone(PageObject):

    def visit_portal(self):
        browser().visit(self.portal_url)
        return self

    def login(self, user=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        # This should be implemented by setting request headers.
        browser().visit(self.portal_url + '/login')
        browser().fill('__ac_name', user)
        browser().fill('__ac_password', password)
        browser().find_by_xpath(
            '//input[@type="submit" and @value="Log in"]').first.click()

    def get_first_heading(self):
        return browser().find_by_css('.documentFirstHeading').text

    def get_body_classes(self):
        """Returns the classes of the body node.
        """
        body = browser().find_by_xpath('//body').first
        assert body, 'No <body> tag found.'
        return body['class'].strip().split(' ')

    def get_template_class(self):
        """Returns the template class of the body node.
        """
        template = [cls for cls in self.get_body_classes()
                    if cls.startswith('template-')]

        assert len(template) != 0, \
            'No "tempalte-" class on body tag found.'

        assert len(template) == 1, \
            'Template classes on body ambiguous: %s' % (
            str(template))

        return template[0]

    def portal_messages(self):
        return {'info': browser().find_by_css('.portalMessage.info dd'),
                'warning': browser().find_by_css('.portalMessage.warning dd'),
                'error': browser().find_by_css('.portalMessage.error dd')}

    def portal_text_messages(self):
        messages = self.portal_messages()
        item_to_text = lambda item: self.normalize_whitespace(
            item.text.strip())
        return {'info': map(item_to_text, messages['info']),
                'warning': map(item_to_text, messages['warning']),
                'error': map(item_to_text, messages['error'])}

    def assert_portal_message(self, kind, message):
        message = message.strip()
        messages = self.portal_text_messages()
        assert message in messages[kind], \
            'Portal message "%s" of kind %s is not visible. Got %s' % (
            message, kind, str(messages))

    def disable_wysiwyg_for_field(self, fieldname):
        browser().find_by_css(
            'div[data-fieldname=%s] .suppressVisualEditor a' % fieldname).first.click()
        assert browser().is_text_not_present('Edit without visual editor'), \
            'Failed to disable WYSIWYG field "%s"' % fieldname

    def open_add_form(self, type_name):
        if self.javascript_supported:
            browser().find_by_xpath(
                "//span[text() = 'Add new\xe2\x80\xa6']").click()

        self.find_one_by_xpath(
            '//a/span[normalize-space(text()) = "%s"]/..' % type_name).click()

        if 'portal_factory' in browser().url:
            return ATFormPage()
        else:
            raise NotImplementedError()

    def create_object(self, type_title, fields):
        page = self.open_add_form(type_title)
        for key, value in fields.items():
            page.fill_field(key, value)

        page = page.save()
        page.assert_portal_message('info', 'Changes saved.')
        return page

    def get_button(self, value, type_=None):
        if type_ is not None:
            xpr = '//input[@type="%s" and @value="%s"]' % (type_, value)

        else:
            xpr = '//input[(@type="submit" or @type="button") and @value="%s"]' % \
                value

        elements = browser().find_by_xpath(xpr)

        if len(elements) == 0:
            return None

        assert len(elements) < 2, \
            'Ambiguous matches for button "%s".\nXpath: %s\n%s' % (
            value, xpr, str(map(lambda item: item.outer_html, elements)))

        return elements.first

    def click_button(self, value, type_=None):
        self.get_button(value, type_=type_).click()


class FormPage(Plone):

    def fill_field(self, label, value):
        fields = browser().find_by_xpath(
            '//*[@name=//label[normalize-space(text())="%s"]/@for]' % label)

        assert len(fields) != 0, \
            'No field with label-content "%s" found.' % label

        assert len(fields) < 2, \
            'Ambiguous matches for fields with labels "%s": %s' % (
            label, str(map(lambda item: item.outer_html, fields)))

        if 'mce_editable' in fields.first['class'].split(' ') and \
                self.iframes_supported:
            # oh gosh, its tinymce
            with browser().get_iframe('%s_ifr' % fields.first['name']) as frame:
                frame.find_by_xpath('//body').first.type(value)

        else:
            browser().fill_form({fields.first['name']: value})


class ATFormPage(FormPage):

    def save(self):
        self.click_button('Save', type_='submit')
        return Plone()
