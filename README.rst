ftw.testing
===========


This package provides helpers for writing tests.

.. figure:: http://onegov.ch/approved.png/image
   :align: right
   :target: http://onegov.ch/community/zertifizierte-module/ftw.testing

   Certified: 01/2013

.. contents:: Table of Contents


Browser testing with splinter
-----------------------------

`Splinter`_ is a library which provides a common browser API with a driver
for `zope.testbrowser`.

The `ftw.testing` package provides integration of `Splinter`_ with Plone
using Page Objects.

For using the splinter features, use the `splinter` extras require::

    ftw.testing [splinter]


Setting a package up for browser tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's easy to setup your package for browser tests:

- Add a test-dependency to `ftw.testing` in your `setup.py`:

.. code:: python

    tests_require = [
        'ftw.testing[splinter]',
        ]

    setup(name='my.package',
          ...
          tests_require=tests_require,
          extras_require=dict(tests=tests_require),
          )

- In your `testing.py` use the `FunctionalSplinterTesting` layer wrapper:

.. code:: python

    from ftw.testing import FunctionalSplinterTesting
    from plone.app.testing import PLONE_FIXTURE
    from plone.app.testing import PloneSandboxLayer
    from plone.app.testing import applyProfile
    from zope.configuration import xmlconfig


    class MyPackageLayer(PloneSandboxLayer):

        defaultBases = (PLONE_FIXTURE,)

        def setUpZope(self, app, configurationContext):
            import my.package
            xmlconfig.file('configure.zcml', my.package)

        def setUpPloneSite(self, portal):
            applyProfile(portal, 'my.package:default')


    MY_PACKAGE_FIXTURE = MyPackageLayer()
    MY_PACKAGE_FUNCTIONAL_TESTING = FunctionalSplinterTesting(
        bases=(MY_PACKAGE_FIXTURE, ),
        name="my.package:functional")

- Write tests using the Plone Page Objects:

.. code:: python

    from ftw.testing import browser
    from ftw.testing.pages import Plone
    from my.package.testing import MY_PACKAGE_FUNCTIONAL_TESTING
    from plone.app.testing import SITE_OWNER_NAME
    from plone.app.testing import SITE_OWNER_PASSWORD
    from unittest2 import TestCase


    class TestDocument(TestCase):

        layer = MY_PACKAGE_FUNCTIONAL_TESTING

        def test_add_document(self):
            Plone().login(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
            Plone().visit_portal()
            Plone().create_object('Page', {'Title': 'Foo',
                                           'Body Text': '<b>Hello World</b>'})
            self.assertTrue(browser().is_text_present('Hello World'))


Writing Page Objects
~~~~~~~~~~~~~~~~~~~~

Write your own Page Objects for your views and content types.
Put a module `pages.py` in your tests folder:

.. code:: python

    from ftw.testing.pages import Plone


    class MyContentType(Plone):

        def create_my_content(self, title, text):
            self.create_object('MyContent', {'Title': title,
                                             'Body Text': text})
            return self

The Page Object should have methods for all features of your view.



Using the Plone Page Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Plone page object provided by `ftw.testing` already has the most
important features built in, such as:

- portal_url handling
- Login
- Accessing Headings, <body>-CSS-classes, status messages
- Adding content
- TinyMCE handling

Currently it's best to just look in the
`page object code <https://github.com/4teamwork/ftw.testing/blob/master/ftw/testing/pages.py>`_.



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

    from ftw.testing.pages import Mailing
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


Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.1`, `4.2` or `4.3`.


Links
-----

- Main github project repository: https://github.com/4teamwork/ftw.testing
- Issue tracker: https://github.com/4teamwork/ftw.testing/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.testing
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.testing


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.testing`` is licensed under GNU General Public License, version 2.





.. _plone.mocktestcase: http://pypi.python.org/pypi/plone.mocktestcase
.. _Splinter: https://pypi.python.org/pypi/splinter

.. image:: https://cruel-carlota.pagodabox.com/fbb27e21f06d795e60173da59259a1a6
   :alt: githalytics.com
   :target: http://githalytics.com/4teamwork/ftw.testing
