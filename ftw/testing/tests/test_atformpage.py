from ftw.testing.pages import Plone
from ftw.testing.testing import PAGE_OBJECT_FUNCTIONAL
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from unittest2 import TestCase
import transaction


class TestATFormPage(TestCase):

    layer = PAGE_OBJECT_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Contributor', 'Member'])
        transaction.commit()

    def test_schemata_labels_on_page(self):
        form = (Plone()
                .login()
                .visit_portal()
                .open_add_form('Page'))

        ignore_schematas = (
            'Ownership',  # Plone <= 4.1
            'Creators',  # Plone >= 4.2
            )

        self.assertEquals(
            ['Default', 'Categorization', 'Dates', 'Settings'],

            filter(lambda label: label not in ignore_schematas,
                   form.schemata_labels))

    def test_schemata_field_labels_on_page(self):
        form = (Plone()
                .login()
                .visit_portal()
                .open_add_form('Page'))

        self.assertEquals(['Title', 'Summary', 'Body Text'],
                          form.schemata_field_labels['Default'])

    def test_schemata_field_labels_on_image(self):
        # The image widget has a different structure.
        form = (Plone()
                .login()
                .visit_portal()
                .open_add_form('Image'))

        self.assertIn('Image', form.schemata_field_labels['Default'])

    def test_field_labels_on_page(self):
        form = (Plone()
                .login()
                .visit_portal()
                .open_add_form('Page'))

        self.assertIn('Title', form.field_labels)
