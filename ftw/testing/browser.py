from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.testing.layers import FunctionalTesting
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser
from splinter.browser import Browser
from splinter.browser import _DRIVERS
from splinter.driver.zopetestbrowser import ZopeTestBrowser
from zope.component.hooks import getSite
from zope.deprecation import deprecated


class FunctionalSplinterTesting(FunctionalTesting):

    defaultBases = ()

    def testSetUp(self):
        super(FunctionalSplinterTesting, self).testSetUp()
        # The default browser is zope.testbrowser.
        # The browser may be changed later using decorators.
        set_browser_driver('zope.testbrowser')

    def testTearDown(self):
        shutdown_browser()
        super(FunctionalSplinterTesting, self).testTearDown()

    def tearDown(self):
        shutdown_all_browser()
        super(FunctionalSplinterTesting, self).tearDown()


class PloneZopeTestBrowser(ZopeTestBrowser):

    def __init__(self, *args, **kwargs):
        super(PloneZopeTestBrowser, self).__init__(*args, **kwargs)
        self._browser.handleErrors = False

    def _get_mech_browser(self, user_agent):
        app = aq_parent(aq_inner(getSite()))
        return Zope2MechanizeBrowser(app)


_DRIVERS['zope.testbrowser'] = PloneZopeTestBrowser


CURRENT_BROWSER_DRIVER = None
CURRENT_BROWSER_INSTANCE = None

# The browser cache may contain browser instances so that the browser can
# be reused for multiple test cases without closing / reopening.
# The key is the driver name (such as "phantomjs"), the value is the browser
# object.
# zope.testbrowser is not cached.
BROWSER_CACHE = {}



def javascript(func):
    """Decorator for marking a test method to require javascript.
    """

    def _javascript_required_decorator(*args, **kwargs):
        set_browser_driver(JAVASCRIPT_BROWSER_DRIVER)
        return func(*args, **kwargs)

    _javascript_required_decorator.__name__ = func.__name__
    return _javascript_required_decorator
deprecated('javascript', 'Javascript support will be dropped soon!')


def browser():
    """Returns a browser instance.
    If no browser is open a browser is created.
    """

    assert CURRENT_BROWSER_DRIVER is not None, \
        'You need to a FunctionalSplinterTesting layer for being able to' \
        ' use the ftw.testing browser abstraction.'

    if CURRENT_BROWSER_INSTANCE is not None:
        return CURRENT_BROWSER_INSTANCE

    elif CURRENT_BROWSER_DRIVER in ('zope.testbrowser'):
        return _set_browser(Browser('zope.testbrowser'))

    elif CURRENT_BROWSER_DRIVER in BROWSER_CACHE:
        return _set_browser(BROWSER_CACHE[CURRENT_BROWSER_DRIVER])

    else:
        obj = _set_browser(Browser(CURRENT_BROWSER_DRIVER))
        BROWSER_CACHE[CURRENT_BROWSER_DRIVER] = obj
        return obj


def clear_browser():
    """Clears the browser session. Depending on the driver the browser is
    completely restarted.
    """

    if CURRENT_BROWSER_DRIVER != 'zope.testbrowser':
        obj = browser()
        obj.cookies.delete()
        obj.visit('file://about:blank')

    _set_browser(None)


def get_driver():
    return CURRENT_BROWSER_DRIVER


def shutdown_browser():
    if CURRENT_BROWSER_INSTANCE is None:
        # no browser is opened - no need for shutting down.
        return

    assert CURRENT_BROWSER_DRIVER is not None
    clear_browser()
    set_browser_driver(None)


def shutdown_all_browser():
    if CURRENT_BROWSER_DRIVER is not None:
        shutdown_browser()

    for name, obj in BROWSER_CACHE.items():
        obj.quit()
        del BROWSER_CACHE[name]


def set_browser_driver(driver):
    globals()['CURRENT_BROWSER_DRIVER'] = driver


DEFAULT_JAVASCRIPT_BROWSER_DRIVER = 'phantomjs'
JAVASCRIPT_BROWSER_DRIVER = DEFAULT_JAVASCRIPT_BROWSER_DRIVER


def _activate_javascript_browser():
    globals()['CURRENT_BROWSER_DRIVER'] = JAVASCRIPT_BROWSER_DRIVER


def _deactivate_javascript_browser():
    globals()['CURRENT_BROWSER_DRIVER'] = None


def _set_browser(obj):
    globals()['CURRENT_BROWSER_INSTANCE'] = obj
    return obj
