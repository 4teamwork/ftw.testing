from contextlib import contextmanager
from datetime import datetime
from datetime import timedelta
from mocker import expect
from mocker import Mocker
from mocker import ProxyReplacer
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

        # Manually create a proxy mock class for overwriting "now"
        class datetime_class(datetime):
            @staticmethod
            def now():
                return self.new_now
            __mocker_object__ = datetime
            __mocker_replace__ = False

        event = self.mocker._get_replay_restore_event()
        event.add_task(ProxyReplacer(datetime_class))

        # Rebuild the new_now so that it is an instance of the mocked class
        self.new_now = datetime_class(*self.new_now.timetuple()[:-3]
                                       + (self.new_now.microsecond,))

        # Replace "datetime" module
        datetime_module = self.mocker.replace('datetime', spec=False)
        expect(datetime_module.datetime).result(datetime_class).count(0, None)

        # Replace "time" class
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


@contextmanager
def freeze(new_now=None):
    with FreezedClock(new_now or datetime.now()) as clock:
        yield clock
