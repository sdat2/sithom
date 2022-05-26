"""Xarray utils."""
import numpy as np
import xarray as xr


def spatial_mean(da: xr.DataArray, x_dim: str = "X", y_dim: str = "Y") -> xr.DataArray:
    # pylint: disable=anomalous-backslash-in-string
    """
    Average a datarray over "X" and "Y" coordinates.

    Spatially weighted.

    Originally from:
    https://ncar.github.io/PySpark4Climate/tutorials/Oceanic-Ni%C3%B1o-Index/
    (although their version is wrong as it assumes numpy input is degrees)

    https://numpy.org/doc/stable/reference/generated/numpy.cos.html
    https://numpy.org/doc/stable/reference/generated/numpy.radians.html

    The average should behave like:

    .. math::
        :nowrap:

        \\begin{equation}
            \\bar{T}_{\\text {lat }}=\\frac{1}{n \\text{ Lon }}
            \\sum_{i=1}^{n \\text{Lon}} T_{\\text \\text{lon}, i}
        \\end{equation}

        \\begin{equation}
            \\bar{T}_{\\text {month }}=\\frac{\\sum_{j=1}^{n L a t}
            \\cos \\left(\\text { lat }_{j}\\right)
            \\bar{T}_{\\text {lat }, j}}{\\sum_{j=1}^{\\text{n \\text{Lat} }}
            \\cos \\left(\\text { lat }_{j}\\right)}
        \\end{equation}

    Args:
        da (xr.DataArray): da to average.
        x_dim: The longitude dimension name. Defaults to "X".
        y_dim: The latitude dimension name. Defaults to "Y".

    Returns:
        xr.DataArray: Avarage of da.
    """
    # Find mean temperature for each latitude
    mean_sst_lat = da.mean(dim="X")

    # Find Weighted mean of those values
    # https://numpy.org/doc/stable/reference/generated/numpy.cos.html
    # https://numpy.org/doc/stable/reference/generated/numpy.radians.html
    num = (np.cos(np.radians(da.Y)) * mean_sst_lat).sum(dim="Y")
    denom = np.sum(np.cos(np.radians(da.Y)))

    # Find mean global temperature
    mean_temp = num / denom

    return mean_temp
