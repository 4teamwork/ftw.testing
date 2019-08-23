from contextlib import contextmanager
from Products.CMFQuickInstallerTool import events
import inspect


def noop_event_handler(event):
    """An event handler that does nothing.
    """


class QuickInstallerSnapshots(object):
    """Patches Products.CMFQuickInstallerTool:
    Removes the quickinstaller's subscribers to GenericSetup events
    which create snapshots for each installed profile.

    The snapshots are used for uninstalling products, which is usually
    not done in tests.

    Creating the snapshots consume quite a lot of time.
    Disabling it speeds up the testing layer setup time.
    """

    def __init__(self):
        self._current_version = 'original'
        self._functions = {}

        self._prepare(events.handleBeforeProfileImportEvent,
                      noop_event_handler)
        self._prepare(events.handleProfileImportedEvent, noop_event_handler)

    def is_enabled(self):
        """Returns ``True`` when snapshots are
        enabled (original implementation).
        """
        return self._current_version == 'original'

    def disable(self):
        """Disable quickinstaller snapshots in general.
        """
        self._apply('noop')

    def enable(self):
        """Enable quickinstaller snapshots in general, when disabled.
        """
        self._apply('original')

    @contextmanager
    def disabled(self):
        """While in this context manager, snapshots are disabled.
        """
        if self.is_enabled():
            self.disable()
            try:
                yield
            finally:
                self.enable()
        else:
            yield

    @contextmanager
    def enabled(self):
        """While in this context manager, snapshots are enabled.
        """
        if not self.is_enabled():
            self.enable()
            try:
                yield
            finally:
                self.disable()
        else:
            yield

    def _apply(self, version):
        if self._current_version == version:
            return

        self._current_version = version
        for dottedname, info in self._functions.items():
            print('ftw.testing PATCHING: {0} with {1}'.format(
                dottedname, version))
            info['function'].__code__ = info[version]

    def _prepare(self, func, replacement):
        dottedname = '.'.join((func.__module__, func.__name__))
        original_code = func.__code__
        replacement_source = inspect.getsource(replacement)
        exec(replacement_source, func.__globals__)
        replacement_code = func.__globals__[replacement.__name__].__code__

        self._functions[dottedname] = {'original': original_code,
                                       'noop': replacement_code,
                                       'function': func}


snapshots = QuickInstallerSnapshots()
