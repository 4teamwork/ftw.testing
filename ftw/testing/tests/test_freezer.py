from DateTime import DateTime
from ftw.testing import freeze
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from unittest2 import TestCase
import datetime
import pytz
import time
import transaction


time_module = time
time_function = time.time


class TestFreeze(TestCase):

    def test_datetime_now_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)

        self.assertLess(the_date, datetime.datetime.now())
        with freeze(the_date):
            self.assertEquals(the_date, datetime.datetime.now(),
                              'Existing dateitme MODULE pointers are not patched.')
        self.assertLess(the_date, datetime.datetime.now())

    def test_time_module_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)
        the_time = 1287529200.0

        self.assertLess(the_time, time_module.time())
        with freeze(the_date):
            self.assertEquals(the_time, time_module.time(),
                              'Existing time CLASS pointers are not patched.')
        self.assertLess(the_time, time_module.time())

    def test_time_function_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)
        the_time = 1287529200.0

        self.assertLess(the_time, time_function())
        with freeze(the_date):
            self.assertEquals(the_time, time_function(),
                              'Existing time FUNCTION pointers are not patched.')
        self.assertLess(the_time, time_function())

    def test_zope_datetime_freezing(self):
        the_date = datetime.datetime(2010, 1, 1, 1)
        the_zope_date = DateTime(the_date)

        self.assertLess(the_zope_date, DateTime())
        with freeze(the_date):
            self.assertEquals(the_zope_date, DateTime())
        self.assertLess(the_zope_date, DateTime())

    def test_verifies_argument(self):
        with self.assertRaises(ValueError) as cm:
            with freeze(10):
                pass

        self.assertEquals(
            str(cm.exception),
            'The freeze_date argument must be a datetime.datetime'
            ' instance, got int')

    def test_handles_tzinfo_correctly(self):
        with freeze(datetime.datetime(2015, 1, 1, 7, 15, tzinfo=pytz.UTC)):
            self.assertEquals(
                datetime.datetime(2015, 1, 1, 7, 15, tzinfo=pytz.UTC),
                datetime.datetime.now(pytz.UTC))

    def test_now_without_tz_returns_timezone_naive_datetime(self):
        freezed = datetime.datetime(2015, 1, 1, 7, 15,
                                    tzinfo=pytz.timezone('US/Eastern'))

        with freeze(freezed):
            self.assertEquals(
                datetime.datetime(2015, 1, 1, 7, 15),
                datetime.datetime.now())

    def test_update_freezed_time_forwards(self):
        with freeze(datetime.datetime(2010, 10, 20)) as clock:
            self.assertEquals(datetime.datetime(2010, 10, 20),
                              datetime.datetime.now())

            clock.forward(days=1)
            self.assertEquals(datetime.datetime(2010, 10, 21),
                              datetime.datetime.now())

    def test_update_freezed_time_backwards(self):
        with freeze(datetime.datetime(2010, 10, 20)) as clock:
            self.assertEquals(datetime.datetime(2010, 10, 20),
                              datetime.datetime.now())

            clock.backward(days=2)
            self.assertEquals(datetime.datetime(2010, 10, 18),
                              datetime.datetime.now())

    def test_freeze_relative_to_current_time(self):
        with freeze() as clock:
            before = datetime.datetime.now()
            clock.forward(hours=1)
            after = datetime.datetime.now()
            self.assertEquals(60 * 60, (after - before).seconds)


class TestFreezeIntegration(TestCase):
    layer = PLONE_FUNCTIONAL_TESTING

    def test_commit_works_with_transactions(self):
        with freeze(datetime.datetime(2015, 7, 22, 11, 45, 58)):
            self.layer['portal'].current_date = datetime.datetime.now()
            transaction.commit()

        transaction.begin()

        thedate = self.layer['portal'].current_date
        self.assertEquals(datetime.datetime(2015, 7, 22, 11, 45, 58), thedate)
        self.assertEquals('datetime.datetime',
                          '.'.join((type(thedate).__module__,
                                    type(thedate).__name__)))
