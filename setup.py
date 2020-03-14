from setuptools import find_packages, setup

import pyui

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="pyui",
    version=pyui.__version__,
    description="A declarative GUI framework for Python using PySDL2.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dan Watson",
    author_email="dcwatson@gmail.com",
    url="https://github.com/dcwatson/pyui",
    project_urls={"Documentation": "https://dcwatson.github.io/pyui/"},
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: User Interfaces",
    ],
)
