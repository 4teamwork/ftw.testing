from ftw.testing import TransactionInterceptor
from ftw.testing.exceptions import Intercepted
from ftw.testing.testing import FTW_TESTING_FUNCTIONAL
from unittest import TestCase
import transaction


class TestTransactionInterceptor(TestCase):
    layer = FTW_TESTING_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']

    def tearDown(self):
        if hasattr(transaction.manager, 'uninstall'):
            transaction.manager.uninstall()

    def test_intercept_begin(self):
        transaction.begin()  # not intercepted

        interceptor = TransactionInterceptor().install()
        transaction.begin()  # not intercepted

        interceptor.intercept(interceptor.BEGIN)
        with self.assertRaises(Intercepted) as cm:
            transaction.begin()  # intercepted

        self.assertEquals('Not allowed to transaction.begin() at the moment.',
                          str(cm.exception))

        interceptor.clear()
        transaction.begin()  # not intercepted

        interceptor.uninstall()
        transaction.begin()  # not intercepted

    def test_intercept_commit(self):
        transaction.commit()  # not intercepted

        interceptor = TransactionInterceptor().install()
        transaction.commit()  # not intercepted

        interceptor.intercept(interceptor.COMMIT)
        with self.assertRaises(Intercepted) as cm:
            transaction.commit()  # intercepted

        self.assertEquals('Not allowed to transaction.commit() at the moment.',
                          str(cm.exception))

        interceptor.clear()
        transaction.commit()  # not intercepted

        interceptor.uninstall()
        transaction.commit()  # not intercepted

    def test_intercept_abort(self):
        transaction.abort()  # not intercepted

        interceptor = TransactionInterceptor().install()
        transaction.abort()  # not intercepted

        interceptor.intercept(interceptor.ABORT)
        with self.assertRaises(Intercepted) as cm:
            transaction.abort()  # intercepted

        self.assertEquals('Not allowed to transaction.abort() at the moment.',
                          str(cm.exception))

        interceptor.clear()
        transaction.abort()  # not intercepted

        interceptor.uninstall()
        transaction.abort()  # not intercepted

    def test_intercept_multiple_methods_in_one_call(self):
        interceptor = TransactionInterceptor().install()
        transaction.begin()
        transaction.commit()
        transaction.abort()

        interceptor.intercept(interceptor.COMMIT | interceptor.ABORT)
        transaction.begin()
        with self.assertRaises(Intercepted):
            transaction.commit()
        with self.assertRaises(Intercepted):
            transaction.abort()

        interceptor.uninstall()

    def test_intercept_multiple_methods_by_extending(self):
        interceptor = TransactionInterceptor().install()
        transaction.begin()
        transaction.commit()
        transaction.abort()

        interceptor.intercept(interceptor.COMMIT)
        interceptor.intercept(interceptor.ABORT)
        transaction.begin()
        with self.assertRaises(Intercepted):
            transaction.commit()
        with self.assertRaises(Intercepted):
            transaction.abort()

        interceptor.uninstall()

    def test_intercepts_on_transaction(self):
        interceptor = TransactionInterceptor().install()
        interceptor.intercept(interceptor.COMMIT | interceptor.ABORT)

        txn = transaction.get()
        with self.assertRaises(Intercepted):
            txn.commit()
        with self.assertRaises(Intercepted):
            txn.abort()

    def test_not_installable_twice(self):
        TransactionInterceptor().install()
        with self.assertRaises(Exception) as cm:
            TransactionInterceptor().install()

        self.assertEqual('Cannot install TransactionInterceptor,'
                         ' there is already one installed.',
                         str(cm.exception))

    def test_savepoint_simulation_abort(self):
        """Aborting in savepoint simulation rolls back to the last begin state.
        """
        self.portal.foo = 'One'
        interceptor = TransactionInterceptor().install()
        interceptor.begin_savepoint_simulation()
        transaction.begin()
        self.portal.foo = 'Two'
        self.assertEquals('Two', self.portal.foo)

        transaction.abort()
        self.assertEquals('One', self.portal.foo)

    def test_savepoint_simulation_abort_without_begin(self):
        """An error occurs when aborting without beginning.
        """
        interceptor = TransactionInterceptor().install()
        interceptor.begin_savepoint_simulation()
        with self.assertRaises(Intercepted):
            interceptor.abort()

    def test_savepoint_simulation_commit(self):
        """Committing in savepoint simulation does not commit nor fail.
        """
        self.portal.foo = 'One'
        interceptor = TransactionInterceptor().install()
        interceptor.begin_savepoint_simulation()
        transaction.begin()
        self.portal.foo = 'Two'
        self.assertEquals('Two', self.portal.foo)
        transaction.commit()
        self.assertEquals('Two', self.portal.foo)

        interceptor.uninstall()
        transaction.begin()  # reset to actual committed state
        self.assertFalse(hasattr(self.portal, 'foo'))

    def test_savepoint_simulation_commit_without_begin(self):
        """An error occurs when commiting without beginning.
        """
        interceptor = TransactionInterceptor().install()
        interceptor.begin_savepoint_simulation()
        with self.assertRaises(Intercepted):
            interceptor.commit()

    def test_savepoint_simulation_two_begins(self):
        """A begin should abort existing transactions when there is one.
        """
        self.portal.foo = 'One'
        interceptor = TransactionInterceptor().install()
        interceptor.begin_savepoint_simulation()
        transaction.begin()
        self.portal.foo = 'Two'
        self.assertEquals('Two', self.portal.foo)
        transaction.begin()
        self.assertEquals('One', self.portal.foo)

    def test_savepoint_simulation_while_intercepting(self):
        """When the interceptor is configured to intercept, it will
        keep intercepting after an intermediate savepoint simulation is stopped.
        """
        interceptor = TransactionInterceptor().install()
        interceptor.intercept(interceptor.COMMIT)

        interceptor.begin_savepoint_simulation()
        transaction.begin()
        transaction.commit()
        interceptor.stop_savepoint_simulation()

        with self.assertRaises(Intercepted):
            transaction.commit()

    def test_savepoint_simulation_as_context_manager(self):
        interceptor = TransactionInterceptor().install()
        interceptor.intercept(interceptor.COMMIT)

        with interceptor.savepoint_simulation():
            transaction.begin()
            transaction.commit()

        with self.assertRaises(Intercepted):
            transaction.commit()

    def test_savepoint_simulation_resets_savepoint_on_exit(self):
        interceptor = TransactionInterceptor().install()
        interceptor.intercept(interceptor.COMMIT)

        with interceptor.savepoint_simulation():
            transaction.begin()
            self.assertTrue(interceptor._savepoint)

        self.assertIsNone(interceptor._savepoint)
