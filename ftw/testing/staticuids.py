from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getGlobalSiteManager
from zope.interface import implements
from zope.site.hooks import getSite
import re


def staticuid(prefix=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            site = getSite()
            pushGlobalRegistry(site)
            try:
                register_static_uid_uitility(prefix=prefix or func.__name__)
                return func(*args, **kwargs)
            finally:
                popGlobalRegistry(site)
        return wrapper
    return decorator


class StaticUUIDGenerator(object):
    implements(IUUIDGenerator)

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
