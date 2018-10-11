from contextlib import contextmanager
from datetime import datetime
from datetime import timedelta
from forbiddenfruit import curse
from mocker import expect
from mocker import Mocker
from time import mktime
import pytz


class FreezedClock(object):
    """Freeze the clock.

    Supported:
      time.time()
      datetime.now()
      datetime.utcnow()
    """

    def __init__(self, new_now):
        self.new_now = new_now

    def forward(self, **kwargs):
        self.new_now += timedelta(**kwargs)
        self.__exit__(None, None, None)
        self.__enter__()

    def backward(self, **kwargs):
        self.new_now -= timedelta(**kwargs)
        self.__exit__(None, None, None)
        self.__enter__()

    def __enter__(self):
        if type(self.new_now) != datetime:
            raise ValueError(
                'The freeze_date argument must be a datetime.datetime'
                ' instance, got %s' % type(self.new_now).__name__)

        self.mocker = Mocker()

        # Replace "datetime.datetime.now" classmethod
        self._previous_datetime_now = datetime.now

        # Replace "datetime.datetime.utcnow" classmethod
        self._previous_datetime_utcnow = datetime.utcnow

        @classmethod
        def freezed_now(klass, tz=None):
            if not tz:
                return self.new_now.replace(tzinfo=None)

            # Time was frozen to a naive DT, but a TZ-aware time is being requested
            # from now(). We assume the same TZ for freezing as requested by now.
            elif self.new_now.tzinfo is None:
                return self.new_now.replace(tzinfo=tz)

            elif self.new_now.tzinfo != tz:
                return tz.normalize(self.new_now.astimezone(tz))

            return self.new_now

        @classmethod
        def freezed_utcnow(klass):
            if self.new_now.tzinfo and self.new_now.tzinfo != pytz.UTC:
                return pytz.UTC.normalize(self.new_now.astimezone(pytz.UTC))
            return self.new_now

        curse(datetime, 'now', freezed_now)
        curse(datetime, 'utcnow', freezed_utcnow)

        # Replace "time.time" function
        new_time = mktime(self.new_now.timetuple())
        time_class = self.mocker.replace('time.time')
        expect(time_class()).call(lambda: new_time).count(0, None)

        self.mocker.replay()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.mocker.restore()
        self.mocker.verify()
        curse(datetime, 'now', self._previous_datetime_now)
        curse(datetime, 'utcnow', self._previous_datetime_utcnow)


@contextmanager
def freeze(new_now=None):
    with FreezedClock(new_now or datetime.now()) as clock:
        yield clock
