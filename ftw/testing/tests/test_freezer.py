from DateTime import DateTime
from ftw.testing import freeze
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from unittest import TestCase
import datetime
import pickle
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
                              'Existing datetime MODULE pointers are not patched.')
        self.assertLess(the_date, datetime.datetime.now())

    def test_datetime_utcnow_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)

        self.assertLess(the_date, datetime.datetime.utcnow())
        with freeze(the_date):
            self.assertEquals(the_date, datetime.datetime.utcnow(),
                              'Existing datetime MODULE pointers are not patched.')
        self.assertLess(the_date, datetime.datetime.utcnow())

    def test_time_module_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)
        the_time = time.mktime(the_date.timetuple())

        self.assertLess(the_time, time_module.time())
        with freeze(the_date):
            self.assertEquals(the_time, time_module.time(),
                              'Existing time CLASS pointers are not patched.')
        self.assertLess(the_time, time_module.time())

    def test_time_function_is_patched(self):
        the_date = datetime.datetime(2010, 10, 20)
        the_time = time.mktime(the_date.timetuple())

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
        dt_naive = datetime.datetime(2018, 5, 9, 18, 15)
        dt_naive_plusone = datetime.datetime(2018, 5, 10, 18, 15)

        for timezone in (pytz.UTC, pytz.timezone('US/Eastern'), pytz.timezone('Europe/Zurich'), ):
            dt = dt_naive.replace(tzinfo=timezone)
            dt_utc = pytz.UTC.normalize(dt.astimezone(pytz.UTC))

            dt_plusone = dt_naive_plusone.replace(tzinfo=timezone)
            dt_plusone_utc = pytz.UTC.normalize(dt_plusone.astimezone(pytz.UTC))

            with freeze(dt) as clock:
                self.assertEquals(dt, datetime.datetime.now(timezone))
                self.assertEquals(dt_utc, datetime.datetime.utcnow())
                self.assertEquals(dt, timezone.normalize(DateTime().asdatetime().astimezone(timezone)))
                self.assertEquals(dt_utc, pytz.UTC.normalize(DateTime().asdatetime()))

                clock.forward(days=1)
                self.assertEquals(dt_plusone, datetime.datetime.now(timezone))
                self.assertEquals(dt_plusone_utc, datetime.datetime.utcnow())
                self.assertEquals(dt_plusone, timezone.normalize(DateTime().asdatetime().astimezone(timezone)))
                self.assertEquals(dt_plusone_utc, pytz.UTC.normalize(DateTime().asdatetime()))

                clock.backward(days=1)
                self.assertEquals(dt, datetime.datetime.now(timezone))
                self.assertEquals(dt_utc, datetime.datetime.utcnow())
                self.assertEquals(dt, timezone.normalize(DateTime().asdatetime().astimezone(timezone)))
                self.assertEquals(dt_utc, pytz.UTC.normalize(DateTime().asdatetime()))

    def test_now_without_tz_returns_timezone_naive_datetime(self):
        freezed = datetime.datetime(2015, 1, 1, 7, 15,
                                    tzinfo=pytz.timezone('US/Eastern'))

        with freeze(freezed):
            self.assertEquals(
                datetime.datetime(2015, 1, 1, 7, 15),
                datetime.datetime.now())

    def test_now_with_tz_for_freeze_without_tz_returns_timezone_aware_datetime(self):
        """If Time is frozen with a naive DT, but a TZ-aware time is being requested
        from now(), we assume the same TZ for freezing as requested by now."""
        freezed = datetime.datetime(2015, 1, 1, 7, 15)

        with freeze(freezed):
            self.assertNotEquals(
                datetime.datetime(2015, 1, 1, 7, 15, tzinfo=pytz.timezone('Europe/Zurich')),
                datetime.datetime.now(pytz.timezone('US/Eastern')))

            self.assertEquals(
                datetime.datetime(2015, 1, 1, 7, 15, tzinfo=pytz.timezone('US/Eastern')),
                datetime.datetime.now(pytz.timezone('US/Eastern')))

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

    def test_today_is_now_in_summer(self):
        now = datetime.datetime(2010, 6, 1)
        with freeze(now):
            self.assertEquals(now, datetime.datetime.now())
            self.assertEquals(now, datetime.datetime.today())

    def test_today_is_now_in_winter(self):
        now = datetime.datetime(2010, 12, 1)
        with freeze(now):
            self.assertEquals(now, datetime.datetime.now())
            self.assertEquals(now, datetime.datetime.today())

    def test_ignore_modules(self):
        dt_now = datetime.datetime(2010, 12, 1)
        time_now = time.mktime(dt_now.timetuple())

        with freeze(dt_now):
            self.assertEquals(dt_now, datetime.datetime.now())
            self.assertEquals(dt_now, datetime.datetime.today())
            self.assertEquals(time_now, time_function())

        with freeze(dt_now, ignore_modules=('ftw.testing.tests.test_freezer',)):
            self.assertNotEquals(dt_now, datetime.datetime.now())
            self.assertNotEquals(dt_now, datetime.datetime.today())
            self.assertNotEquals(time_now, time_function())

    def test_ignore_modules_real_time_is_correct(self):
        """This test makes sure that the correct current time is used when
        a module is ignored and should fall back to real time while a freezer is active.
        This is tested by using a wrapping freezer and assuming that freezing behaves correctly.
        """
        dt_now = datetime.datetime(2010, 12, 1)
        time_now = time.mktime(dt_now.timetuple())

        with freeze(dt_now):
            with freeze(datetime.datetime(2000, 1, 1), ignore_modules=('ftw.testing.tests.test_freezer',)):
                self.assertEquals(dt_now, datetime.datetime.now())
                self.assertEquals(dt_now, datetime.datetime.today())
                self.assertEquals(time_now, time_function())

    def test_ignore_modules_real_time_supports_timezones(self):
        timezone = pytz.timezone('Europe/Zurich')
        dt_now = datetime.datetime(2010, 12, 1).replace(tzinfo=timezone)
        time_now = time.mktime(dt_now.timetuple())

        with freeze(dt_now):
            with freeze(datetime.datetime(2000, 1, 1),
                        ignore_modules=('ftw.testing.tests.test_freezer',)):
                self.assertEquals(dt_now, datetime.datetime.now(timezone))
                self.assertEquals(time_now, time_function())

    def test_pickling_of_datetime_while_frozen(self):
        dt = datetime.datetime(2019, 11, 22, 13, 45, 31)
        with freeze(datetime.datetime(2015, 7, 22, 11, 45, 58)):
            try:
                pickle.dumps(dt)
            except pickle.PicklingError:
                self.fail('Pickling of datetime failed.')


class TestFreezeIntegration(TestCase):
    layer = PLONE_FUNCTIONAL_TESTING

    def test_commit_works_with_transactions(self):
        with freeze(datetime.datetime(2015, 7, 22, 11, 45, 58)):
            self.layer['portal'].current_date = datetime.datetime.now()
            transaction.commit()

        transaction.begin()

        thedate = self.layer['portal'].current_date
        self.assertEquals(datetime.datetime(2015, 7, 22, 11, 45, 58), thedate)
        self.assertEquals('ftw.testing.freezer.FrozenDatetime',
                          '.'.join((type(thedate).__module__,
                                    type(thedate).__name__)))
