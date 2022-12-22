from ftw.testing.freezer import freeze
from ftw.testing.integration_testing import FTWIntegrationTestCase
from ftw.testing.integration_testing import FTWIntegrationTesting
from ftw.testing.layer import ComponentRegistryLayer
from ftw.testing.staticuids import staticuid
from ftw.testing.testcase import MockTestCase
from ftw.testing.transaction_interceptor import TransactionInterceptor
from Products.CMFPlone.utils import getFSVersionTuple
import pkg_resources


IS_PLONE_5 = pkg_resources.get_distribution('Products.CMFPlone').version >= '5'
PLONE_VERSION = getFSVersionTuple()