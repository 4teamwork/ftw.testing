from Products.MailHost.interfaces import IMailHost
from ftw.testing.mailing import Mailing
from ftw.testing.testing import FTW_TESTING_FUNCTIONAL
from unittest2 import TestCase
from zope.component import getUtility


class TestMailing(TestCase):

    layer = FTW_TESTING_FUNCTIONAL

    def setUp(self):
        self.mailing = Mailing(self.layer['portal'])
        self.mailing.set_up(configure=True)
        self.mailhost = getUtility(IMailHost)

    def tearDown(self):
        Mailing(self.layer['portal']).tear_down()

    def _send_test_mail(self, mto='info@4teamwork.ch',
                        mfrom='info@4teamwork.ch'):
        self.mailhost.send(messageText='Hello World',
                           mto=mto,
                           mfrom=mfrom,
                           subject='A test mail from ftw.testing')

    def test_reset(self):
        self.assertEqual(0, len(self.mailing.get_messages()))
        self._send_test_mail()
        self.assertEqual(1, len(self.mailing.get_messages()))
        self.mailing.reset()
        self.assertEqual(0, len(self.mailing.get_messages()))

    def test_has_messages(self):
        self.assertFalse(self.mailhost.has_messages())
        self._send_test_mail()
        self.assertTrue(self.mailhost.has_messages())

    def test_pop_from_empty_list_fails(self):
        self.assertRaises(IndexError, self.mailing.pop)

    def test_pop_from_filled_list(self):
        self._send_test_mail()
        message = self.mailing.pop()
        self.assertIn('info@4teamwork.ch', message)

    def test_get_messages_by_recipient(self):
        self._send_test_mail()
        self._send_test_mail()
        self._send_test_mail(mto='foo@example.com')

        messages = self.mailing.get_messages_by_recipient()
        self.assertEqual(2, len(messages), 'expected two recipients')
        self.assertIn('foo@example.com', messages)
        self.assertIn('info@4teamwork.ch', messages)

        self.assertEqual(2, len(messages['info@4teamwork.ch']))
        self.assertEqual(1, len(messages['foo@example.com']))

    def test_get_messages_by_sender(self):
        self._send_test_mail()
        self._send_test_mail()
        self._send_test_mail(mfrom='foo@example.com')

        messages = self.mailing.get_messages_by_sender()
        self.assertEqual(2, len(messages), 'expected two senders')
        self.assertIn('foo@example.com', messages)
        self.assertIn('info@4teamwork.ch', messages)

        self.assertEqual(2, len(messages['info@4teamwork.ch']))
        self.assertEqual(1, len(messages['foo@example.com']))

    def test_mailing_mock(self):
        self._send_test_mail()
        self.assertTrue(Mailing(self.layer['portal']).has_messages(),
                        'There should be one message in the MockMailHost,'
                        ' but there was none.')

        self.assertEquals(
            1, len(Mailing(self.layer['portal']).get_messages()),
            'Expected exactly one email in the MockMailHost.')
        message = Mailing(self.layer['portal']).pop().split('\n')
        self.assertEquals(
            0, len(Mailing(self.layer['portal']).get_messages()),
            'Expected no email in the MockMailHost after popping.')

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
