ftw.testing
===========


This package provides helpers for writing tests.

.. contents:: Table of Contents


MockTestCase
------------

``ftw.testing`` provides an advanced MockTestCase which provides bases on
the `plone.mocktestcase`_ ``MockTestCase``.

.. code:: python

    from ftw.testing import MockTestCase


The following additional methods are available:

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

``self.assertRaises(*args, **kwargs)``
      Uses ``unittest2`` implementation of assertRaises instead of
      ``unittest`` implementation.

It also fixes a problem in ``mock_tool``, where the ``getToolByName`` mock
had assertions which is not very useful in some cases.


Mocking vs. stubbing
--------------------

A **mock** is used for testing the communication between two objects. It
asserts *method calls*. This is used when a test should not test if
a object has a specific state after doing something (e.g. it has it's
attribute *xy* set to something), but if the object *does* something
with another object. If for example an object `Foo` sends an email
when method `bar` is called, we could mock the sendmail object and
assert on the send-email method call.

On the other hand we often have to test the state of an object (attribute
values) after doing something. This can be done without mocks by just
calling the method and asserting the attribute values. But then we have
to set up an integration test and install plone, which takes very long.
For testing an object with dependencies to other parts of plone in a
unit test, we can use **stubs** for faking other (separately tested) parts
of plone. Stubs work like mocks: you can "expect" a method call and
define a result. The difference between **stubs** and **mocks** is that
stubs do not assert the expectations, so there will be no errors if
something expected does not happen. So when using stubs we can assert
the state without asserting the communcation between objects.


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
  from unittest2 import TestCase

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
    from unittest2 import TestCase


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
    from unittest2 import TestCase


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
    from unittest2 import TestCase

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

    from unittest2 import TestCase
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
    from unittest2 import TestCase


    class TestConsoleScripts(TestCase):
        layer = CONSOLE_SCRIPT_TESTING

        def test_executing_command(self):
            exitcode, output = self.layer['execute_script']('my-command args')
            self.assertEqual('something\n', output)

Be aware that the dependency ``zc.recipe.egg`` is required for building the
console scripts. You may put the dependency into your ``tests`` extras require.


Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.2` or `4.3`.


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
