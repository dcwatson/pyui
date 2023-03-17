import re

from setuptools import find_packages, setup

with open("README.md", "r") as readme:
    long_description = readme.read()

with open("pyui/__init__.py", "r") as init:
    version = re.match(r'.*__version__ = "(.*?)"', init.read(), re.S).group(1)

setup(
    name="pyui",
    version=version,
    description="A declarative GUI framework for Python using PySDL2.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dan Watson",
    author_email="dcwatson@gmail.com",
    url="https://github.com/dcwatson/pyui",
    project_urls={"Documentation": "https://pyui.net"},
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["PySDL2>=0.9.7"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: User Interfaces",
    ],
)
