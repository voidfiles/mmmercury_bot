#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    "mmmercury"
]

requires = [
    "redis==2.7.2",
    "requests==1.1.0",
    "redisco==0.1.4",
    "iso8601==0.1.4",
    "-e git+git@github.com:saffsd/langid.py.git@5048323bd2f21265a06dcc0717ceb26bf05806f1#egg=langid-dev",
    "pytz==2012j",
]

setup(
    name='mmmercury',
    version='0.1.1',
    description='An App.net bot.',
    long_description=open('README.md').read(),
    author='Alex Kessinger',
    author_email='voidfiles@gmail.com',
    url='https://github.com/voidfiles/mmmercury_bot',
    packages=packages,
    package_data={},
    package_dir={'mmmercury': 'mmmercury'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)