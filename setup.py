from setuptools import setup, find_packages
import os

version = '1.0.0a1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='splinterext.proxyheader',
      version=version,
      description="A splinter companion that provides access to HTTP headers through a local proxy.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          ],
      keywords='splinter',
      author='Gilles Lenfant',
      author_email='gilles.lenfant@gmail.org',
      url='http://pypi.python.org/pypi/splinterext.proxyheader',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['splinterext'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'splinter',
          ],
      entry_points="""
      # -*- Entry points: -*-
      """
    )
