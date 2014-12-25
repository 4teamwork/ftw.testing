from Products.statusmessages.interfaces import IStatusMessage
from zope.publisher.browser import BrowserView


class StatusMessagesTestView(BrowserView):

    def __call__(self):
        IStatusMessage(self.request).add('This is an INFO message.', 'info')
        IStatusMessage(self.request).add('This is an ERROR message.', 'error')
        IStatusMessage(self.request).add('This is an WARNING message.', 'warning')
        return self.context.restrictedTraverse('view')()
