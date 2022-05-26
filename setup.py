"""setup.py allows the installation of the project by pip."""
from setuptools import find_packages, setup

setup(
    name="sithom",
    version="0.0.1",
    author="Simon Thomas",
    author_email="sdat2@cam.ac.uk",
    description="General utility scripts",
    url="https://github.com/sdat2/sithom",
    packages=find_packages(),
    # test_suite="src.tests.test_all.suite",
    # setup_requires=["pytest-runner"],
    # tests_require=["pytest"],
)
