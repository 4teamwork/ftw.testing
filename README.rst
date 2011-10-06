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

