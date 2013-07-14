from ftw.testing.layer import ComponentRegistryLayer
from ftw.testing.testcase import MockTestCase
import pkg_resources

try:
    pkg_resources.get_distribution('splinter')

except pkg_resources.DistributionNotFound:
    pass

else:
    from ftw.testing.browser import FunctionalSplinterTesting
    from ftw.testing.browser import browser
