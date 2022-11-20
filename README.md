# sithom README

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![Python package](https://github.com/sdat2/sithom/actions/workflows/python-package.yml/badge.svg)](https://github.com/sdat2/sithom/actions/workflows/python-package.yml)[![Documentation Status](https://readthedocs.org/projects/sithom/badge/?version=latest)](https://sithom.readthedocs.io/en/latest/?badge=latest)[![PyPI version](https://badge.fury.io/py/sithom.svg)](https://badge.fury.io/py/sithom)[![DOI](https://zenodo.org/badge/496635214.svg)](https://zenodo.org/badge/latestdoi/496635214)


## Description

A package for shared utility scripts that I use in my research projects.

I realised I was copying functionality from project to project. So instead, here it is.

## Install using pip

```txt
pip install sithom
```

## Install using conda

```txt
conda install -c conda-forge sithom
```

## Package structure

```txt

├── CHANGELOG.txt      <- List of main changes at each new package version.
├── CITATION.cff       <- File to allow you to easily cite this repository.
├── LICENSE            <- MIT Open software license.
├── Makefile           <- Makefile with commands.
├── pytest.ini         <- Enable doctest unit-tests.
├── README.md          <- The top-level README for developers using this project.
├── setup.py           <- Python setup file for pip install.
|
├── sithom             <- Package folder.
|   |
│   ├── __init__.py    <- Init file.
│   ├── _version.py    <- Key package information.
│   ├── curve.py       <- Curve fitting w. uncertainty propogation.
│   ├── misc.py        <- Miscellanious utilties.
│   ├── place.py       <- Place objects.
│   ├── plot.py        <- Plot utilties.
│   ├── time.py        <- Time utilties.
│   ├── unc.py         <- Uncertainties utilties.
│   └── xr.py          <- Xarray utilties.
|
└── tests              <- Test folder.

```

## Requirements

 - Python 3.8+
 - `matplotlib`
 - `seaborn`
 - `cmocean`
 - `xarray`
 - `uncertainties`
 - `jupyterthemes`
 