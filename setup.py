
from __future__ import division, print_function, unicode_literals, absolute_import

import setuptools

"""
PyPi Instructions:
https://packaging.python.org/distributing/#uploading-your-project-to-pypi

twin command-line tool:
https://github.com/pypa/twine
"""

version = '2017.3.27d'

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
                 download_url='https://github.com/Who8MyLunch/NutMeg/archive/{}.tar.gz'.format(version),
                 version=version,
                 keywords=['video', 'ffmpeg', 'intra', 'clip', 'probe'])
