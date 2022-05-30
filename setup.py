"""setup.py allows the installation of the project by pip."""
import os
from setuptools import find_packages, setup
from typing import Dict

NAME = "sithom"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

REQUIRED = ["matplotlib", "seaborn", "jupyterthemes", "cmocean", "xarray", "uncertainties"]

here = os.path.abspath(os.path.dirname(__file__))

# Load the package"s _version.py module as a dictionary.
about: Dict = {}
with open(os.path.join(here, NAME, "_version.py")) as f:
    # pylint: disable=exec-used
    exec(f.read(), about)

setup(
    name=NAME,
    version=about["__version__"],
    author="Simon Thomas",
    author_email="sdat2@cam.ac.uk",
    description="General utility scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sdat2/sithom",
    packages=find_packages(where=NAME),
    include_package_data=True,
    install_requires=REQUIRED,
    license="MIT",
    # test_suite="src.tests.test_all.suite",
    # setup_requires=["pytest-runner"],
    # package_dir={"": "sithom"},
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.6",
)
