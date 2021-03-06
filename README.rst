ftw.testing
===========


This package provides helpers for writing tests.

.. contents:: Table of Contents


IntegrationTesting
------------------

FTWIntegrationTesting layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``FTWIntegrationTesting`` is an opinionated extension of Plone's
default integration testing layer.

The primary goal is to be able to run ``ftw.testbrowser``\s traversal
driver with integration testing.

**Database isolation and transactions**

The Plone default integration testing layer does support transactions:
when changes are committed in tests, no isolation is provided
and the committed changes will apear in the next layer.

- We isolate between tests by making a savepoint in the test setup and
  rolling back to the savepoint in test tear down.
- With a transaction interceptor we make sure that no code in the test
  can commit or abort a transaction. Transactional behavior is simulated
  by using savepoints.


**Usage example:**

.. code:: python

    from ftw.testing import FTWIntegrationTesting
    from plone.app.testing import PLONE_FIXTURE
    from plone.app.testing import PloneSandboxLayer

    class TestingLayer(PloneSandboxLayer):
        defaultBases = (PLONE_FIXTURE,)


    TESTING_FIXTURE = TestingLayer()
    INTEGRATION_TESTING = FTWIntegrationTesting(
        bases=(TESTING_FIXTURE,),
        name='my.package:integration')



FTWIntegrationTestCase
~~~~~~~~~~~~~~~~~~~~~~

The integration test case is an test case base class providing sane defaults
and practical helpers for testing Plone addons with an ``FTWIntegrationTesting``
testing layer.

You may make your own base class in your package, setting the default testing
layer and extending the behavior and helpers for your needs.


**Usage example:**

.. code:: python

    # my/package/tests/test_case.py
    from ftw.testing import FTWIntegrationTestCase
    from my.package.testing import INTEGRATION_TESTING

    class IntegrationTestCase(FTWIntegrationTestCase):
        layer = INTEGRATION_TESTING



MockTestCase
------------

``ftw.testing`` provides an advanced MockTestCase with support for registering
Zope components (utilities, adapters, subscription adapters and event handlers)
from mocks and tearing down the global component registry during test tear-down.
Some functionality was formerly provided by plone.mocktestcase, which is no
longer maintained. Thus it has been copied over into this package. 

.. code:: python

    from ftw.testing import MockTestCase


The following methods are available:

``self.create_dummy(**kw)``
      Return a dummy object that is *not* a mock object, just a dumb object
      with whatever attributes or methods you pass as keyword arguments.
      To make a dummy method, pass a function object or a lambda, e.g.
      self.create_dummy(id="foo", absolute_url=lambda:'http://example.org/foo')

``self.mock_utility(mock, provides, name=u"")```
      Register the given mock object as a global utility providing the given
      interface, with the given name (defaults to the unnamed default utility).

``self.mock_adapter(mock, provides, adapts, name=u"")```
      Register the given mock object as a global adapter providing the given
      interface and adapting the given interfaces, with the given name
      (defaults to the unnamed default adapter).

``self.mock_subscription_adapter(mock, provides, adapts)``
      Register the given mock object as a global subscription adapter providing
      the given interface and adapting the given interfaces.

``self.mock_handler(mock, adapts)``
      Register the given mock object as a global event subscriber for the
      given event types.

``self.mock_tool(mock, name)``
      Create a getToolByName() mock (using 'replace' mode) and configure it so
      that code calling getToolByName(context, name) obtains the given mock
      object. Can be used multiple times: the getToolByName() mock is created
      lazily the first time this method is called in any one test fixture.

``self.providing_mock(interfaces, *args, **kwargs)``
      Creates a mock which provides ``interfaces``.

``self.mock_interface(interface, provides=None, *args, **kwargs)``
      Creates a mock object implementing ``interface``. The mock does not
      only provide ``interface``, but also use it as specification and
      asserts that the mocked methods do exist on the interface.

``self.stub(*args, **kwargs)``
      Creates a stub. It acts like a mock but has no assertions.

``self.providing_stub(interfaces, *args, **kwargs)``
      Creates a stub which provides ``interfaces``.

``self.stub_interface(interface, provides=None, *args, **kwargs)``
      Does the same as ``mock_interface``, but disables counting of expected
      method calls and attribute access. See "Mocking vs. stubbing" below.

``self.set_parent(context, parent_context)``
      Stubs the ``context`` so that its acquisition parent is ``parent_context``.
      Expects at least context to be a mock or a stub. Returns the ``context``.

``self.stub_request(interfaces=[], stub_response=True, content_type='text/html', status=200)``
      Returns a request stub which can be used for rendering templates. With the
      ``stub_response`` option, you can define if the request should stub a
      response by itself. The other optional arguments:
      ``content_type``: Defines the expected output content type of the response.
      ``status``: Defines the expected status code of the response.

``self.stub_response(request=None, content_type='text/html', status=200))``
      Returns a stub response with some headers and options. When a ``request``
      is given the response is also added to the given request.
      The other optional arguments:
      ``content_type``: Defines the expected output content type of the response.
      ``status``: Defines the expected status code of the response.


Component registry layer
------------------------

The ``MockTestCase`` is able to mock components (adapters, utilities). It
cleans up the component registry after every test.

But when we use a ZCML layer, loading the ZCML of the package it should use
the same component registry for all tests on the same layer. The
``ComponentRegistryLayer`` is a layer superclass for sharing the component
registry and speeding up tests.

Usage:

.. code:: python

    from ftw.testing.layer import ComponentRegistryLayer

    class ZCMLLayer(ComponentRegistryLayer):

        def setUp(self):
            super(ZCMLLayer, self).setUp()

            import my.package
            self.load_zcml_file('configure.zcml', my.package)

    ZCML_LAYER = ZCMLLayer()

Be aware that ``ComponentRegistryLayer`` is a base class for creating your
own layer (by subclassing ``ComponentRegistryLayer``) and is not usable with
``defaultBases`` directly. This allows us to use the functions
``load_zcml_file`` and ``load_zcml_string``.


Mailing test helper
-------------------
The Mailing helper object mocks the mailhost and captures sent emails.
The emails can then be easily used for assertions.

Usage:

.. code:: python

    from ftw.testing.mailing import Mailing
    import transaction

    class MyTest(TestCase):
        layer = MY_FUNCTIONAL_TESTING

     def setUp(self):
         Mailing(self.layer['portal']).set_up()
         transaction.commit()

     def tearDown(self):
         Mailing(self.layer['portal']).tear_down()

     def test_mail_stuff(self):
         portal = self.layer['portal']
         do_send_email()
         mail = Mailing(portal).pop()
         self.assertEquals('Subject: ...', mail)


Freezing datetime.now()
-----------------------

When testing code which depends on the current time, it is necessary to set
the current time to a specific time. The ``freeze`` context manager makes that
really easy:

.. code:: python

    from ftw.testing import freeze
    from datetime import datetime

    with freeze(datetime(2014, 5, 7, 12, 30)):
        # test code

The ``freeze`` context manager patches the `datetime` module, the `time` module
and supports the Zope `DateTime` module. It removes the patches when exiting
the context manager.

**Updating the freezed time**

.. code:: python

    from ftw.testing import freeze
    from datetime import datetime

    with freeze(datetime(2014, 5, 7, 12, 30)) as clock:
        # its 2014, 5, 7, 12, 30
        clock.forward(days=2)
        # its 2014, 5, 9, 12, 30
        clock.backward(minutes=15)
        # its 2014, 5, 9, 12, 15


It is possible to ignore modules, so that all calls to date / time functions from
this module are responded with the real current values instead of the frozen ones:

.. code:: python

    from ftw.testing import freeze
    from datetime import datetime

    with freeze(datetime(2014, 5, 7, 12, 30), ignore_modules=['my.package.realtime']):
        pass

You can use the
`timedelta arguments`(https://docs.python.org/2/library/datetime.html#datetime.timedelta)_
for ``forward`` and ``backward``.



Static UUIDS
------------

When asserting UUIDs it can be annoying that they change at each test run.
The ``staticuid`` decorator helps to fix that by using static uuids which
are prefixed and counted within a scope, usually a test case:

.. code:: python

  from ftw.testing import staticuid
  from plone.app.testing import PLONE_INTEGRATION_TESTING
  from unittest import TestCase

  class MyTest(TestCase):
      layer = PLONE_INTEGRATION_TESTING

      @staticuid()
      def test_all_the_things(self):
          doc = self.portal.get(self.portal.invokeFactory('Document', 'the-document'))
          self.assertEquals('testallthethings0000000000000001', IUUID(doc))

      @staticuid('MyUIDS')
      def test_a_prefix_can_be_set(self):
          doc = self.portal.get(self.portal.invokeFactory('Document', 'the-document'))
          self.assertEquals('MyUIDS00000000000000000000000001', IUUID(doc))



Generic Setup uninstall test
----------------------------

``ftw.testing`` provides a test superclass for testing uninstall profiles.
The test makes a Generic Setup snapshot before installing the package, then
installs and uninstalls the package, creates another snapshot and diffs it.
The package is installed without installing its dependencies, because it
should not include uninstalling dependencies in the uninstall profile.

Appropriate testing layer setup is included and the test runs on a seperate
layer which should not interfere with other tests.

Simple example:

.. code:: python

    from ftw.testing.genericsetup import GenericSetupUninstallMixin
    from ftw.testing.genericsetup import apply_generic_setup_layer
    from unittest import TestCase


    @apply_generic_setup_layer
    class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):
        package = 'my.package'


The ``my.package`` is expected to have a Generic Setup profile
``profile-my.package:default`` for installing the package and a
``profile-my.package:uninstall`` for uninstalling the package.
It is expected to use ``z3c.autoinclude`` entry points for loading
its ZCML.

The options are configured as class variables:

**package**
    The dotted name of the package as string, which is used for things such
    as guessing the Generic Setup profile names. This is mandatory.

**autoinclude** (``True``)
    This makes the testing fixture load ZCML using the ``z3c.autoinclude``
    entry points registered for the target ``plone``.

**additional_zcml_packages** (``()``)
    Use this if needed ZCML is not loaded using the ``autoinclude`` option,
    e.g. when you need to load testing zcml. Pass in an iterable of
    dottednames of packages, which contain a ``configure.zcml``.

**additional_products** (``()``)
    A list of additional Zope products to install.

**install_profile_name** (``default``)
    The Generic Setup install profile name postfix.

**skip_files** (``()``)
    An iterable of Generic Setup files (e.g. ``("viewlets.xml",)``) to be
    ignored in the diff. This is sometimes necessary, because not all
    components can and should be uninstalled properly. For example viewlet
    orders cannot be removed using Generic Setup - but this is not a problem
    they do no longer take effect when the viewlets / viewlet managers are
    no longer registered.


Full example:

.. code:: python

    from ftw.testing.genericsetup import GenericSetupUninstallMixin
    from ftw.testing.genericsetup import apply_generic_setup_layer
    from unittest import TestCase


    @apply_generic_setup_layer
    class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):
        package = 'my.package'
        autoinclude = False
        additional_zcml_packages = ('my.package', 'my.package.tests')
        additional_products = ('another.package', )
        install_profile_name = 'default'
        skip_files = ('viewlets.xml', 'rolemap.xml')


Disabling quickinstaller snapshots
----------------------------------

Quickinstaller normally makes a complete Generic Setup (GS) snapshot
before and after installing each GS profile, in order to be able to
uninstall the profile afterwards.

In tests we usually don't need this feature and want to disable it to
speed up tests.

The ``ftw.testing.quickinstaller`` module provides a patcher for
replacing the quickinstaller event handlers to skip creating snapshots.
Usually we want to do this early (when loading ``testing.py``), so that
all the tests are speeding up.
However, some tests which involve quickinstaller rely on having the
snapshots made (see previous section about uninstall tests).
Therefore the snapshot patcher object provides context managers for
temporarily enabling / disabling the snapshot feature.

Usage:

Disable snapshots early, so that everything is fast. Usually this is
done in the ``testing.py`` in module scope, so that it happens already
when the testrunner imports the tests:

.. code:: python

  from ftw.testing.quickinstaller import snapshots
  from plone.app.testing import PloneSandboxLayer

  snapshots.disable()

  class MyPackageLayer(PloneSandboxLayer):
  ...

When testing quickinstaller snapshot related things, such as uninstalling,
the snapshots can be re-enabled for a context manager or in general:

.. code:: python

  from ftw.testing.quickinstaller import snapshots

  snapshots.disable()
  # snapshotting is now disabled

  with snapshots.enabled():
      # snapshotting is enabled only within this block

  snapshots.enable()
  # snapshotting is now enabled

  with snapshots.disabled():
      # snapshotting is disabled only within this block


Transaction interceptor
-----------------------

The ``TransactionInterceptor`` patches Zope's transaction manager in
order to prevent code from interacting with the transaction.

This can be used for example for making sure that no tests commit transactions
when they are running on an integration testing layer.

The interceptor needs to be installed manually with ``install()`` and removed
at the end with ``uninstall()``. It is the users responsibility to ensure
proper uninstallation.

When the interceptor is installed, it is not yet active and passes through all
calls.
The intercepting begins with ``intercept()`` and ends when ``clear()`` is
called.

.. code:: python

    from ftw.testing import TransactionInterceptor

    interceptor = TransactionInterceptor().install()
    try:
        interceptor.intercept(interceptor.BEGIN | interceptor.COMMIT
                              | interceptor.ABORT)
        # ...
        interceptor.clear()
        transaction.abort()
    finally:
        interceptor.uninstall()


Testing Layers
--------------

Component registry isolation layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``plone.app.testing``'s default testing layers (such as ``PLONE_FIXTURE``) do not
isolate the component registry for each test.

``ftw.testing``'s ``COMPONENT_REGISTRY_ISOLATION`` testing layer isolates the
component registry for each test, provides a stacked ZCML configuration context
and provides the methods ``load_zcml_string`` and ``load_zcml_file`` for loading
ZCML.

Example:

.. code:: python

    # testing.py
    from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
    from plone.app.testing import IntegrationTesting
    from plone.app.testing import PloneSandboxLayer
    from zope.configuration import xmlconfig


    class MyPackageLayer(PloneSandboxLayer):
        defaultBases = (COMPONENT_REGISTRY_ISOLATION,)

        def setUpZope(self, app, configurationContext):
            import my.package
            xmlconfig.file('configure.zcml', ftw.package,
                           context=configurationContext)

    MY_PACKAGE_FIXTURE = MyPackageLayer()
    MY_PACKAGE_INTEGRATION = IntegrationTesting(
        bases=(MY_PACKAGE_FIXTURE,
               COMPONENT_REGISTRY_ISOLATION),
        name='my.package:integration')


    # ----------------------------
    # test_*.py
    from unittest import TestCase

    class TestSomething(TestCase):
        layer = MY_PACKAGE_INTEGRATION

        def test(self):
            self.layer['load_zcml_string']('<configure>...</configure>')


Temp directory layer
~~~~~~~~~~~~~~~~~~~~

The ``TEMP_DIRECTORY`` testing layer creates an empty temp directory for
each test and removes it recursively on tear down.

The path to the directory can be accessed with the ``temp_directory`` key.

Usage example:

.. code:: python

    from unittest import TestCase
    from ftw.testing.layer import TEMP_DIRECTORY


    class TestSomething(TestCase):
        layer = TEMP_DIRECTORY

        def test(self):
            path = self.layer['temp_directory']


Console script testing layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The console script layer helps testing console scripts.
On layer setup it creates and executes an isolated buildout with the package under
development, which creates all console scripts of this package.
This makes it easy to test console scripts by really executing them.

Usage example:

.. code:: python

    # testing.py
    from ftw.testing.layer import ConsoleScriptLayer

    CONSOLE_SCRIPT_TESTING = ConsoleScriptLayer('my.package')


    # test_*.py
    from my.package.testing import CONSOLE_SCRIPT_TESTING
    from unittest import TestCase


    class TestConsoleScripts(TestCase):
        layer = CONSOLE_SCRIPT_TESTING

        def test_executing_command(self):
            exitcode, output = self.layer['execute_script']('my-command args')
            self.assertEqual('something\n', output)

Be aware that the dependency ``zc.recipe.egg`` is required for building the
console scripts. You may put the dependency into your ``tests`` extras require.


Upgrading
---------

Upgrading from ftw.testing 1.x to 2.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``mocker`` has been replaced in favor of ``unittest.mock``.
This is a `breaking` change and may require amending existing tests based on
``MockTestCase``.

With ``mocker`` expectations were recorded in `record` mode while using the
mock in tests was done in `replay` mode. This is no longer the case with
``unittest.mock``. Here's a simple example how expectations can be adopted:

.. code:: python

  # Mocking with mocker
  mock = self.mocker.mock()  # mocker.Mock
  self.expect(mock.lock()).result('already locked')
  self.replay()
  self.assertEqual(mock.lock(), 'already locked')


.. code:: python

  # Mocking with unittest.mock
  mock = self.mock()  # unittest.mock.Mock
  mock.lock.return_value = 'already locked'
  self.assertEqual(mock.lock(), 'already locked')


Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.3`, `5.1` and `5.2`.


Links
-----

- Github: https://github.com/4teamwork/ftw.testing
- Issues: https://github.com/4teamwork/ftw.testing/issues
- Pypi: http://pypi.python.org/pypi/ftw.testing
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.testing


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.testing`` is licensed under GNU General Public License, version 2.





.. _plone.mocktestcase: http://pypi.python.org/pypi/plone.mocktestcase
.. _Splinter: https://pypi.python.org/pypi/splinter
