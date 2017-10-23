#!/usr/bin/python

try:
    from setuptools import setup
    from setuptools.extension import Extension
except Exception:
    from distutils.core import setup
    from distutils.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext
import numpy

extensions = [
    Extension('ecosim/collisiongrid/collision_gridx',
             ['ecosim/collisiongrid/collision_gridx.pyx']),
]

setup(
    name = "ecosim",
    version = '0.1.0',
    author = 'Joel Simon (joelsimon.net)',
    install_requires = ['numpy', 'cython'],
    license = 'MIT',
    cmdclass={'build_ext' : build_ext},
    include_dirs = [numpy.get_include()],

    ext_modules = cythonize(
        extensions,
        include_path = [numpy.get_include()],
    )
)
