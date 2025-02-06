"""Use this module to create animations using the plot module repeatedly."""

from typing import List, Tuple, Optional
import xarray as xr
from .plot import feature_grid


def dataset_ani(
    ds: xr.Dataset,
    fig_var: List[List[str]],
    units: Optional[List[List[str]]],
    names: Optional[List[List[str]]],
    vlim: Optional[List[List[Tuple[float, float, str]]]],
    super_titles: List[str],
    figsize: Tuple[float, float] = (12, 6),  # in inches
    label_size: int = 12,
    supertitle_pos: Tuple[float, float] = (0.4, 1.3),
    xy: Optional[Tuple[Tuple[str, str, str], Tuple[str, str, str]]] = None,
    label=True,
    time_dim="T",
):
    print(ds, fig_var)
    # let's test if all var ds
    for var in fig_var:
        if var is not None:
            assert var in ds
