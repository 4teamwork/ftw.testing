from contextlib import contextmanager
from datetime import datetime
from mocker import Mocker
from mocker import expect
import calendar


@contextmanager
def freeze(new_now):
    if type(new_now) != datetime:
        raise ValueError(
            'The freeze_date argument must be a datetime.datetime'
            ' instance, got %s' % type(new_now).__name__)

    mocker = Mocker()

    # Replace "now" function
    now_func = mocker.replace('datetime.datetime.now')
    expect(now_func()).call(lambda: new_now).count(0, None)

    # Replace "datetime" class
    datetime_class = mocker.replace('datetime.datetime')
    expect(datetime_class.now).result(now_func).count(0, None)

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
