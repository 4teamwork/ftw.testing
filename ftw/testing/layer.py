from path import Path
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from plone.app.testing import PLONE_FIXTURE
from plone.testing import Layer
from plone.testing import zca
from Products.CMFPlone.utils import getFSVersionTuple
from zope.configuration import xmlconfig
import logging
import os
import tempfile
import zc.buildout.easy_install
import zc.buildout.testing
import zope.component.testing

_marker = object()

# We do not use the standard zca.ZCML_DIRECTIVES layer, but a separate
# instances so that we do not share it with integration / functional tests.
# Using the same instance can cause tearing down issues.

SEPARATED_ZCML_DIRECTIVES = zca.ZCMLDirectives(
    bases=(zca.LayerCleanup(name='ftw.testing:LAYER_CLEANUP'),),
    name='ftw.testing:ZCML_DIRECTIVES')


class ComponentRegistryLayer(Layer):
    """Testing layer used for loading ZCML and keeping the same global
    component registry for all tests. This speeds up the setup.

    It is meant to be subclassed by the implementing layer.
    """

    defaultBases = (SEPARATED_ZCML_DIRECTIVES,)

    def __init__(self):
        super(ComponentRegistryLayer, self).__init__()
        self._configuration_context = None

    def setUp(self):
        zca.pushGlobalRegistry()

    def testSetUp(self):
        zca.pushGlobalRegistry()

    def testTearDown(self):
        zca.popGlobalRegistry()

    def tearDown(self):
        zca.popGlobalRegistry()
        if hasattr(self, 'configurationContext'):
            del self['configurationContext']
        zope.component.testing.tearDown(self)

    def load_zcml_file(self, filename, module):
        xmlconfig.file(filename, module,
                       context=self._get_configuration_context())

    def load_zcml_string(self, zcml):
        xmlconfig.string(zcml, context=self._get_configuration_context())

    def _get_configuration_context(self):
        if self._configuration_context is None:
            self._configuration_context = zca.stackConfigurationContext(
                self.get('configurationContext'))
            self['configurationContext'] = self._configuration_context
        return self._configuration_context


class ComponentRegistryIsolationLayer(Layer):
    defaultBases = (PLONE_FIXTURE, )

    def setUp(self):
        self['load_zcml_string'] = self.load_zcml_string

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'),
            name='ftw.testing.component_registry_isolation')
        zca.pushGlobalRegistry()

    def testTearDown(self):
        del self['configurationContext']
        zca.popGlobalRegistry()

    def load_zcml_string(self, *zcml_lines):
        zcml = '\n'.join(zcml_lines)
        xmlconfig.string(zcml, context=self['configurationContext'])

    def load_zcml_file(self, filename, module):
        xmlconfig.file(filename, module,
                       context=self['configurationContext'])


COMPONENT_REGISTRY_ISOLATION = ComponentRegistryIsolationLayer()


class TempDirectoryLayer(Layer):

    def testSetUp(self):
        self['temp_directory'] = Path(tempfile.mkdtemp('ftw.testing'))

    def testTearDown(self):
        self['temp_directory'].rmtree_p()


TEMP_DIRECTORY = TempDirectoryLayer()


CONSOLE_SCRIPT_BUILDOUT_TEMPLATE = """[buildout]
parts =
    package

[package]
recipe = zc.recipe.egg:script
eggs = {package_name}{extras}
interpreter = py

[versions]
{versions}
"""


class ConsoleScriptLayer(Layer):

    def __init__(self,
                 package_name,
                 extras=('tests',),
                 buildout_template=CONSOLE_SCRIPT_BUILDOUT_TEMPLATE,
                 bases=None,
                 name=None,
                 module=None):

        super(ConsoleScriptLayer, self).__init__(bases=bases,
                                                 name=name,
                                                 module=module)
        self.package_name = package_name
        self.extras = extras
        self.buildout_template = buildout_template

    def setUp(self):
        zc.buildout.testing.buildoutSetUp(self)
        self['root_path'] = Path(self.sample_buildout)
        self['execute_script'] = self.execute_script
        del self.globs['get']

        dependencies = self.get_dependencies_with_pinnings()
        self.mark_dependencies_for_development(dependencies)
        self.write('buildout.cfg', self.get_buildout_cfg(dependencies))
        self.execute_script('buildout')

        self.filesystem_snapshot = set(Path(self.sample_buildout).walk())

    def tearDown(self):
        zc.buildout.testing.buildoutTearDown(self)
        pypi_url = 'http://pypi.python.org/simple'
        zc.buildout.easy_install.default_index_url = pypi_url
        os.environ['buildout-testing-index-url'] = pypi_url
        zc.buildout.easy_install._indexes = {}
        logging.shutdown()

    def testTearDown(self):
        for path in (set(Path(self.sample_buildout).walk())
                     - self.filesystem_snapshot):
            if path.isdir():
                path.rmtree()
            if path.isfile():
                path.remove()

    def execute_script(self, command, assert_exitcode=True):
        command = self['root_path'] + '/bin/' + command
        output, exitcode = self.system(
            command, with_exit_code=True).split('EXIT CODE: ')
        exitcode = int(exitcode)

        if assert_exitcode:
            assert exitcode == 0, ('Expected exit code 0, got'
                                   ' {0} for "{1}".\nOutput:\n{2}'.format(
                    exitcode, command, output))

        return exitcode, output

    def get_buildout_cfg(self, dependencies):
        extras = self.extras and '[{0}]'.format(', '.join(self.extras)) or ''
        versions = '\n'.join('='.join((name, version))
                             for (name, version) in dependencies.items())

        return self.buildout_template.format(package_name=self.package_name,
                                             versions=versions,
                                             extras=extras)

    def mark_dependencies_for_development(self, dependencies):
        for pkgname in sorted(dependencies.keys()):
            zc.buildout.testing.install_develop(pkgname, self)

    def get_dependencies_with_pinnings(self):
        dependencies = self.resolve_dependency_versions(self.package_name,
                                                        extras=self.extras)

        assert 'zc.recipe.egg' in dependencies, \
            'For using the ConsoleScriptLayer you need to put "zc.recipe.egg" in' + \
            ' the test dependencies of your package.'

        if getFSVersionTuple() < (4, 3):
            self.resolve_dependency_versions('manuel', dependencies)
            self.resolve_dependency_versions('zope.hookable', dependencies)
        if getFSVersionTuple() > (5, 1):
            self.resolve_dependency_versions('zope.untrustedpython', dependencies)
        return dependencies

    def resolve_dependency_versions(self, pkgname, result=None, extras=()):
        result = result or {}
        if pkgname in result or pkgname in ('setuptools', 'zc.buildout'):
            return result

        try:
            dist = get_distribution(pkgname)
        except DistributionNotFound:
            return result

        result[pkgname] = dist.version
        for pkg in dist.requires(extras):
            self.resolve_dependency_versions(pkg.project_name, result)

        return result

    @property
    def globs(self):
        return self.__dict__
