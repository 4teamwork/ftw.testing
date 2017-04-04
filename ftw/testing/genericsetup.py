from datetime import datetime
from ftw.testing import IS_PLONE_5
from ftw.testing.quickinstaller import snapshots
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import installProduct
from Products.CMFCore.utils import getToolByName
from Products.CMFQuickInstallerTool.InstalledProduct import InstalledProduct
from zope.component import getUtility
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

        installProduct(app, self.package)
        for product in self.additional_products:
            installProduct(app, product)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


def apply_generic_setup_layer(test_class):
    FIXTURE = ZCMLLayer(
        package=test_class.package,
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
    autoinclude = True
    additional_zcml_packages = ()
    additional_products = ()
    install_dependencies = True
    install_profile_name = 'default'
    skip_files = ()

    datetime = datetime.now()

    def _make_profile_name(self, name):
        return 'profile-{0}:{1}'.format(self.package, name)

    @property
    def uninstall_profile_id(self):
        return self._make_profile_name('uninstall')

    @property
    def install_profile_id(self):
        return self._make_profile_name(self.install_profile_name)

    @property
    def setup_tool(self):
        if not hasattr(self, '_setup_tool'):
            self._setup_tool = getToolByName(self.layer['portal'],
                                             'portal_setup')
        return self._setup_tool

    def _install_dependencies(self):
        if self.install_dependencies:
            for profile in self.setup_tool.getDependenciesForProfile(
                    self.install_profile_id):
                self.setup_tool.runAllImportStepsFromProfile(profile)

    def _install_package(self):
        self.setup_tool.runAllImportStepsFromProfile(self.install_profile_id,
                                                     ignore_dependencies=True)

    def _quickinstaller_uninstall_package(self):
        quick_installer_tool = getToolByName(self.layer['portal'],
                                             'portal_quickinstaller')
        quick_installer_tool.uninstallProducts([self.package])

    def _setuptool_uninstall_package(self):
        self.setup_tool.runAllImportStepsFromProfile(self.uninstall_profile_id)

    def _create_before_snapshot(self, id_='before-install'):
        self._prepare_registry()
        self.setup_tool.createSnapshot(id_)

    def _create_after_shapshot(self, id_='after-uninstall'):
        self._prepare_registry()
        self.setup_tool.createSnapshot(id_)

    def _prepare_registry(self):
        if IS_PLONE_5:
            registry = getUtility(IRegistry)
            registry.records['plone.resources.last_legacy_import'].value = self.datetime
            registry.records['plone.bundles/plone-legacy.last_compilation'].value = self.datetime
        
    def assertSnapshotsEqual(self, before_id='before-install',
                             after_id='after-uninstall',
                             msg=None):
        """Assert that two configuration snapshots are equal.

        Compare setup-tool snapshots identified by ``before_id`` and
        ``after_id`` and assert that they are equal.

        """
        before = self.setup_tool._getImportContext('snapshot-' + before_id)
        after = self.setup_tool._getImportContext('snapshot-' + after_id)

        self.maxDiff = None
        self.assertMultiLineEqual(
            self.setup_tool.compareConfigurations(
                before, after, skip=self.skip_files),
            '',
            msg=msg)

    def test_quickinstall_uninstallation_removes_resets_configuration(self):
        self._install_dependencies()

        self._create_before_snapshot()
        with snapshots.enabled():
            self._install_package()
        self._quickinstaller_uninstall_package()
        self._create_after_shapshot()

        self.assertSnapshotsEqual(
            msg='Quickinstaller seems not to uninstall everything.')

    def test_setup_tool_uninstall_profile_removes_resets_configuration(self):
        self._install_dependencies()

        self._create_before_snapshot()
        with snapshots.enabled():
            self._install_package()
        self._setuptool_uninstall_package()
        self._create_after_shapshot()

        self.assertSnapshotsEqual(
            msg='The uninstall profile seems not to uninstall everything.')

    def test_uninstall_method_is_available(self):
        product = InstalledProduct(self.package)
        self.assertIsNotNone(
            product.getUninstallMethod(),

            'The package "{0}" has no uninstall external method defined,'
            ' or there is an error (e.g. ImportError) in your external'
            ' method, which might be swallowed silently by quick installer.'
            ' Take a look at the ftw.contentpage package for an example.'
            .format(self.package))
