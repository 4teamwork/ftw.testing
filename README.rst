Introduction
============


This package provides helpers for writing tests.


MockTestCase
------------

`ftw.testing` provides an advanced MockTestCase which provides bases on
the `plone.mocktestcase`_ `MockTestCase`.

    >>> from ftw.testing import MockTestCase


The following additional methos are available:

    self.providing_mock(interfaces, *args, **kwargs)
      Creates a mock which provides `interfaces`.

    self.stub(*args, **kwargs)
      Creates a stub. It acts like a mock but has no assertions.

    self.providing_stub(interfaces, *args, **kwargs)
      Creates a stub which provides `interfaces`.

    self.set_parent(context, parent_context)
      Stubs the `context` so that its acquision parent is `parent_context`.
      Expects at least context to be a mock or a stub. Returns the `parent_context`.
