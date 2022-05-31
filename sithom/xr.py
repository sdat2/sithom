"""Xarray utils."""
from typing import Union
import numpy as np
import xarray as xr


def spatial_mean(
    dataarray: xr.DataArray, x_dim: str = "longitude", y_dim: str = "latitude"
) -> xr.DataArray:
    # pylint: disable=anomalous-backslash-in-string
    """
    Average a datarray over "longitude" and "latitude" coordinates.

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
            \\bar{T}_{\\text{Lat }}=\\frac{1}{n \\text{ Lon }}
            \\sum_{i=1}^{n \\text{Lon}} T_{\\text \\text{Lon},\\; i}
        \\end{equation}

        \\begin{equation}
            \\bar{T}_{\\text {month }}=\\frac{\\sum_{j=1}^{n \\text{ Lat }}
            \\cos \\left(\\text { Lat }_{j}\\right)
            \\bar{T}_{\\text{lat },\\; j}}{\\sum_{j=1}^{\\text{n \\text{ Lat } }}
            \\cos \\left(\\text{ Lat }_{j}\\right)}
        \\end{equation}

    Args:
        da (xr.DataArray): da to average.
        x_dim: The longitude dimension name. Defaults to "longitude".
        y_dim: The latitude dimension name. Defaults to "latitude".

    Returns:
        xr.DataArray: Avarage of da.

    Example of calculating and plotting mean timeseries of dataarray::

        import xarray as xr
        from sithom.xr import spatial_mean
        da = xr.tutorial.open_dataset("air_temperature").air
        timeseries_mean = spatial_mean(da)
        timeseries_mean.plot.line()

    """
    # Find mean temperature for each latitude
    mean_sst_lat = dataarray.mean(dim=x_dim)

    # Find Weighted mean of those values
    # https://numpy.org/doc/stable/reference/generated/numpy.cos.html
    # https://numpy.org/doc/stable/reference/generated/numpy.radians.html
    num = (np.cos(np.radians(dataarray[y_dim])) * mean_sst_lat).sum(dim=y_dim)
    denom = np.sum(np.cos(np.radians(dataarray[y_dim])))

    # Find mean global temperature
    mean_temp = num / denom

    return mean_temp


def _latexify(input: str) -> str:
    """
    Latexify the units.

    Args:
        input (str): input string.

    Returns:
        str: latexed output string.
    """
    output = ""
    for x in input.split(" "):
        if "**" in x:
            y, z = x.split("**")
            output += y+"$^{"+ z +"}$"
        else:
            output += x
        output += " "
    output.strip(" ")
    if "degree_Celsius" in input:
        output.replace("degree_Celsius","$^{\circ}$C")
    return output


def plot_units(
    xr_obj: Union[xr.DataArray, xr.Dataset],
    x_dim: str = "longitude",
    y_dim: str = "latitude",
) -> Union[xr.DataArray, xr.Dataset]:
    """
    Adding good units to make axes plottable.

    Currently only for lat, lon axes, but could be improved to
    add degrees celsius and so on.

    Fails softly.

    Args:
        xr_da (Union[xr.DataArray, xr.Dataset]): Initial datarray/datset
            (potentially with units for axes).
        x_dim (str): Defaults to "longitude"
        y_dim (str): Defaults to "latitude"

    Returns:
        Union[xr.DataArray, xr.Dataset]: Datarray/Dataset with correct
            units/names for plotting. Assuming that you've given the
            correct x_dim and y_dim for the object.
    """
    if x_dim in xr_obj.coords:
        xr_obj.coords[x_dim].attrs["units"] = r"$^{\circ}$E"
        xr_obj.coords[x_dim].attrs["long_name"] = "Longitude"
    if y_dim in xr_obj.coords:
        xr_obj.coords[y_dim].attrs["units"] = r"$^{\circ}$N"
        xr_obj.coords[y_dim].attrs["long_name"] = "Latitude"

    if isinstance(xr_obj, xr.Dataset):
        for var in xr_obj:
            xr_obj[var].attrs["units"] = _latexify(xr_obj[var].attrs["units"])
    elif isinstance(xr_obj, xr.DataArray):
        xr_obj.attrs["units"] = _latexify(xr_obj.attrs["units"])

    return xr_obj
