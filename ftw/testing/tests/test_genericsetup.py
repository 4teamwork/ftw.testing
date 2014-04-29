from ftw.testing.genericsetup import GenericSetupUninstallMixin
from ftw.testing.genericsetup import apply_generic_setup_layer
from unittest2 import TestCase


@apply_generic_setup_layer
class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.testing.tests'
    additional_zcml_packages = ('ftw.testing.tests',)

    # The test_testcase.TestToolMocking relies on
    # Products.PloneHotfix20121106 to be not imported before running
    # the test. Autoinclude would import it, therefore we do not use
    # autoinclude here, since we are importing ZCML with
    # additional_zcml_packages anyways.
    autoinclude = False
