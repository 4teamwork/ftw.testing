from Products.CMFPlone.tests.utils import MockMailHost as DefaultMockMailHost
from Products.MailHost.MailHost import _mungeHeaders


class MockMessage(object):

    def __init__(self, mfrom, mto, messageText):
        self.mfrom = mfrom
        self.mto = mto
        self.messageText = messageText


MESSAGES = []


class MockMailHost(DefaultMockMailHost):
    """Remembers senders and recipient of messages.

    Provides utility methods to access mails by sender/recipient.

    """
    def reset(self):
        try:
            while MESSAGES.pop():
                pass
        except IndexError:
            pass

    @property
    def messages(self):
        return MESSAGES

    def _send(self, mfrom, mto, messageText, immediate=False):
        self.messages.append(MockMessage(mfrom, mto, messageText))

    def send(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):

        messageText, mto, mfrom = _mungeHeaders(messageText,
                                                mto, mfrom, subject,
                                                charset=charset,
                                                msg_type=msg_type)
        self._send(mfrom, mto, messageText)

    def pop(self):
        return self.messages.pop().messageText

    def get_messages_by_sender(self):
        """Return the messages by sender.
        """

        result = dict()
        for each in self.messages:
            if each.mfrom not in result:
                result[each.mfrom] = []
            result[each.mfrom].append(each.messageText)
        return result

    def get_messages_by_recipient(self):
        """Return the messages by recipient.
        """

        result = dict()
        for each in self.messages:
            for recipient in each.mto:
                if recipient not in result:
                    result[recipient] = []
                result[recipient].append(each.messageText)
        return result

    def get_messages(self):
        """Return a list of message texts.
        """

        return [each.messageText for each in self.messages]

    def has_messages(self):
        """Return whether there are outgoing messages.
        """

        return len(self.messages) > 0
