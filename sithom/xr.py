"""Xarray utilities module."""
from typing import Union, Sequence
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
            \\bar{T}_{\\text{Lat }}=\\frac{1}{\\text{nLon }}
            \\sum_{i=1}^{\\text{nLon}} T_{ \\text{Lon}, \\; i}
        \\end{equation}

        \\begin{equation}
            \\bar{T}_{\\text{ month }}=
            \\frac{
            \\sum_{j=1}^{\\text{nLat} }
            \\cos \\left(\\text{ Lat }_{j} \\right)
            \\bar{T}_{\\text{ Lat }, \\; j}
            }
            {
            \\sum_{j=1}^{\\text{nLat} }
            \\cos \\left( \\text{ Lat }_{j} \\right)
            }
        \\end{equation}

    Args:
        da (xr.DataArray): da to average.
        x_dim: The longitude dimension name. Defaults to "longitude".
        y_dim: The latitude dimension name. Defaults to "latitude".

    Returns:
        xr.DataArray: Avarage of da.

    Example of calculating and plotting mean timeseries of dataarray::

        >>> import xarray as xr
        >>> from sithom.xr import spatial_mean
        >>> da = xr.tutorial.open_dataset("air_temperature").air
        >>> timeseries_mean = spatial_mean(da, x_dim="lon", y_dim="lat")
    
    timeseries_mean.plot.line()
    """
    # make sure the datarray is the right way round.
    dataarray = mon_increase(dataarray, x_dim=x_dim, y_dim=y_dim)

    # Find mean for each latitude
    mean_lat = dataarray.mean(dim=x_dim)

    # Find Weighted mean of those values
    # https://numpy.org/doc/stable/reference/generated/numpy.cos.html
    # https://numpy.org/doc/stable/reference/generated/numpy.radians.html
    num = (np.cos(np.radians(dataarray[y_dim])) * mean_lat).sum(dim=y_dim)
    denom = np.sum(np.cos(np.radians(dataarray[y_dim])))

    # Find spatially weighted mean
    mean = num / denom

    return mean


def _latexify(units: str) -> str:
    """
    Latexify the units.

    Args:
        ins (str): input string.

    Returns:
        str: latexed output string.

    Examples::
        >>> from sithom.xr import _latexify
        >>> _latexify("m s**-2")
        'm s$^{-2}$'
        >>> _latexify("kg m s**-2")
        'kg m s$^{-2}$'
        >>> _latexify("degree_Celsius")
        '$^{\\\\circ}$C'
        >>> _latexify("degK")
        'K'

    """
    output = ""
    for unit_index in units.split(" "):
        if "**" in unit_index:
            unit, index = unit_index.split("**")
            output += unit + "$^{" + index + "}$"
        else:
            output += unit_index
        output += " "
    output = output.strip(" ")
    unit_d = {"degree_Celsius": r"$^{\circ}$C", "degK": "K"}
    for initial_unit in unit_d:
        if initial_unit in units:
            output = output.replace(initial_unit, unit_d[initial_unit])
    return output


def plot_units(
    xr_obj: Union[xr.DataArray, xr.Dataset],
    x_dim: str = "longitude",
    y_dim: str = "latitude",
) -> Union[xr.DataArray, xr.Dataset]:
    """
    Adding good latex units to make the xarray object plottable.

    Xarray uses "long_name" and "units" attributes for plotting.

    Fails softly.

    Args:
        xr_da (Union[xr.DataArray, xr.Dataset]): Initial datarray/dataset
            (potentially with units for axes).
        x_dim (str): Defaults to "longitude".
        y_dim (str): Defaults to "latitude".

    Returns:
        Union[xr.DataArray, xr.Dataset]: Datarray/Dataset with correct
            units/names for plotting. Assuming that you've given the
            correct x_dim and y_dim for the object.

    Examples of using it::
        >>> import xarray as xr
        >>> from sithom.xr import plot_units
        >>> da = plot_units(xr.tutorial.open_dataset("air_temperature").air)
        >>> da.attrs["units"]
        'K'

    """
    if x_dim in xr_obj.coords:
        xr_obj.coords[x_dim].attrs["units"] = r"$^{\circ}$E"
        xr_obj.coords[x_dim].attrs["long_name"] = "Longitude"
    if y_dim in xr_obj.coords:
        xr_obj.coords[y_dim].attrs["units"] = r"$^{\circ}$N"
        xr_obj.coords[y_dim].attrs["long_name"] = "Latitude"

    if isinstance(xr_obj, xr.Dataset):
        for var in xr_obj:
            if "units" in xr_obj[var].attrs:
                xr_obj[var].attrs["units"] = _latexify(xr_obj[var].attrs["units"])
    elif isinstance(xr_obj, xr.DataArray):
        if "units" in xr_obj.attrs:
            xr_obj.attrs["units"] = _latexify(xr_obj.attrs["units"])

    return xr_obj


def mon_increase(
    xr_obj: Union[xr.Dataset, xr.DataArray],
    x_dim: str = "longitude",
    y_dim: str = "latitude",
) -> Union[xr.Dataset, xr.DataArray]:
    """Make sure that an xarray axes has monotonically increasing values.

    Args:
        xr_obj (Union[xr.Dataset, xr.DataArray]): 
        x_dim (str, optional): x dimension name. Defaults to "longitude".
        y_dim (str, optional): y dimension name. Defaults to "latitude".

    Returns:
        Union[xr.Dataset, xr.DataArray]: xarray object.

    Examples::
        >>> import xarray as xr
        >>> da = xr.tutorial.open_dataset("air_temperature").air
        >>> improved_da = mon_increase(da, x_dim="lon", y_dim="lat")

    """

    def positive_monotonic(indices: Sequence) -> bool:
        return all(indices[i] <= indices[i + 1] for i in range(len(indices) - 1))

    def negative_monotonic(indices: Sequence) -> bool:
        return all(indices[i] >= indices[i + 1] for i in range(len(indices) - 1))

    for var in [x_dim, y_dim]:
        if negative_monotonic(xr_obj.coords[var].values):
            xr_obj = xr_obj.reindex(**{var: xr_obj.coords[var][::-1]})
        elif not positive_monotonic(xr_obj.coords[var].values):
            assert False

    return xr_obj
