# sithom README

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>[![Python package](https://github.com/sdat2/sithom/actions/workflows/python-package.yml/badge.svg)](https://github.com/sdat2/sithom/actions/workflows/python-package.yml)[![Documentation Status](https://readthedocs.org/projects/sithom/badge/?version=latest)](https://sithom.readthedocs.io/en/latest/?badge=latest)[![PyPI version](https://badge.fury.io/py/sithom.svg)](https://badge.fury.io/py/sithom)

A package for shared utility scripts that I use in my research projects.

I realised I was copying functionality from project to project. So instead, here it is.

## Install using pip:

```bash
pip install sithom
```

## Package structure

```txt
├── LICENSE
├── Makefile           <- Makefile with commands.
├── README.md          <- The top-level README for developers using this project.
|
├── sithom          <- package folder.
|   |
│   ├── __init__.py   <- init.
│   ├── _version.py   <- key package information.
│   ├── misc.py       <- miscellanious utilties.
│   ├── plot.py       <- plot utilties.
│   ├── time.py       <- time utilties.
│   ├── unc.py        <- uncertainties utilties.
│   └── xr.py         <- xarray utilties.
|
└── tests             <- test folder.

```

## Requirements

- Python 3.8+
- `matplotlib`
- `seaborn`
- `cmocean`
- `xarray`
- `uncertainties`
