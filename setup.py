
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy as np

with open("README.md", "r") as f:
    long_description = f.read()

ext = Extension(
    name="pyCIAP.dsur_cy",
    sources=["pyCIAP/dsur_cy.pyx"],
    include_dirs=[np.get_include()],
    define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
)

setup(
    name="pyCIAP",
    url="https://github.com/jhelgert/pyCIAP",
    version='0.0.2',
    ext_modules=cythonize(ext, language_level="3"),
    packages=find_packages(),
    author='Jonathan Helgert',
    author_email='jhelgert@mail.uni-mannheim.de',
    description='A simple package the solve CIAPs with dwell time constraints',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy",
    ],
    zip_safe=False
)
