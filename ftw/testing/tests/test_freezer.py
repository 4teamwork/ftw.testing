from DateTime import DateTime
from ftw.testing import freeze
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.mocktestcase.dummy import Dummy
from unittest2 import TestCase
import datetime
import pytz
import time
import transaction

datetime_module = datetime
datetime_class = datetime.datetime
time_module = time
time_class = time.time


class TestFreeze(TestCase):

    def test_datetime_module_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)

        self.assertLess(the_date, datetime_module.datetime.now())
        with freeze(the_date):
            self.assertEquals(the_date, datetime_module.datetime.now(),
                              'Existing dateitme MODULE pointers are not patched.')
        self.assertLess(the_date, datetime_module.datetime.now())

    def test_datetime_class_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)

        self.assertLess(the_date, datetime_class.now())
        with freeze(the_date):
            self.assertEquals(the_date, datetime_class.now(),
                              'Existing datetime CLASS pointers are not patched.')
        self.assertLess(the_date, datetime_class.now())

    def test_time_module_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)
        the_time = 1287529200.0

        self.assertLess(the_time, time_module.time())
        with freeze(the_date):
            self.assertEquals(the_time, time_module.time(),
                              'Existing time CLASS pointers are not patched.')
        self.assertLess(the_time, time_module.time())

    def test_time_class_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)
        the_time = 1287529200.0

        self.assertLess(the_time, time_class())
        with freeze(the_date):
            self.assertEquals(the_time, time_class(),
                              'Existing time CLASS pointers are not patched.')
        self.assertLess(the_time, time_class())

    def test_zope_datetime_freezing(self):
        the_date = datetime.datetime(2010, 1, 1, 1)
        the_zope_date = DateTime(the_date)

        self.assertLess(the_zope_date, DateTime())
        with freeze(the_date):
            self.assertEquals(the_zope_date, DateTime())
        self.assertLess(the_zope_date, DateTime())

    def test_timeldelta_still_works(self):
        # Since we patch everything, make sure
        # that datetime.timedelta is still there
        the_date = datetime.datetime(2010, 10, 20)
        with freeze(the_date):
            self.assertLess(the_date, the_date + datetime.timedelta(days=1))

    def test_fromtimestamp_still_works(self):
        # Since we patch everything, make sure
        # that datetime.timedelta is still there
        with freeze(datetime.datetime(2010, 10, 20)):
            self.assertEquals(datetime.datetime(1970, 1, 1, 1, 0, 1),
                              datetime_class.fromtimestamp(1))

    def test_verifies_argument(self):
        with self.assertRaises(ValueError) as cm:
            with freeze(10):
                pass

        self.assertEquals(
            str(cm.exception),
            'The freeze_date argument must be a datetime.datetime'
            ' instance, got int')

    def test_isinstance_still_works(self):
        with freeze(datetime.datetime(2010, 10, 20)):
            self.assertTrue(isinstance(datetime.datetime.now(),
                                       datetime_class))

    def test_handles_tzinfo_correctly(self):
        with freeze(datetime.datetime(2015, 01, 01, 7, 15, tzinfo=pytz.UTC)):
            self.assertEquals(
                datetime.datetime(2015, 01, 01, 7, 15, tzinfo=pytz.UTC),
                datetime.datetime.now(pytz.UTC))

            self.assertEquals(
                datetime.datetime(2015, 01, 01, 2, 15, tzinfo=pytz.timezone('US/Eastern')),
                datetime.datetime.now(pytz.timezone('US/Eastern')))
            self.assertEquals(pytz.timezone('US/Eastern'),
                              datetime.datetime.now(pytz.timezone('US/Eastern')).tzinfo)

    def test_now_without_tz_returns_timezone_naive_datetime(self):
        freezed = datetime.datetime(2015, 01, 01, 7, 15,
                                    tzinfo=pytz.timezone('US/Eastern'))

        with freeze(freezed):
            self.assertEquals(
                datetime.datetime(2015, 01, 01, 7, 15),
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

    def test_patches_are_removed_from_freezed_instances(self):
        with freeze():
            dummy = Dummy(datetime_class=datetime.datetime,
                          date=datetime.datetime.now())

        self.assertEquals(
            {'class': 'datetime.datetime',
             'instance': 'datetime.datetime'},

            {'class': '.'.join((dummy.datetime_class.__module__,
                                dummy.datetime_class.__name__)),
             'instance': '.'.join((type(dummy.date).__module__,
                                   type(dummy.date).__name__))})


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
