from ftw.testing import FunctionalSplinterTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig


class PageObjectLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import plone.app.dexterity
        xmlconfig.file('configure.zcml',
                       plone.app.dexterity,
                       context=configurationContext)

        import ftw.testing.tests
        xmlconfig.file('profiles/dxtype.zcml',
                       ftw.testing.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(
            portal, 'ftw.testing.tests:dxtype')


PAGE_OBJECT_FIXTURE = PageObjectLayer()
PAGE_OBJECT_FUNCTIONAL = FunctionalSplinterTesting(
    bases=(PAGE_OBJECT_FIXTURE, PLONE_ZSERVER),
    name="ftw.testing:pageobject:functional")
