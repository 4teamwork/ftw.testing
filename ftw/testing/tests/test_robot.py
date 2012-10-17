from ftw.testing.robotfw import LocalizedRobotLayer
from ftw.testing.testcase import MockTestCase
from mocker import ANY
from unittest2 import TestCase


class TestLanguageResolution(TestCase):

    def test_get_translations(self):
        layer = LocalizedRobotLayer()
        self.assertIn('en', layer._get_translations())

    def test_english(self):
        layer = LocalizedRobotLayer(languages=['en'])
        self.assertEqual(
            layer._get_bdd_prefixes(),
            ['given ',
             'when ',
             'then ',
             'and ',
             'but '])

    def test_german(self):
        layer = LocalizedRobotLayer(languages=['de'])
        self.assertEqual(
            layer._get_bdd_prefixes(),
            ['angenommen ',
             'gegeben sei ',
             'wenn ',
             'dann ',
             'und ',
             'aber '])

    def test_multiple_languages(self):
        layer = LocalizedRobotLayer(languages=['en', 'de'])
        self.assertEqual(
            layer._get_bdd_prefixes(),
            ['given ',
             'when ',
             'then ',
             'and ',
             'but ',
             'angenommen ',
             'gegeben sei ',
             'wenn ',
             'dann ',
             'und ',
             'aber '])

    def test_default_language_is_english(self):
        self.assertEqual(LocalizedRobotLayer()._languages, ['en'])

    def test_setting_multiple_languages(self):
        self.assertEqual(
            LocalizedRobotLayer(['en', 'de'])._languages, ['en', 'de'])

    def test_setting_all_languages(self):
        layer = LocalizedRobotLayer('all')
        self.assertIn('en', layer._languages)
        self.assertIn('de', layer._languages)
        self.assertIn('ar', layer._languages)

        layer = LocalizedRobotLayer('*')
        self.assertIn('en', layer._languages)
        self.assertIn('de', layer._languages)
        self.assertIn('ar', layer._languages)


class TestPatching(MockTestCase):

    def setUp(self):
        super(TestPatching, self).setUp()
        from robot.running.namespace import Namespace

        class StubbedNamespace(object, Namespace):
            def __init__(self): pass

        self.namespace = StubbedNamespace()

    def test_german_fails_without_patching(self):
        ns = self.mocker.proxy(self.namespace)
        self.expect(ns._get_handler(ANY)).count(0)

        self.replay()

        ns._get_bdd_style_handler('Angenommen es w\xc3\xbcrde funktionieren')

    def test_german_works_with_patching_layer(self):
        ns = self.mocker.patch(self.namespace)
        self.expect(ns._get_handler('deutscher text')).count(1)

        self.replay()

        layer = LocalizedRobotLayer(languages=['en', 'de'])
        layer.setUp()

        try:
            ns._get_bdd_style_handler(
                'Gegeben sei deutscher text')
        finally:
            layer.tearDown()
