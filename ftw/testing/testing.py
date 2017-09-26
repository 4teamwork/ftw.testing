from ftw.testing import FTWIntegrationTesting
from ftw.testing import IS_PLONE_5
from ftw.testing.quickinstaller import snapshots
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from zope.configuration import xmlconfig


snapshots.disable()


class TestingLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.testing.tests
        xmlconfig.file('profiles/dxtype.zcml',
                       ftw.testing.tests,
                       context=configurationContext)

        xmlconfig.file('views.zcml',
                       ftw.testing.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.testing.tests:dxtype')

        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


FTW_TESTING_FIXTURE = TestingLayer()
FTW_TESTING_FUNCTIONAL = FunctionalTesting(
    bases=(FTW_TESTING_FIXTURE, PLONE_ZSERVER, ),
    name="ftw.testing:functional")
FTW_TESTING_INTEGRATION = FTWIntegrationTesting(
    bases=(FTW_TESTING_FIXTURE, ),
    name="ftw.testing:integration")
