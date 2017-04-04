from ftw.testing.freezer import freeze
from ftw.testing.layer import ComponentRegistryLayer
from ftw.testing.staticuids import staticuid
from ftw.testing.testcase import MockTestCase
import pkg_resources

try:
    pkg_resources.get_distribution('splinter')

except pkg_resources.DistributionNotFound:
    pass

else:
    from ftw.testing.browser import FunctionalSplinterTesting
    from ftw.testing.browser import browser


IS_PLONE_5 = pkg_resources.get_distribution('Plone').version >= '5'
