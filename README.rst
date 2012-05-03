ftw.testing
===========


This package provides helpers for writing tests.


MockTestCase
------------

``ftw.testing`` provides an advanced MockTestCase which provides bases on
the `plone.mocktestcase`_ ``MockTestCase``.

::

    >>> from ftw.testing import MockTestCase


The following additional methos are available:

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
      Stubs the ``context`` so that its acquision parent is ``parent_context``.
      Expects at least context to be a mock or a stub. Returns the ``context``.

``self.stub_request(interfaces=[], stub_response=True,
                     content_type='text/html', status=200)``
      Returns a request stub which can be used for rendering templates. With the
      ``stub respones`` option, you can define if the request should stub a
      response by him self. The other optional arguments:
      ``content_type``: Defines the expected output content type of the response.
      ``status``: Defines the expected status code of the response.

``self.stub_response(request=None, content_type='text/html', status=200))``
      Returns a stub response with some headers and options. When a ``request``
      is given the response would append also to the giver request.
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
with another object when. If for example a object `Foo` sends a email
when method `bar` is called, we could mock the sendmail object and
assert on the send-email method call.

On the other hand we often have to test the state of a object (attribute
values) after doing something. This can be done without mocks by just
calling the method and asserting the attribute values. But then we have
to set up an integration test and install plone, which takes very long.
For testing an object with dependencies to other parts of plone in a
unit test, we can use **stubs** for faking other (seperately tested) parts
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


Links
-----

- Main github project repository: https://github.com/4teamwork/ftw.testing
- Issue tracker: https://github.com/4teamwork/ftw.testing/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.testing


Maintainer
----------

This package is produced and maintained by `4teamwork <http://www.4teamwork.ch/>`_ company.




.. _plone.mocktestcase: http://pypi.python.org/pypi/plone.mocktestcase
