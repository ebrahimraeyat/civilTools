#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
'matplotlib>=2.0.0',
'numpy>=1.12.1',
'pandas>=0.19.2',
'PyQt5>=5.8.1',
'pyqtgraph>=0.10.0',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='civiltools',
    version='1.40.0.dev1',
    description="A series of tools for civil engineers.",
    long_description=readme + '\n\n' + history,
    author="Raeyat Ebrahim",
    author_email='ebe79442114@yahoo.com',
    url='https://github.com/ebrahimraeyat/civiltools',
    packages=[
        'civilTools',
    ],
    package_dir={'civilTools':
                 'civilTools'},
    include_package_data=True,
    install_requires=requirements,
    license = "GPL-3.0",
    zip_safe=False,
    keywords='civiltools',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: Persian',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)


# from __future__ import print_function
# from setuptools import setup, find_packages
# from setuptools.command.test import test as TestCommand
# import io
# import codecs
# import os
# import sys

# import records

# here = os.path.abspath(os.path.dirname(__file__))

# def read(*filenames, **kwargs):
#     encoding = kwargs.get('encoding', 'utf-8')
#     sep = kwargs.get('sep', '\n')
#     buf = []
#     for filename in filenames:
#         with io.open(filename, encoding=encoding) as f:
#             buf.append(f.read())
#     return sep.join(buf)

# long_description = read('README.txt', 'CHANGES.txt')

# class PyTest(TestCommand):
#     def finalize_options(self):
#         TestCommand.finalize_options(self)
#         self.test_args = []
#         self.test_suite = True

#     def run_tests(self):
#         import pytest
#         errcode = pytest.main(self.test_args)
#         sys.exit(errcode)

# setup(
#     name='sandman',
#     version=records.__version__,
#     url='http://github.com/jeffknupp/sandman/',
#     license='Apache Software License',
#     author='Jeff Knupp',
#     tests_require=['pytest'],
#     install_requires=['Flask>=0.10.1',
#                     'Flask-SQLAlchemy>=1.0',
#                     'SQLAlchemy==0.8.2',
#                     ],
#     cmdclass={'test': PyTest},
#     author_email='jeff@jeffknupp.com',
#     description='Automated REST APIs for existing database-driven systems',
#     long_description=long_description,
#     packages=['sandman'],
#     include_package_data=True,
#     platforms='any',
#     test_suite='sandman.test.test_sandman',
#     classifiers = [
#         'Programming Language :: Python',
#         'Development Status :: 4 - Beta',
#         'Natural Language :: English',
#         'Environment :: Web Environment',
#         'Intended Audience :: Developers',
#         'License :: OSI Approved :: Apache Software License',
#         'Operating System :: OS Independent',
#         'Topic :: Software Development :: Libraries :: Python Modules',
#         'Topic :: Software Development :: Libraries :: Application Frameworks',
#         'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
#         ],
#     extras_require={
#         'testing': ['pytest'],
#     }
# )
