from ftw.testing.browser import set_browser_driver
from ftw.testing.browser import shutdown_all_browser
from ftw.testing.browser import shutdown_browser
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing.layers import FunctionalTesting
from plone.testing import Layer
from plone.testing import z2
from plone.testing import zca
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser
from splinter.browser import _DRIVERS
from splinter.driver.zopetestbrowser import ZopeTestBrowser
from zope.configuration import xmlconfig
import zope.component.testing


class ComponentRegistryLayer(Layer):
    """Testing layer used for loading ZCML and keeping the same global
    component registry for all tests. This speeds up the setup.

    It is meant to be subclassed by the implementing layer.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def __init__(self):
        super(ComponentRegistryLayer, self).__init__()
        self._configuration_context = None

    def setUp(self):
        zca.pushGlobalRegistry()

    def testSetUp(self):
        zca.pushGlobalRegistry()

    def testTearDown(self):
        zca.popGlobalRegistry()

    def tearDown(self):
        zca.popGlobalRegistry()
        if hasattr(self, 'configurationContext'):
            del self['configurationContext']
        zope.component.testing.tearDown(self)

    def load_zcml_file(self, filename, module):
        xmlconfig.file(filename, module,
                       context=self._get_configuration_context())

    def load_zcml_string(self, zcml):
        xmlconfig.string(zcml, context=self._get_configuration_context())

    def _get_configuration_context(self):
        if self._configuration_context is None:
            self._configuration_context = zca.stackConfigurationContext(
                self.get('configurationContext'))
            self['configurationContext'] = self._configuration_context
        return self._configuration_context


class FunctionalSplinterTesting(FunctionalTesting):

    defaultBases = ()

    def __init__(self, bases=None, name=None, module=None):
        # We need to make sure that we open the ZSERVER port
        # by using the PLONE_ZSERVER layer.
        if not bases:
            bases = self.defaultBases
        bases = bases + (PLONE_ZSERVER, )

        super(FunctionalSplinterTesting, self).__init__(
            bases=bases, name=name, module=module)

    def testSetUp(self):
        super(FunctionalSplinterTesting, self).testSetUp()
        # The default browser is zope.testbrowser.
        # The browser may be changed later using decorators.
        set_browser_driver('zope.testbrowser')

    def testTearDown(self):
        shutdown_browser()
        super(FunctionalSplinterTesting, self).testTearDown()

    def tearDown(self):
        shutdown_all_browser()
        super(FunctionalSplinterTesting, self).tearDown()


class PloneZopeTestBrowser(ZopeTestBrowser):

    def _get_mech_browser(self, user_agent):
        with z2.zopeApp() as app:
            return Zope2MechanizeBrowser(app)


_DRIVERS['zope.testbrowser'] = PloneZopeTestBrowser
