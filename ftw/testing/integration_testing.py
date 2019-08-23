from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from ftw.testing.transaction_interceptor import TransactionInterceptor
from functools import wraps
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import SITE_OWNER_NAME
from six.moves import filter
from unittest import TestCase
import timeit
import transaction


class FTWIntegrationTesting(IntegrationTesting):
    """An extended integration testing layer class, extending the Plone
    default integration testing with opinionated behavior.

    DATABASE ISOLATION AND TRANSACTIONS
    The Plone default integration testing layer does support transactions:
    when changes are committed in tests, no isolation is provided
    and the committed changes will apear in the next layer.

    - We isolate between tests by making a savepoint in the test setup and
      rolling back to the savepoint in test tear down.
    - With a transaction interceptor we make sure that no code in the test
      can commit or abort a transaction. Transactional behavior is simulated
      by using savepoints.
    """

    def setUp(self):
        super(FTWIntegrationTesting, self).setUp()
        transaction.commit()
        self.interceptor = TransactionInterceptor().install()

    def tearDown(self):
        self.interceptor.uninstall()
        super(FTWIntegrationTesting, self).tearDown()

    def testSetUp(self):
        super(FTWIntegrationTesting, self).testSetUp()
        self.makeSavepoint()
        self.interceptor.intercept(self.interceptor.BEGIN |
                                   self.interceptor.COMMIT |
                                   self.interceptor.ABORT)
        self.interceptor.begin_savepoint_simulation()
        self.interceptor.begin()

    def testTearDown(self):
        self.interceptor.stop_savepoint_simulation()
        self.rollbackSavepoint()
        self.interceptor.clear().intercept(self.interceptor.COMMIT)
        super(FTWIntegrationTesting, self).testTearDown()

    def makeSavepoint(self):
        self.savepoint = transaction.savepoint()

    def rollbackSavepoint(self):
        self.savepoint.rollback()
        self.savepoint = None


class FTWIntegrationTestCase(TestCase):
    """An opinionated test case which works well with the FTWIntegrationTesting
    layer.

    This class may be subclassed as baseclass and extended with a testing layer
    and custom behavior:

    .. code:: python

    class IntegrationTestCase(FTWIntegrationTestCase):
        layer = MY_PACKAGE_INTEGRATION_TESTING
    """

    logout_by_default = True

    def setUp(self):
        super(FTWIntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        if self.logout_by_default:
            logout()

    @staticmethod
    def clock(func):
        """Decorator for measuring the duration of a test and printing the result.
        This function is meant to be used temporarily in development.

        Example:

        >>> @FTWIntegrationTestCase.clock
        ... def test_something(self):
        ...     pass
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            timer = timeit.default_timer
            start = timer()
            try:
                return func(self, *args, **kwargs)
            finally:
                end = timer()
                print('')
                print('{}.{} took {:.3f} ms'.format(
                    type(self).__name__,
                    func.__name__,
                    (end - start) * 1000))
        return wrapper

    def login(self, user, browser=None):
        """Login a user by setting the security manager.

        The login method logs in a user by creating a new security manager
        with this user.
        The ``user`` may be a userid or a user object.

        >>> self.login(acl_users.getUserById('john.doe'))
        >>> self.login('john.doe')

        The optional ``browser`` keyword argument allows to pass in an
        ``ftw.testbrowser`` browser instance, which will be logged in with
        the same user.

        >>> self.login(user_object, browser=browser)

        When the method is used as context manager, the prior security manager
        will be restored on exit:

        >>> with self.login(admin):
        ...     do_something_as_admin()

        :param user: A user object or a user name.
        :type user: string or user object
        :param browser: A ``ftw.testbrowser`` instance to log in too.
        :type browser: :py:class:`ftw.testbrowser.core.Browser`
        """

        if hasattr(user, 'getUserName'):
            userid = user.getUserName()
        else:
            userid = user

        security_manager = getSecurityManager()
        if userid == SITE_OWNER_NAME:
            login(self.layer['app'], userid)
        else:
            login(self.portal, userid)

        if browser is not None:
            browser_auth_headers = [
                item for item in browser.session_headers
                if item[0] == 'Authorization'
            ]
            browser.login(userid)

        @contextmanager
        def login_context_manager():
            try:
                yield
            finally:
                setSecurityManager(security_manager)
                if browser is not None:
                    browser.clear_request_header('Authorization')
                    [browser.append_request_header(name, value)
                     for (name, value) in browser_auth_headers]

        return login_context_manager()

    @contextmanager
    def observe_children(self, obj, check_security=True):
        """Observe the children of an object for testing that children were
        added or removed within the context manager.

        :param obj: The container to observe.
        :type obj: Plone object.
        :param check_security: Only report children allowed to access.
        :type check_security: bool
        :returns: A dict which will be updated with result when leaving the
          context manager.
        :rtype: dict
        """
        if check_security:
            def allowed(obj):
                return getSecurityManager().checkPermission(
                    'Access contents information', obj)
        else:
            def allowed(obj):
                return True

        children = {'before': list(filter(allowed, obj.objectValues()))}
        yield children
        children['after'] = list(filter(allowed, obj.objectValues()))
        children['added'] = set(children['after']) - set(children['before'])
        children['removed'] = set(children['before']) - set(children['after'])
