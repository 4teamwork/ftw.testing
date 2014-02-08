from DateTime import DateTime
from ftw.testing import freeze
from unittest2 import TestCase
import datetime
import time


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
