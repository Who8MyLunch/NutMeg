
from __future__ import division, print_function, unicode_literals, absolute_import

import setuptools

version = '2017.3.25'

dependencies = ['sarge']

setuptools.setup(install_requires=dependencies,
                 include_package_data=True,
                 packages=setuptools.find_packages(),
                 # zip_safe=False,

                 name='nutmeg',
                 description='Simple video processing tools. Python + fmpeg.',
                 maintainer='Pierre V. Villeneuve',
                 maintainer_email='pierre.villeneuve@gmail.com',
                 version=version)
