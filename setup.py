
from __future__ import division, print_function, unicode_literals, absolute_import

import setuptools

"""
Great workflow for configuring a project for both github and pypi:

http://peterdowns.com/posts/first-time-with-pypi.html
"""

version = '2017.3.25'

dependencies = ['sarge']

setuptools.setup(install_requires=dependencies,
                 include_package_data=True,
                 packages=setuptools.find_packages(),
                 # zip_safe=False,

                 name='nutmeg',
                 description='Simple video processing tools. Python + fmpeg.',
                 author='Pierre V. Villeneuve',
                 author_email='pierre.villeneuve@gmail.com',
                 url='https://github.com/Who8MyLunch/NutMeg',
                 download_url='',
                 version=version)
