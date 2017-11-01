#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
from setuptools import setup, find_packages
import ip2geotools


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = '\n' + f.read()

with io.open(os.path.join(here, 'LICENSE'), encoding='utf-8') as f:
    license = '\n' + f.read()

with io.open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [i.strip() for i in f.readlines()]

setup(
    name='ip2geotools',
    version=ip2geotools.__version__,
    description=ip2geotools.__description__,
    long_description=readme,
    author=ip2geotools.__author__,
    author_email=ip2geotools.__author_email__,
    url=ip2geotools.__url__,
    download_url=ip2geotools.__url__ + '/archive/' + ip2geotools.__version__ + '.tar.gz',
    packages=find_packages(exclude=['docs', 'tests', 'tests.*']),
    package_data={'': ['LICENSE']},
    package_dir={'ip2geotools': 'ip2geotools'},
    install_requires=requirements,
    include_package_data=True,
    test_suite="tests",
    license=ip2geotools.__license__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': ['ip2geotools=ip2geotools.cli:execute_from_command_line'],
    },
)
