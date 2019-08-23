from functools import wraps
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getGlobalSiteManager
from zope.interface import implementer
from zope.site.hooks import getSite
import re


def staticuid(prefix=None):
    """Generate a function decorator or a context manager for static uuids.
    """
    return StaticUUIDActivator(prefix)


class StaticUUIDActivator(object):
    """A utility for configuring and registering a StaticUUIDActivator temporarily
    while caring for proper isolation and teardown.
    The object can be used either as raw context manager or as function decorator.
    """

    def __init__(self, prefix=None):
        self.prefix = prefix

    def __enter__(self):
        if self.prefix is None:
            raise ValueError(
                'A prefix must be defined when using staticuid as a context manager.')
        pushGlobalRegistry(getSite())
        register_static_uid_uitility(prefix=self.prefix)

    def __exit__(self, exc_type, exc_value, traceback):
        popGlobalRegistry(getSite())

    def __call__(self, func):
        # The object is used as decorator.
        if self.prefix is None:
            self.prefix = func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper


@implementer(IUUIDGenerator)
class StaticUUIDGenerator(object):

    def __init__(self, prefix):
        self.prefix = prefix[:26]
        self.counter = 0

    def __call__(self):
        self.counter += 1
        postfix = str(self.counter).rjust(32 - len(self.prefix), '0')
        return self.prefix + postfix


def register_static_uid_uitility(prefix):
    prefix = re.sub(r'[^a-zA-Z0-9]', '', prefix)
    generator = StaticUUIDGenerator(prefix)
    getGlobalSiteManager().registerUtility(component=generator)
