from contextlib import contextmanager
from datetime import datetime
from datetime import timedelta
from mocker import expect
from mocker import global_replace
from mocker import Mocker
from mocker import ProxyReplacer
import calendar
import gc
import transaction


class FreezedClock(object):

    def __init__(self, new_now):
        self.new_now = new_now
        self.enabled = False

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
            def now(tz=None):
                if not tz:
                    return self.new_now.replace(tzinfo=None)
                elif self.new_now.tzinfo != tz:
                    return tz.normalize(self.new_now.astimezone(tz))

                return self.new_now
            __mocker_object__ = datetime
            __mocker_replace__ = False

        event = self.mocker._get_replay_restore_event()
        event.add_task(ProxyReplacer(datetime_class))

        # Rebuild the new_now so that it is an instance of the mocked class
        self.new_now = datetime_class(*self.new_now.timetuple()[:-3]
                                      + (self.new_now.microsecond,),
                                      tzinfo=self.new_now.tzinfo)

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
        self.enabled = True
        transaction.get().addBeforeCommitHook(
            self.transaction_before_commit_hook)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        datetime_mock_class = datetime
        self.mocker.restore()
        self.mocker.verify()

        # The labix mocker does only replace pointers to the mock-class which
        # are in dicts.
        # This does not change the class of instances of our mock-class.
        # In order to be able to commit while the time is freezed,
        # we need to replace those classes manually.
        # Since we cannot patch the class of existing instances,
        # we need to construct new instances with the real datetime class and
        # replace all mock instances.
        for referrer in gc.get_referrers(datetime_mock_class):
            if not isinstance(referrer, datetime_mock_class):
                continue
            if getattr(referrer, '__class__') != datetime_mock_class:
                continue
            replacement = datetime(*referrer.timetuple()[:6] + (
                referrer.microsecond,))
            global_replace(referrer, replacement)

        self.enabled = False

    def transaction_before_commit_hook(self):
        """Since a transaction.commit() will serialize the data, it tries
        to serialize the datetime mock-class when freezing is active.
        In order to fix pickling problems while committing we disable the
        freezing temporarily while committing so that mock-based datetime
        instances are replaced with real ones.
        """
        if not self.enabled:
            return

        self.__exit__(None, None, None)
        transaction.get().addAfterCommitHook(
            self.transaction_after_commit_hook)

    def transaction_after_commit_hook(self, status):
        self.__enter__()


@contextmanager
def freeze(new_now=None):
    with FreezedClock(new_now or datetime.now()) as clock:
        yield clock
