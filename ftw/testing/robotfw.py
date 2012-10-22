from plone.testing import Layer
import copy
import json
import os.path


class LocalizedRobotLayer(Layer):
    """Testing layer for patching the robot framework so that the
    BBD prefixes (given / when / then /and) can be localized.
    """

    def __init__(self, languages=['en']):
        super(LocalizedRobotLayer, self).__init__()

        if languages in ('all', '*'):
            self._languages = self._get_translations().keys()

        else:
            self._languages = languages

    def setUp(self):
        super(LocalizedRobotLayer, self).setUp()
        self._apply_patch()

    def tearDown(self):
        super(LocalizedRobotLayer, self).tearDown()
        self._remove_patch()

    def _get_bdd_prefixes(self):
        prefixes = []
        for lang in self._languages:
            translations = self._get_translations()[lang]

            for key in ('given', 'when', 'then', 'and', 'but'):
                prefixes.extend(self._convert_translation_value(
                        translations[key]))

        return prefixes

    def _convert_translation_value(self, value):
        return [('%s ' % val.lower()).encode('utf8')
                for val in value.split('|')
                if val != '*']

    def _get_translations(self):
        if getattr(self, '_translations', None) is None:
            path = os.path.abspath(
                os.path.join(os.path.dirname(__file__),
                             'resources', 'i18n.json'))

            self._translations = json.loads(open(path).read())

        return self._translations

    def _apply_patch(self):
        prefixes = self._get_bdd_prefixes()

        from robot.running import namespace

        def _patched_get_bdd_style_handler(self, name):
            for prefix in prefixes:
                if name.lower().startswith(prefix):
                    handler = self._get_handler(name[len(prefix):])
                    if handler:
                        handler = copy.copy(handler)
                        handler.name = name
                    return handler
            return None

        self._original = namespace.Namespace._get_bdd_style_handler
        namespace.Namespace._get_bdd_style_handler = \
            _patched_get_bdd_style_handler

    def _remove_patch(self):
        from robot.running import namespace
        namespace.Namespace._get_bdd_style_handler = self._original


class RobotLibrary(object):

    def __init__(self):
        self._localization = None

    def setup_localization(self, languages='en de'):
        languages = languages.strip().split()
        self._localization = LocalizedRobotLayer(languages)
        self._localization.setUp()

    def teardown_localization(self):
        if self._localization:
            self._localization.tearDown()
            self._localization = None
