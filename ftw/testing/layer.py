from plone.testing import Layer
from plone.testing import zca
from zope.component import globalregistry
from zope.configuration import xmlconfig


class ComponentRegistryLayer(Layer):
    """Testing layer used for loading ZCML and keeping the same global
    component registry for all tests. This speeds up the setup.

    It is meant to be subclassed by the implementing layer.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def __init__(self):
        super(ComponentRegistryLayer, self).__init__()
        self._configuration_context = None
        self._adapters = None
        self._utilities = None

    def testSetUp(self):
        base = globalregistry.base
        if self._adapters is None:
            self._adapters = base.adapters
            self._utilities = base.utilities

        else:
            base.adapters = self._adapters
            base.utilities = self._utilities

    def tearDown(self):
        del self['configurationContext']

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
