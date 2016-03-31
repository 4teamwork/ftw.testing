from contextlib import contextmanager
from datetime import datetime
from datetime import timedelta
from forbiddenfruit import curse
from mocker import expect
from mocker import Mocker
import calendar


class FreezedClock(object):

    def __init__(self, new_now):
        self.new_now = new_now

    def forward(self, **kwargs):
        self.new_now = datetime.now() + timedelta(**kwargs)
        self.__exit__(None, None, None)
        self.__enter__()

    def backward(self, **kwargs):
        self.new_now = datetime.now() - timedelta(**kwargs)
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

        @classmethod
        def freezed_now(klass, tz=None):
            if not tz:
                return self.new_now.replace(tzinfo=None)
            elif self.new_now.tzinfo != tz:
                return tz.normalize(self.new_now.astimezone(tz))
            else:
                return self.new_now

        curse(datetime, 'now', freezed_now)

        # Replace "time.time" function
        new_time = (calendar.timegm(self.new_now.timetuple()) +
                    (self.new_now.timetuple().tm_isdst * 60 * 60) +
                    (self.new_now.microsecond * 0.000001))
        time_class = self.mocker.replace('time.time')
        expect(time_class()).call(lambda: new_time).count(0, None)

        self.mocker.replay()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.mocker.restore()
        self.mocker.verify()
        curse(datetime, 'now', self._previous_datetime_now)


@contextmanager
def freeze(new_now=None):
    with FreezedClock(new_now or datetime.now()) as clock:
        yield clock
