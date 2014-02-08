from contextlib import contextmanager
from datetime import datetime
from mocker import Mocker
from mocker import ProxyReplacer
from mocker import expect
import calendar


@contextmanager
def freeze(new_now):
    if type(new_now) != datetime:
        raise ValueError(
            'The freeze_date argument must be a datetime.datetime'
            ' instance, got %s' % type(new_now).__name__)

    mocker = Mocker()

    # Manually create a proxy mock class for overwriting "now"
    class datetime_class(datetime):
        @staticmethod
        def now():
            return new_now
        __mocker_object__ = datetime
        __mocker_replace__ = False

    event = mocker._get_replay_restore_event()
    event.add_task(ProxyReplacer(datetime_class))

    # Rebuild the new_now so that it is an instance of the mocked class
    new_now = datetime_class(*new_now.timetuple()[:-3] + (new_now.microsecond,))

    # Replace "datetime" module
    datetime_module = mocker.replace('datetime', spec=False)
    expect(datetime_module.datetime).result(datetime_class).count(0, None)

    # Replace "time" class
    new_time = (calendar.timegm(new_now.timetuple()) +
                (new_now.timetuple().tm_isdst * 60 * 60) +
                (new_now.microsecond * 0.000001))
    time_class = mocker.replace('time.time')
    expect(time_class()).call(lambda: new_time).count(0, None)

    mocker.replay()
    try:
        yield
    finally:
        mocker.restore()
        mocker.verify()
