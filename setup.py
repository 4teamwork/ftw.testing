from setuptools import setup, find_packages
import os

version = '2.0.7'
maintainer = 'Jonas Baumann'

extras_require = {}
tests_require = [
    'plone.api',
    'plone.app.dexterity',
    'zc.recipe.egg',
    ]

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
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.1',
        'Framework :: Plone :: 5.2',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='ftw testing mocking testcase mock stub',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/ftw.testing',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'mock;python_version<"3.3"',
        'path.py',
        'plone.app.testing',
        'plone.testing',
        'pytz',
        'setuptools >= 20.8.1',
        'six',
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
