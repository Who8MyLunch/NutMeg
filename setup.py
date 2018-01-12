
from __future__ import division, print_function, unicode_literals, absolute_import

import setuptools


version = '2018.1.12'

dependencies = ['sarge', 'ordered-namespace']

setuptools.setup(install_requires=dependencies,
                 include_package_data=True,
                 packages=setuptools.find_packages(),
                 version=version)
