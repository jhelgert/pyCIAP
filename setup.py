
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pyCIAP",
    url="https://github.com/jhelgert/pyCIAP",
    version='0.0.1',
    packages=['pyCIAP'],
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
        "gurobipy"
    ]
)
