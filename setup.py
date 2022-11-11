"""setup.py allows the installation of the project by pip."""
import os
import sys
from shutil import rmtree
from setuptools import find_packages, setup, Command
from typing import Dict, List

NAME = "sithom"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

REQUIRED = [
    "matplotlib",
    "seaborn",
    "jupyterthemes",
    "cmocean",
    "pandas",
    "xarray",
    "uncertainties",
    "pooch",  # only for test tutorial.
]

here = os.path.abspath(os.path.dirname(__file__))

# Load the package"s _version.py module as a dictionary.
about: Dict = {}
with open(os.path.join(here, NAME, "_version.py")) as f:
    # pylint: disable=exec-used
    exec(f.read(), about)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options: List = []

    @staticmethod
    def status(s):
        """Print things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Publish package to PyPI."""
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


setup(
    name=NAME,
    version=about["__version__"],
    author=about["__author__"],
    author_email="sdat2@cam.ac.uk",
    description="General utility scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=str("https://github.com/sdat2/" + NAME),
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
    install_requires=REQUIRED,
    license="MIT",
    # test_suite=str(NAME +".tests.test_all.suite"),
    # setup_requires=["pytest-runner"],
    # package_dir={"": NAME},
    tests_require=["pytest", "pooch"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    cmdclass={"upload": UploadCommand,},
)
