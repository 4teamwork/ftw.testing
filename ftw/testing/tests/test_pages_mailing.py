from Products.MailHost.interfaces import IMailHost
from ftw.testing.pages import Mailing
from ftw.testing.testing import PAGE_OBJECT_FUNCTIONAL
from unittest2 import TestCase
from zope.component import getUtility


class TestMailingPageObject(TestCase):

    layer = PAGE_OBJECT_FUNCTIONAL

    def setUp(self):
        Mailing(self.layer['portal']).set_up(configure=True)

    def tearDown(self):
        Mailing(self.layer['portal']).tear_down()

    def test_mailing_mock(self):
        mailhost = getUtility(IMailHost)
        mailhost.send(messageText='Hello World',
                      mto='info@4teamwork.ch',
                      mfrom='info@4teamwork.ch',
                      subject='A test mail from ftw.testing')

        self.assertTrue(Mailing(self.layer['portal']).has_messages(),
                        'There should be one message in the MockMailHost,'
                        ' but there was none.')

        message = Mailing(self.layer['portal']).pop().split('\n')

        # replace "Date: ..." - it changes constantly.
        message = [line.startswith('Date:') and 'Date: ---' or line
                   for line in message]

        self.assertEquals(
            ['Subject: A test mail from ftw.testing',
             'To: info@4teamwork.ch',
             'From: info@4teamwork.ch',
             'Date: ---',
             '',
             'Hello World'],

            message)
