import os

def get_browser_driver_name():
    """Returns the name of the browser to be used.
    """

    return os.environ.get('BROWSER', 'zope.testbrowser')


def is_real_browser():
    """Returns `True` if the browser is a real browser.
    Real browsers are phantomjs, webdriver (remote, local).
    """

    if get_browser_driver_name() == 'zope.testbrowser':
        return False
    else:
        return True
