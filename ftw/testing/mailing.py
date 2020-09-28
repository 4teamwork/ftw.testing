from Products.MailHost.interfaces import IMailHost
from ftw.testing import IS_PLONE_5
from plone.registry.interfaces import IRegistry
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
        from ftw.testing.mailhost import MockMailHost

        mockmailhost = MockMailHost('MailHost')
        self.portal.MailHost = mockmailhost
        sm = self.portal.getSiteManager()
        sm.registerUtility(component=mockmailhost,
                           provided=IMailHost)

        if configure:
            mockmailhost.smtp_host = 'localhost'
            if IS_PLONE_5:
                registry = getUtility(IRegistry, context=self.portal)

                if not registry['plone.email_from_address']:
                    self.portal._original_email_address = registry["plone.email_from_address"]
                    registry['plone.email_from_address'] = 'test@localhost'

                if not registry['plone.email_from_name']:
                    self.portal._original_email_name = registry["plone.email_from_name"]
                    registry['plone.email_from_name'] = u'Plone site'
            else:
                self.portal.email_from_address = 'test@localhost'

    def tear_down(self):
        # Do NOT move the MockMailHost import to the top!
        # It patches things implicitly!
        from ftw.testing.mailhost import MockMailHost

        self.get_mailhost().reset()

        sm = self.portal.getSiteManager()
        mailhost = sm.getUtility(IMailHost)
        if isinstance(mailhost, MockMailHost):
            sm.unregisterUtility(component=mailhost, provided=IMailHost)

        if IS_PLONE_5:
            registry = getUtility(IRegistry, context=self.portal)

            if hasattr(self.portal, "_original_email_name"):
                registry["plone.email_from_name"] = self.portal._original_email_name
                delattr(self.portal, "_original_email_name")

            if hasattr(self.portal, "_original_email_address"):
                registry["plone.email_from_address"] = self.portal._original_email_address  # noqa: E501
                delattr(self.portal, "_original_email_address")

    def get_mailhost(self):
        mailhost = getUtility(IMailHost)

        # Do NOT move the MockMailHost import to the top!
        # It patches things implicitly!
        from ftw.testing.mailhost import MockMailHost

        assert isinstance(mailhost, MockMailHost), \
            'The mailhost mocking was not set up properly. ' \
            'Call ftw.testing.pages.Mailing().set_up() in your setUp method.'

        return mailhost

    def get_messages(self):
        return self.get_mailhost().get_messages()

    def get_messages_by_recipient(self):
        return self.get_mailhost().get_messages_by_recipient()

    def get_messages_by_sender(self):
        return self.get_mailhost().get_messages_by_sender()

    def has_messages(self):
        return self.get_mailhost().has_messages()

    def pop(self):
        return self.get_mailhost().pop()

    def reset(self):
        self.get_mailhost().reset()
