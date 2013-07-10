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

    def concat_portal_url(self, *path):
        """Concats the portal url with one or more bits of path.
        """
        return '/'.join((self.portal_url,) + path)

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
            'More than one element found with xpath: %s\n%s' % (
            selector,
            str(map(lambda item: item.outer_html, elements)))

        return elements.first

    def normalize_whitespace(self, text):
        return ' '.join(text.split())


class Plone(PageObject):

    def visit_portal(self, *paths):
        """Open the plone site root in the current browser.
        If one or more path partials as passed as positional arguments
        they are appended to the site root url.
        """
        url = self.concat_portal_url(*paths)
        locals()['__traceback_info__'] = (paths, ':', url)
        browser().visit(url)
        return self

    def visit(self, obj, view=None):
        """Open the default view or a particular `view` of the passed
        `obj` in the browser.
        """

        url = obj.absolute_url()
        if view is not None:
            url = '/'.join((url, view))

        locals()['__traceback_info__'] = ('URL:', url)
        browser().visit(url)
        return self

    def login(self, user=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        """Log the current browser in with the passed user / password or with
        the default `plone.app.testing` user if no arguemnts are passed.
        """

        if self.browser_driver == 'zope.testbrowser':
            browser()._browser.addHeader('Authorization',
                                         'Basic %s:%s' % (user, password))

        else:
            browser().visit(self.concat_portal_url('login'))
            browser().fill('__ac_name', user)
            browser().fill('__ac_password', password)
            browser().find_by_xpath(
                '//input[@type="submit" and @value="Log in"]').first.click()

        return self

    def get_first_heading(self):
        """Returns the first heading (h1.documentFirstHeading) of the current
        page.
        """
        return self.normalize_whitespace(
            browser().find_by_css('h1.documentFirstHeading').text)

    def get_body_classes(self):
        """Returns the classes of the body node.
        """
        body = browser().find_by_xpath('//body').first
        locals()['__traceback_info__'] = browser().url
        assert body, 'No <body> tag found.'
        return body['class'].strip().split(' ')

    def assert_body_class(self, cssclass):
        """Assert that the <body>-Tag of the current page has a class.
        This is useful for asserting that we are on a certain browser
        view (template-folder_contents) or on an object of a certain
        content type (portaltype-folder).
        """
        locals()['__traceback_info__'] = browser().url
        assert cssclass in self.get_body_classes(), \
            'Missing body class "%s" on this page. Body classes are: %s' % (
            cssclass,
            self.get_body_classes())

    def get_template_class(self):
        """Returns the template class of the body node.
        """
        locals()['__traceback_info__'] = browser().url
        template = [cls for cls in self.get_body_classes()
                    if cls.startswith('template-')]

        assert len(template) != 0, \
            'No "tempalte-" class on body tag found.'

        assert len(template) == 1, \
            'Template classes on body ambiguous: %s' % (
            str(template))

        return template[0]

    def portal_messages(self):
        """Returns a dict with lists of portal message elements (dd) grouped
        by type (info, warning, error).
        """
        return {'info': browser().find_by_css('.portalMessage.info dd'),
                'warning': browser().find_by_css('.portalMessage.warning dd'),
                'error': browser().find_by_css('.portalMessage.error dd')}

    def portal_text_messages(self):
        """Returns a dict of lists of portal message texts grouped by
        portal message type (info, warning, error).
        """
        messages = self.portal_messages()
        item_to_text = lambda item: self.normalize_whitespace(
            item.text.strip())

        info_messages = map(item_to_text, messages['info'])

        # remove the empty & invisble KSS info message - we never should assert it.
        if '' in info_messages:
            info_messages.remove('')

        return {'info': info_messages,
                'warning': map(item_to_text, messages['warning']),
                'error': map(item_to_text, messages['error'])}

    def assert_portal_message(self, kind, message, assertion_info=''):
        """Asserts that a status message of a certain `kind` with a given
        `message` text is visible on the current page.
        """
        locals()['__traceback_info__'] = browser().url
        message = message.strip()
        messages = self.portal_text_messages()

        assertion_msg = 'Portal message "%s" of kind %s is not visible. '\
                        'Got %s' % (message, kind, str(messages))
        if assertion_info:
            assertion_msg += '. Additional info %s' % str(assertion_info)
        assert message in messages[kind], assertion_msg

    def assert_no_portal_messages(self):
        """Asserts that there are no portal messages.
        """
        locals()['__traceback_info__'] = browser().url
        messages = self.portal_text_messages()

        assert messages == {'info': [], 'warning': [], 'error': []}, \
            'Expected no portal messages but got: %s' % str(messages)

    def assert_no_error_messages(self):
        """Asserts that there are no error portal messages.
        """
        locals()['__traceback_info__'] = browser().url
        messages = self.portal_text_messages()

        assert messages['error'] == [], \
            'Expected no error portal messages but got: %s' % str(messages)

    def open_add_form(self, type_name):
        """Opens the add form for adding an object of type `type_name` by
        opening the add menu and clicking on the link.
        A ATFormPage or a DXFormPage object is returned, depending on the
        type of object which is added.
        """
        locals()['__traceback_info__'] = browser().url
        if self.javascript_supported:
            browser().find_by_xpath(
                "//span[text() = 'Add new\xe2\x80\xa6']").click()

        factories = [
            self.normalize_whitespace(item.text) for item
            in browser().find_by_css(
                '#plone-contentmenu-factories li a span')]

        assert self.normalize_whitespace(type_name) in factories, \
            'The type "%s" is not addable. Addable types: %s' % (
            type_name, str(factories))

        self.find_one_by_xpath(
            '//a/span[normalize-space(text()) = "%s"]/..' % type_name).click()

        if 'portal_factory' in browser().url:
            return ATFormPage()
        elif '++add++' in browser().url:
            return DXFormPage()
        else:
            raise NotImplementedError()

    def create_object(self, type_title, fields):
        """Creates a new object of type `type_title`.
        The object is created by clicking on the link in the add-menu and
        then filling the passed `fields`.
        The `fields` is a dict of field-labels (e.g. Body Text) and the
        values to be filled.
        """
        page = self.open_add_form(type_title)
        for key, value in fields.items():
            locals()['__traceback_info__'] = (key, value)
            page.fill_field(key, value)

        return page.save()

    def get_button(self, value, type_=None):
        """Returns a button with a certain text (`value`). Optional the type
        of the button (submit, button) may be passed as second argument.

        If no button is found, it returns None.
        If more than one button is found, an AssertionError is thrown.
        """
        if type_ is not None:
            xpr = '//input[@type="%s" and @value="%s"]' % (type_, value)

        else:
            xpr = '//input[(@type="submit" or @type="button")' + \
                ' and @value="%s"]' % value

        elements = browser().find_by_xpath(xpr)

        if len(elements) == 0:
            return None

        assert len(elements) < 2, \
            'Ambiguous matches for button "%s".\nXpath: %s\n%s' % (
            value, xpr, str(map(lambda item: item.outer_html, elements)))

        return elements.first

    def click_button(self, value, type_=None):
        """Click on a butten with a certain text (`value`).
        """
        locals()['__traceback_info__'] = browser().url
        self.get_button(value, type_=type_).click()


class FormPage(Plone):

    def fill_field(self, label, value):
        """Fill the field with the text-`label` with the passed `value`.
        For TinyMCE fields bare HTML is expected.
        """
        locals()['__traceback_info__'] = browser().url
        fields = browser().find_by_xpath(
            '//*[@*[name()="id" or name()="name"]'
            '=//label[normalize-space(text())="%s"]/@for]' % label)

        assert len(fields) != 0, \
            'No field with label-content "%s" found.' % label

        assert len(fields) < 2, \
            'Ambiguous matches for fields with labels "%s": %s' % (
            label, str(map(lambda item: item.outer_html, fields)))

        if 'mce_editable' in fields.first['class'].split(' ') and \
                self.javascript_supported:

            # Typing in the iframe does not work with PhantomJS.
            # Because of this and because we need to have a consistent input
            # value (=HTML) we just set the HTML content in TinyMCE by
            # using JavaScript.
            jscode = 'tinyMCE.getInstanceById("%s").setContent("%s");' % (
                fields.first['name'], value.replace('"', '\"'))
            browser().execute_script(jscode)

        else:
            browser().fill_form({fields.first['name']: value})


class ATFormPage(FormPage):

    def save(self):
        """Save the archetypes add form.
        """
        self.click_button('Save', type_='submit')
        self.assert_portal_message('info', 'Changes saved.')
        return Plone()


class DXFormPage(FormPage):

    def save(self):
        """Save the dexterity add form.
        """
        self.click_button('Save', type_='submit')
        self.assert_portal_message('info', 'Item created',
                                   assertion_info=self.get_form_errors())
        return Plone()

    def get_form_errors(self):
        items = browser().find_by_css('.fieldErrorBox div.error')
        return [self.normalize_whitespace(each.text.strip()) for each in items]


class PloneControlPanel(Plone):

    def open(self):
        """Open the plone control panel in the current browser.
        """
        browser().visit(self.concat_portal_url('@@overview-controlpanel'))
        return self

    def assert_on_control_panel(self):
        """Assert that the current browser is on the plone control panel.
        """
        self.assert_body_class('template-overview-controlpanel')
        self.assert_body_class('portaltype-plone-site')

    def get_control_panel_links(self):
        """Return a dict with the links on the plone control panel.
        Expects that the control panel is already opened.
        The keys of the dict are the text labels of the links, the values
        are the link object.
        """
        self.assert_on_control_panel()
        links = browser().find_by_css('ul.configlets li a')
        return dict(map(lambda link: (link.text.strip(), link), links))

    def get_control_panel_link(self, title):
        """Assuming that we are on the control panel page, click on the
        control panel link with a certain text (`title`).
        """
        return self.get_control_panel_links().get(title)
