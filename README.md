# sithom README

<a href="hhttps://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
 <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  <a href="(https://github.com/sdat2/sithom/actions/workflows/python-package.yml"><img alt="Python package" src="https://github.com/sdat2/sithom/actions/workflows/python-package.yml/badge.svg"></a>
   <a href="https://sithom.readthedocs.io/en/latest/MAIN_README.html"><img alt="Documentation Status" src="https://readthedocs.org/projects/sithom/badge/?version=latest"></a>
    <a href="https://badge.fury.io/py/sithom"><img alt="PyPI Version" src="https://badge.fury.io/py/sithom.svg"></a>

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
