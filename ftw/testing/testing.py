from ftw.testing import FunctionalSplinterTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer


class PageObjectLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )


PAGE_OBJECT_FIXTURE = PageObjectLayer()
PAGE_OBJECT_FUNCTIONAL = FunctionalSplinterTesting(
    bases=(PAGE_OBJECT_FIXTURE, ),
    name="ftw.testing:pageobject:functional")
