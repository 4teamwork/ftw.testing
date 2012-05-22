from setuptools import setup, find_packages
import os

version = '1.3.dev0'
maintainer = 'Jonas Baumann'

tests_require = [
    'Acquisition<4.0a1',
    ]

setup(name='ftw.testing',
      version=version,
      description='Provides some testing helpers and an advanced MockTestCase.',

      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
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
        'unittest2',
        'plone.mocktestcase',
        'plone.testing',
        'zope.interface',
        'zope.component',
        'zope.configuration',
        'zope.publisher',
        ],
      tests_require=tests_require,
      extras_require={'tests': tests_require},

      entry_points='''
      # -*- Entry points: -*-
      ''',
      )
