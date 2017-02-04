from setuptools import setup, Extension
import numpy as np

setup(
    name='nurbs',
    version='0.2',
    description='Python module to work with NURBS curves and surfaces.',
    author='Runar Tenfjord',
    author_email='runten@netcom.no',
    url='https://github.com/bashseb/PyNURBS',
    packages=['nurbs'],
    include_dirs = [np.get_include()],
    ext_modules = [Extension("nurbs._bas", ["nurbs/_bas.c"])],
    package_data={'': ['LICENSE', 'README']}
    )

