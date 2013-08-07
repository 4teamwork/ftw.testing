from Products.CMFPlone.tests.utils import MockMailHost as DefaultMockMailHost
from Products.MailHost.MailHost import _mungeHeaders
from persistent.list import PersistentList


class MockMessage(object):

    def __init__(self, mfrom, mto, messageText):
        self.mfrom = mfrom
        self.mto = mto
        self.messageText = messageText


class MockMailHost(DefaultMockMailHost):
    """Remembers senders and recipient of messages.

    Provides utility methods to access mails by sender/recipient.
    """

    def reset(self):
        self._messages = PersistentList()

    def _send(self, mfrom, mto, messageText, immediate=False):
        self._messages.append(MockMessage(mfrom, mto, messageText))

    def send(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):
        messageText, mto, mfrom = _mungeHeaders(messageText,
                                                mto, mfrom, subject,
                                                charset=charset,
                                                msg_type=msg_type)
        self._send(mfrom, mto, messageText)

    def pop(self):
        return self._messages.pop().messageText

    def get_messages_by_sender(self):
        """Return the messages by sender.
        """

        result = dict()
        for each in self._messages:
            if not each.mfrom in result:
                result[each.mfrom] = []
            result[each.mfrom].append(each.messageText)
        return result

    def get_messages_by_recipient(self):
        """Return the messages by recipient.
        """

        result = dict()
        for each in self._messages:
            for recipient in each.mto:
                if not recipient in result:
                    result[recipient] = []
                result[recipient].append(each.messageText)
        return result

    def get_messages(self):
        """Return a list of message texts.
        """

        return [each.messageText for each in self._messages]

    def has_messages(self):
        """Return whether there are outgoing messages.
        """

        return len(self._messages) > 0
