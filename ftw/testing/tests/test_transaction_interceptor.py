from ftw.testing import TransactionInterceptor
from ftw.testing.exceptions import Intercepted
from ftw.testing.testing import FTW_TESTING_FUNCTIONAL
from unittest2 import TestCase
import transaction


class TestTransactionInterceptor(TestCase):
    layer = FTW_TESTING_FUNCTIONAL

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
