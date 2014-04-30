from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing.z2 import installProduct
from Products.CMFCore.utils import getToolByName
from zope.configuration import xmlconfig


class ZCMLLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def __init__(self,
                 package,
                 is_product=False,
                 autoinclude=True,
                 additional_zcml_packages=(),
                 additional_products=()):

        super(ZCMLLayer, self).__init__()
        self.package = package
        self.is_product = is_product
        self.autoinclude = autoinclude
        self.additional_zcml_packages = additional_zcml_packages
        self.additional_products = additional_products

    def setUpZope(self, app, configurationContext):
        zcml = []

        if self.autoinclude:
            zcml.append(
                '<include package="z3c.autoinclude" file="meta.zcml" />'
                '<includePlugins package="plone" />'
                '<includePluginsOverrides package="plone" />')

        for pkg in self.additional_zcml_packages:
            zcml.append('<include package="%s" />' % pkg)

        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">' +
            ''.join(zcml) +
            '</configure>',
            context=configurationContext)

        if self.is_product:
            installProduct(app, self.package)

        for product in self.additional_products:
            installProduct(app, product)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


def apply_generic_setup_layer(test_class):
    FIXTURE = ZCMLLayer(
        package=test_class.package,
        is_product=test_class.is_product,
        autoinclude=test_class.autoinclude,
        additional_zcml_packages=test_class.additional_zcml_packages,
        additional_products=test_class.additional_products)
    name = 'genericsetup-uninstall:%s' % test_class.__name__
    setattr(test_class, 'layer',
            IntegrationTesting(bases=(FIXTURE,), name=name))
    return test_class


class GenericSetupUninstallMixin(object):
    """This is a test superclass for testing that there is a generic
    setup uninstall profile which does properly reset the configurations
    to a state before the package was installed.
    """

    package = None
    is_product = False
    autoinclude = True
    additional_zcml_packages = ()
    additional_products = ()
    install_dependencies = True
    install_profile_name = 'default'
    skip_files = ()

    def test_uninstall_profile_removes_resets_configuration(self):
        setup_tool = getToolByName(self.layer['portal'], 'portal_setup')
        quick_installer_tool = getToolByName(self.layer['portal'],
                                             'portal_quickinstaller')

        install_profile_id = 'profile-{0}:{1}'.format(
            self.package, self.install_profile_name)

        if self.install_dependencies:
            for profile in setup_tool.getDependenciesForProfile(
                    install_profile_id):
                setup_tool.runAllImportStepsFromProfile(profile)

        setup_tool.createSnapshot('before-install')
        setup_tool.runAllImportStepsFromProfile(install_profile_id,
                                                ignore_dependencies=True)
        quick_installer_tool.uninstallProducts([self.package])
        setup_tool.createSnapshot('after-uninstall')

        before = setup_tool._getImportContext('snapshot-before-install')
        after = setup_tool._getImportContext('snapshot-after-uninstall')

        self.maxDiff = None
        self.assertMultiLineEqual(
            setup_tool.compareConfigurations(
                before, after, skip=self.skip_files),
            '',
            'The uninstall profile seems to not uninstall everything.')
