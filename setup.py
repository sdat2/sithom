"""setup.py allows the installation of the project by pip."""
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sithom",
    version="0.0.1",
    author="Simon Thomas",
    author_email="sdat2@cam.ac.uk",
    description="General utility scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sdat2/sithom",
    packages=find_packages(where="sithom"),
    # test_suite="src.tests.test_all.suite",
    # setup_requires=["pytest-runner"],
    package_dir={"": "sithom"},
    tests_require=["pytest"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
