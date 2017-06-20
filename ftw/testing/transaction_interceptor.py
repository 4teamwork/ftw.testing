from ftw.testing.exceptions import Intercepted
import transaction


class TransactionInterceptor(object):
    """The ``TransactionInterceptor`` patches Zope's transaction manager in
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
    """

    BEGIN = 1
    COMMIT = 2
    ABORT = 4

    def __init__(self):
        self._intercepting = 0
        self._manager = None

    def install(self):
        """Patch the interceptor into Zope's transaction module.
        """
        if isinstance(transaction.manager, type(self)):
            raise Exception('Cannot install TransactionInterceptor,'
                            ' there is already one installed.')

        self._manager = transaction.manager
        transaction.manager = self
        transaction.get = self.get
        transaction.__enter__ = self.get
        transaction.begin = self.begin
        transaction.commit = self.commit
        transaction.abort = self.abort
        transaction.__exit__ = self.__exit__
        transaction.doom = self.doom
        transaction.isDoomed = self.isDoomed
        transaction.savepoint = self.savepoint
        transaction.attempts = self.attempts
        return self

    def uninstall(self):
        """Remove patches.
        """
        transaction.manager = self._manager
        transaction.get = self._manager.get
        transaction.__enter__ = self._manager.get
        transaction.begin = self._manager.begin
        transaction.commit = self._manager.commit
        transaction.abort = self._manager.abort
        transaction.__exit__ = self._manager.__exit__
        transaction.doom = self._manager.doom
        transaction.isDoomed = self._manager.isDoomed
        transaction.savepoint = self._manager.savepoint
        transaction.attempts = self._manager.attempts
        del self._manager
        return self

    def intercept(self, methods):
        if not isinstance(methods, int):
            raise ValueError('Use the binary flags, e.g. interceptor.BEGIN')
        self._intercepting |= methods
        return self

    def clear(self):
        self._intercepting = 0
        return self

    def begin(self):
        if self._intercepting & self.BEGIN:
            raise Intercepted('Not allowed to transaction.begin() at the moment.')
        return self._manager.begin()

    def commit(self):
        if self._intercepting & self.COMMIT:
            raise Intercepted('Not allowed to transaction.commit() at the moment.')
        return self._manager.commit()

    def abort(self):
        if self._intercepting & self.ABORT:
            raise Intercepted('Not allowed to transaction.abort() at the moment.')
        return self._manager.abort()

    def get(self):
        return TransactionWrapper(self._manager.get(), self)

    def __exit__(self, *args, **kwargs):
        return self._manager.__exit__(*args, **kwargs)

    def __getattr__(self, attr):
        if attr in dir(type(self)) or attr in vars(self):
            return object.__getattribute__(self, attr)
        else:
            return self._manager.__getattribute__(attr)


class TransactionWrapper(object):

    def __init__(self, transaction, manager):
        self._transaction = transaction
        self._manager = manager

    def commit(self):
        if self._manager._intercepting & self._manager.COMMIT:
            raise Intercepted('Not allowed to commit transaction at the moment.')
        return self._transaction.commit()

    def abort(self):
        if self._manager._intercepting & self._manager.ABORT:
            raise Intercepted('Not allowed to abort transaction at the moment.')
        return self._transaction.abort()

    def __getattr__(self, attr):
        if attr in dir(type(self)) or attr in vars(self):
            return object.__getattribute__(self, attr)
        else:
            return self._transaction.__getattribute__(attr)
