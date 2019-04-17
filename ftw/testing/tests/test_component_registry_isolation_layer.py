from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone.app.testing import IntegrationTesting
from Products.CMFCore.utils import getToolByName
from unittest import TestCase


COMPONENT_REGISTRY_ISOLATION_INTEGRATION = IntegrationTesting(
    bases=(COMPONENT_REGISTRY_ISOLATION, ),
    name="ftw.testing:test_component_registry_isolation_layer:integration")


GENERICSETUP_PROFILE_ZCML = '''
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
    xmlns:i18n="http://namespaces.zope.org/i18n"
    i18n_domain="ftw.testing"
    package="ftw.testing">

    <genericsetup:registerProfile
        name="default"
        title="ftw.testing"
        directory="."
        provides="Products.GenericSetup.interfaces.EXTENSION"
        />

</configure>
'''


class TestComponentRegistryIsolationLayer(TestCase):
    layer = COMPONENT_REGISTRY_ISOLATION_INTEGRATION

    def test_loading_zcml_string(self):
        self.assertFalse(self.profile_exists(),
                         'Component registry is not isolated per test.')
        self.layer['load_zcml_string'](GENERICSETUP_PROFILE_ZCML)
        self.assertTrue(self.profile_exists(),
                        'Failed to register profile.')

    def test_z3c_isolation_works(self):
        # Actually, this should fail here or in "test_loading_zcml_string"
        # because both register the same utility, which should conflict
        # when not teared down properly.
        self.assertFalse(self.profile_exists(),
                         'Component registry is not isolated per test.')
        self.layer['load_zcml_string'](GENERICSETUP_PROFILE_ZCML)
        self.assertTrue(self.profile_exists(),
                        'Failed to register profile.')

    def profile_exists(self):
        portal_setup = getToolByName(self.layer['portal'], 'portal_setup')
        try:
            portal_setup.getProfileInfo('ftw.testing:default')
        except KeyError:
            return False
        else:
            return True
