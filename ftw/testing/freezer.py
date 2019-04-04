from contextlib import contextmanager
from datetime import datetime
from datetime import timedelta
from forbiddenfruit import curse
from mocker import expect
from mocker import Mocker
from time import mktime
from time import tzname
import inspect
import pytz


class FreezedClock(object):
    """Freeze the clock.

    Supported:
      time.time()
      datetime.now()
      datetime.utcnow()
    """

    def __init__(self, new_now, ignore_modules):
        self.new_now = new_now
        self.ignore_modules = ignore_modules or ()

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

        def is_caller_ignored(frames_up):
            """Inspect the stack for n frames up for a blacklisted caller.

            Stack inspection is very expensive, so we skip this per default as
            we hit this on every access to a frozen time. A fine case example
            of catastrophic access density is a bunch of Plone workflow event
            handlers firing off a Dexterity ``createdInContainer`` event.
            """
            if self.ignore_modules:
                caller_frame = inspect.stack()[frames_up][0]
                module_name = inspect.getmodule(caller_frame).__name__
                return module_name in self.ignore_modules
            return False

        self.mocker = Mocker()

        # Replace "datetime.datetime.now" classmethod
        self._previous_datetime_now = datetime.now

        # Replace "datetime.datetime.utcnow" classmethod
        self._previous_datetime_utcnow = datetime.utcnow

        @classmethod
        def freezed_now(klass, tz=None):
            if is_caller_ignored(2):
                return self._previous_datetime_now(tz)

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
            if is_caller_ignored(2):
                return self._previous_datetime_utcnow()

            if self.new_now.tzinfo and self.new_now.tzinfo != pytz.UTC:
                return pytz.UTC.normalize(self.new_now.astimezone(pytz.UTC))
            return self.new_now

        curse(datetime, 'now', freezed_now)
        curse(datetime, 'utcnow', freezed_utcnow)

        # Replace "time.time" function
        # datetime.timetuple does not contain any timezone information, so this
        # information will be lost. Moreover time.time should be in the system
        # timezone, so we need to correct for the offset of timezone used in
        # the freezing relative to the system timezone.
        local_tz = pytz.timezone(tzname[0])
        if self.new_now.tzinfo is None:
            new_time = mktime(self.new_now.timetuple())
        else:
            new_time = mktime(self.new_now.tzinfo.normalize(self.new_now + local_tz._utcoffset).utctimetuple())
        time_class = self.mocker.replace('time.time')

        def frozen_time():
            if is_caller_ignored(7):
                if self.new_now.tzinfo is None:
                    return mktime(self._previous_datetime_now().timetuple())
                else:
                    return mktime(self._previous_datetime_now().tzinfo.normalize(
                        self.new_now + local_tz._utcoffset).utctimetuple())
            return new_time

        expect(time_class()).call(frozen_time).count(0, None)

        self.mocker.replay()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.mocker.restore()
        self.mocker.verify()
        curse(datetime, 'now', self._previous_datetime_now)
        curse(datetime, 'utcnow', self._previous_datetime_utcnow)


@contextmanager
def freeze(new_now=None, ignore_modules=None):
    with FreezedClock(new_now or datetime.now(),
                      ignore_modules=ignore_modules) as clock:
        yield clock
