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
        import plone.app.dexterity
        xmlconfig.file('configure.zcml',
                       plone.app.dexterity,
                       context=configurationContext)

        import ftw.testing.tests
        xmlconfig.file('profiles/dxtype.zcml',
                       ftw.testing.tests,
                       context=configurationContext)

        xmlconfig.file('views.zcml',
                       ftw.testing.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(
            portal, 'ftw.testing.tests:dxtype')


FTW_TESTING_FIXTURE = TestingLayer()
FTW_TESTING_FUNCTIONAL = FunctionalTesting(
    bases=(FTW_TESTING_FIXTURE, PLONE_ZSERVER, ),
    name="ftw.testing:functional")
