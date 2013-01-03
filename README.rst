ftw.testing
===========


This package provides helpers for writing tests.

.. figure:: http://onegov.ch/approved.png/image
   :align: right
   :target: http://onegov.ch/community/zertifizierte-module/ftw.testing

   Certified: 01/2013


MockTestCase
------------

``ftw.testing`` provides an advanced MockTestCase which provides bases on
the `plone.mocktestcase`_ ``MockTestCase``.

::

    >>> from ftw.testing import MockTestCase


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

Usage::

    >>> from ftw.testing.layer import ComponentRegistryLayer
    >>>
    >>> class ZCMLLayer(ComponentRegistryLayer):
    ...
    ...     def setUp(self):
    ...         super(ZCMLLayer, self).setUp()
    ...
    ...         import my.package
    ...         self.load_zcml_file('configure.zcml', my.package)
    ...
    ... ZCML_LAYER = ZCMLLayer()

Be aware that ``ComponentRegistryLayer`` is a base class for creating your
own layer (by subclassing ``ComponentRegistryLayer``) and is not usable with
``defaultBases`` directly. This allows us to use the functions
``load_zcml_file`` and ``load_zcml_string``.


Robot framework testing
-----------------------

For loading the needed dependencies for robot testing, just add a dependency
to `ftw.testing[robot]`. You may also want `plone.act`_ for plone specific
keywords.

**Translations**

Use the ``LocalizedRobotLayer`` for using robot framework in another language::

    >>> from ftw.testing import LocalizedRobotLayer
    >>> from plone.testing import Layer
    >>>
    >>> class MyPackage(Layer):
    ...
    ...     defaultBases = (LocalizedRobotLayer(['de']),)
    ...
    ... MY_PACKAGE = MyPackage()



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
.. _plone.act: https://github.com/plone/plone.act
