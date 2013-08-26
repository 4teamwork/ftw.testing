from setuptools import setup, find_packages
import os

version = '1.4'
maintainer = 'Jonas Baumann'

extras_require = {
    'splinter': [
        'plone.app.testing',
        'splinter >= 0.5.1',
        'lxml',
        'cssselect']}

tests_require = [
    'Acquisition<4.0a1',
    'Products.PloneHotfix20121106',
    'Plone',
    'plone.app.testing',
    'plone.app.dexterity',
    ] + extras_require['splinter']

extras_require['tests'] = tests_require


setup(name='ftw.testing',
      version=version,
      description='Provides some testing helpers and an advanced MockTestCase.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw testing mocking testcase mock stub',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.testing',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'plone.mocktestcase',
        'plone.testing',
        'unittest2',
        'zope.component',
        'zope.configuration',
        'zope.interface',
        'zope.publisher',
        ],

      tests_require=tests_require,
      extras_require=extras_require,

      entry_points='''
      # -*- Entry points: -*-
      ''',
      )
