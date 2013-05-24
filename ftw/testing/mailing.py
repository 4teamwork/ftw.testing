from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility


class Mailing(object):
    """The Mailing helper object mocks the mailhost and captures sent emails.
    The emails can then be easily used for assertions.
    """

    def __init__(self, portal):
        self.portal = portal

    def set_up(self, configure=True):
        """Setup a mock mail host so that emails can be catched and tested.
        """

        # Do NOT move the MockMailHost import to the top!
        # It patches things implicitly!
        from Products.CMFPlone.tests.utils import MockMailHost

        mockmailhost = MockMailHost('MailHost')
        self.portal.MailHost = mockmailhost
        sm = self.portal.getSiteManager()
        sm.registerUtility(component=mockmailhost,
                           provided=IMailHost)

        if configure:
            mockmailhost.smtp_host = 'localhost'
            self.portal.email_from_address = 'test@localhost'

    def tear_down(self):
        # Do NOT move the MockMailHost import to the top!
        # It patches things implicitly!
        from Products.CMFPlone.tests.utils import MockMailHost

        sm = self.portal.getSiteManager()
        mailhost = sm.getUtility(IMailHost)
        if isinstance(mailhost, MockMailHost):
            sm.unregisterUtility(component=mailhost, provided=IMailHost)

    def get_mailhost(self):
        mailhost = getUtility(IMailHost)

        # Do NOT move the MockMailHost import to the top!
        # It patches things implicitly!
        from Products.CMFPlone.tests.utils import MockMailHost

        assert isinstance(mailhost, MockMailHost), \
            'The mailhost mocking was not set up properly. ' \
            'Call ftw.testing.pages.Mailing().set_up() in your setUp method.'
        return mailhost

    def get_messages(self):
        return self.get_mailhost().messages

    def has_messages(self):
        return len(self.get_messages()) > 0

    def pop(self):
        return self.get_messages().pop()

    def reset(self):
        # self.get_mailhost().reset()
        try:
            while self.pop():
                pass
        except IndexError:
            pass