from contextlib import contextmanager
from datetime import timedelta
from ftw.testing.patch import patch_refs
from six import with_metaclass
from six.moves import copyreg
from time import mktime
from time import tzname
import datetime
import inspect
import pytz
import time

orig_datetime = datetime.datetime
datetime_patch_count = 0
__patch_refs__ = False


class FrozenDatetimeMeta(type):

    @classmethod
    def __instancecheck__(self, obj):
        return isinstance(obj, orig_datetime)

    @classmethod
    def __subclasscheck__(cls, subclass):
        return issubclass(subclass, orig_datetime)


class FrozenDatetime(with_metaclass(FrozenDatetimeMeta, datetime.datetime)):

    @classmethod
    def today(cls):
        return cls.now(tz=None)

    @classmethod
    def fromdatetime(cls, dt):
        return FrozenDatetime(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
            dt.microsecond, dt.tzinfo)


# Customize pickling of datetime:
# While frozen, pickling a (non-frozen) datetime instance would fail.
# We have to ensure that datetimes are pickeled as FrozenDatetime in this case.
def pickle_frozendatetime(dt):
    if datetime_patch_count > 0:
        return FrozenDatetime, dt.__reduce__()[1]
    else:
        return orig_datetime, dt.__reduce__()[1]


copyreg.pickle(orig_datetime, pickle_frozendatetime)


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
        self.__patch_refs__ = False

    def forward(self, **kwargs):
        self.new_now += timedelta(**kwargs)
        self.__exit__(None, None, None)
        self.__enter__()

    def backward(self, **kwargs):
        self.new_now -= timedelta(**kwargs)
        self.__exit__(None, None, None)
        self.__enter__()

    def __enter__(self):
        global datetime_patch_count

        if type(self.new_now) != datetime.datetime:
            raise ValueError(
                'The freeze_date argument must be a datetime.datetime'
                ' instance, got %s' % type(self.new_now).__name__)

        # datetime.datetime.now() is a built-in method and can't be patched
        # easily. Thus we replace datetime.datetime with a custom class to
        # allow patching.
        if datetime_patch_count == 0:
            patch_refs(datetime, 'datetime', FrozenDatetime)
        datetime_patch_count += 1

        def is_caller_ignored(frames_up):
            """Inspect the stack for n frames up for a blacklisted caller.

            Stack inspection is very expensive, so we skip this per default as
            we hit this on every access to a frozen time. A fine case example
            of catastrophic access density is a bunch of Plone workflow event
            handlers firing off a Dexterity ``createdInContainer`` event.
            """
            if self.ignore_modules:
                frame = inspect.currentframe()
                for _ in range(frames_up):
                    frame = frame.f_back

                    module = inspect.getmodule(frame)
                    if module:
                        module_name = module.__name__
                        if module_name in self.ignore_modules:
                            return True

            return False

        @classmethod
        def freezed_now(klass, tz=None):
            if is_caller_ignored(3):
                return self._previous_datetime_now(tz)

            if not tz:
                return FrozenDatetime.fromdatetime(
                    self.new_now.replace(tzinfo=None))

            # Time was frozen to a naive DT, but a TZ-aware time is being requested
            # from now(). We assume the same TZ for freezing as requested by now.
            elif self.new_now.tzinfo is None:
                return FrozenDatetime.fromdatetime(
                    self.new_now.replace(tzinfo=tz))

            elif self.new_now.tzinfo != tz:
                return FrozenDatetime.fromdatetime(
                    tz.normalize(self.new_now.astimezone(tz)))

            return FrozenDatetime.fromdatetime(self.new_now)

        self._previous_datetime_now = FrozenDatetime.now
        FrozenDatetime.now = freezed_now

        @classmethod
        def freezed_utcnow(klass):
            if is_caller_ignored(3):
                return self._previous_datetime_utcnow()

            if self.new_now.tzinfo and self.new_now.tzinfo != pytz.UTC:
                return FrozenDatetime.fromdatetime(
                    pytz.UTC.normalize(self.new_now.astimezone(pytz.UTC)))
            return FrozenDatetime.fromdatetime(self.new_now)

        self._previous_datetime_utcnow = FrozenDatetime.utcnow
        FrozenDatetime.utcnow = freezed_utcnow

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

        def frozen_time():
            if is_caller_ignored(7):
                if self.new_now.tzinfo is None:
                    return mktime(self._previous_datetime_now().timetuple())
                else:
                    return mktime(self._previous_datetime_now().tzinfo.normalize(
                        self.new_now + local_tz._utcoffset).utctimetuple())
            return new_time

        self._previous_time_time = time.time
        patch_refs(time, 'time', frozen_time)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        global datetime_patch_count

        FrozenDatetime.now = self._previous_datetime_now
        patch_refs(datetime.datetime, 'utcnow', self._previous_datetime_utcnow)
        patch_refs(time, 'time', self._previous_time_time)

        datetime_patch_count -= 1
        if datetime_patch_count == 0:
            patch_refs(datetime, 'datetime', orig_datetime)


@contextmanager
def freeze(new_now=None, ignore_modules=None):
    with FreezedClock(new_now or datetime.datetime.now(),
                      ignore_modules=ignore_modules) as clock:
        yield clock
