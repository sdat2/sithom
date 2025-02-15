"""Plotting Utilities Module.

Contains generic plotting functions that are used to achieve
consistent and easy to produce plots across the project.

Example:
    Usage with simple plots::

        from sithom.plot import (
            plot_defaults,
            label_subplots,
            get_dim,
            set_dim,
            PALETTE,
            STD_CLR_LIST,
            CAM_BLUE,
            BRICK_RED,
            OX_BLUE,
        )

        plot_defaults(use_tex=True)

        # ---- example set of graphs ---

        import numpy as np
        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(2, 2)

        x = np.linspace(0, np.pi, num=100)
        axs[0, 0].plot(x, np.sin(x), color=STD_CLR_LIST[0])
        axs[0, 1].plot(x, np.cos(x), color=STD_CLR_LIST[1])
        axs[1, 0].plot(x, np.sinc(x), color=STD_CLR_LIST[2])
        axs[1, 1].plot(x, np.abs(x), color=STD_CLR_LIST[3])

        # set size
        set_dim(fig, fraction_of_line_width=1, ratio=(5 ** 0.5 - 1) / 2)

        # label subplots
        label_subplots(axs, start_from=0, fontsize=10)

"""

from typing import Sequence, Tuple, Optional, Literal, List, Union, Callable
import itertools
from shutil import which
import numpy as np
import numpy.ma as ma
import pandas as pd
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from jupyterthemes import jtplot
import cmocean
from uncertainties import unumpy as unp, ufloat
from .misc import in_notebook
from .curve import fit, label_poly


REPORT_WIDTH: float = 398.3386  # in pixels
# Constants from SVM
# Standard color list
STD_CLR_LIST = [
    "#4d2923ff",
    "#494f1fff",
    "#38734bff",
    "#498489ff",
    "#8481baff",
    "#c286b2ff",
    "#d7a4a3ff",
]
_paper_colors = sns.color_palette(STD_CLR_LIST)
# Note: To inspect colors, call `sns.palplot(_paper_colors)`
PALETTE = itertools.cycle(_paper_colors)
CAM_BLUE = "#a3c1ad"
OX_BLUE = "#002147"
BRICK_RED = "#CB4154"


def plot_defaults(use_tex: Optional[bool] = None, dpi: Optional[int] = None) -> None:
    """
    Apply plotting style to produce nice looking figures.

    Call this at the start of a script which uses `matplotlib`.
    Can enable `matplotlib` LaTeX backend if it is available.

    Uses serif font to fit into latex report.

    Args:
        use_tex (bool, optional): Whether or not to use latex matplotlib backend.
            Defaults to False.
        dpi (int, optional): Which dpi to set for the figures.
            Defaults to 600 dpi (high quality) in terminal or 150 dpi for notebooks.
            Larger dpi may be needed for presentations.

    Examples:
        Basic setting for the plotting defaults::

            >>> from sithom.plot import plot_defaults
            >>> plot_defaults()

    """
    # mac needs a different plotting backend...
    # if platform == "darwin":
    #    matplotlib.use("TkAgg")

    if in_notebook():
        jtplot.style(theme="grade3", context="notebook", ticks=True, grid=False)
        if use_tex is None:
            use_tex: bool = False  # assume tex does not exist.
        if dpi is None:
            dpi: int = 150
    else:
        if use_tex is None:
            use_tex: bool = False  # assume tex does not exist.
        if dpi is None:
            dpi = 600  # high quality dpi

    p_general = {
        "font.family": "STIXGeneral",  # Nice serif font, similar to latex default.
        # "font.family": "serif",
        # "font.serif": [],
        # Use 10pt font in plots, to match 10pt font in document
        "axes.labelsize": 10,
        "font.size": 10,
        "figure.dpi": dpi,
        "savefig.dpi": dpi,
        # Make the legend/label fonts a little smaller
        "legend.fontsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        # Times.
        "date.autoformatter.year": "%Y",
        "date.autoformatter.month": "%Y-%m",
        "date.autoformatter.day": "%Y-%m-%d",
        "date.autoformatter.hour": "%m-%d %H",
        "date.autoformatter.minute": "%Y-%m-%d %H:%M:%S",
        "date.autoformatter.second": "%H:%M:%S",
        "date.autoformatter.microsecond": "%M:%S.%f",
        # Set the font for maths
        "axes.formatter.use_mathtext": True,
        "mathtext.fontset": "cm",
        # "font.sans-serif": ["DejaVu Sans"],  # gets rid of error messages
        # "font.monospace": [],
        "figure.figsize": get_dim(),
        "figure.autolayout": True,  # turn on tight_layout.
        "lines.linewidth": 1.0,
        "scatter.marker": "X",
        "image.cmap": "viridis",
    }
    matplotlib.rcParams.update(p_general)

    # colorblind optimised colormap as default.
    preferred_style = "seaborn-colorblind"
    if preferred_style in plt.style.available:
        matplotlib.style.use(preferred_style)

    if use_tex and which("latex") is not None:
        p_setting = {
            "pgf.texsystem": "pdflatex",
            "text.usetex": True,
            "pgf.preamble": str(
                r"\usepackage[utf8x]{inputenc} \usepackage[T1]{fontenc}"
                + r"\usepackage[separate -uncertainty=true]{siunitx}"
            ),
        }
    else:
        p_setting = {
            "text.usetex": False,
        }
    matplotlib.rcParams.update(p_setting)


# pylint: disable=too-many-arguments
def label_subplots(
    axs: Sequence[matplotlib.axes.Axes],
    labels: Sequence[str] = [chr(ord("a") + z) for z in range(0, 26)]
    + [chr(ord("A") + z) for z in range(0, 26)],
    start_from: int = 0,
    fontsize: int = 10,
    x_pos: float = 0.02,
    y_pos: float = 0.95,
    override: Optional[Literal["inside", "outside", "default"]] = None,
) -> None:
    """Adds e.g. (a), (b), (c) at the top left of each subplot panel.

    Labelling order achieved through ravelling the input `list` or `np.array`.

    Args:
        axs (Sequence[matplotlib.axes.Axes]): `list` or `np.array` of
            `matplotlib.axes.Axes`.
        labels (Sequence[str]): A sequence of labels for the subplots.
        start_from (int, optional): skips first `start_from` labels. Defaults to 0.
        fontsize (int, optional): Font size for labels. Defaults to 10.
        x_pos (float, optional): Relative x position of labels. Defaults to 0.02.
        y_pos (float, optional): Relative y position of labels. Defaults to 0.95.
        override (Optional[Literal["inside", "outside", "default"]], optional): Choose a
            preset x_pos, y_pos option to overide choices.
            "Outside" is good for busy colormaps. Defaults to None.

    Returns:
        void; alters the `matplotlib.axes.Axes` objects

    Example:
        Here is an example of using this function::

            >>> import matplotlib.pyplot as plt
            >>> from sithom.plot import label_subplots
            >>> fig, axs = plt.subplots(2, 2)
            >>> label_subplots(axs, start_from=0, fontsize=10)
            >>> fig, axs = plt.subplots(2, 2)
            >>> label_subplots(axs, start_from=4, fontsize=10)

    """
    override_d = {"default": "inside", "outside": [-0.12, 1.12], "inside": [0.02, 0.95]}
    if override is not None:
        # allow redirection to keep DRY.
        if not isinstance(override_d[override], list):
            override = override_d[override]
        if override in override_d:
            x_pos = override_d[override][0]
            y_pos = override_d[override][1]

    if isinstance(axs, list):
        axs = np.asarray(axs)
    assert len(axs.ravel()) + start_from <= len(labels)
    subset_labels = []
    for i in range(len(axs.ravel())):
        subset_labels.append(labels[i + start_from])
    for i, label in enumerate(subset_labels):
        axs.ravel()[i].text(
            x_pos,
            y_pos,
            str("(" + label + ")"),
            color="black",
            transform=axs.ravel()[i].transAxes,
            fontsize=fontsize,
            fontweight="bold",
            va="top",
        )


def get_dim(
    width: float = REPORT_WIDTH,
    fraction_of_line_width: float = 1,
    ratio: float = (5**0.5 - 1) / 2,
) -> Tuple[float, float]:
    """Return figure height, width in inches to avoid scaling in latex.

    Default width is `sithom.constants.REPORT_WIDTH`.
    Default ratio is golden ratio, with figure occupying full page width.

    Args:
        width (float, optional): Textwidth of the report to make fontsizes match.
            Defaults to `sithom.constants.REPORT_WIDTH`.
        fraction_of_line_width (float, optional): Fraction of the document width
            which you wish the figure to occupy.  Defaults to 1.
        ratio (float, optional): Fraction of figure width that the figure height
            should be. Defaults to (5 ** 0.5 - 1)/2.

    Returns:
        fig_dim (tuple):
            Dimensions of figure in inches

    Example:
        Here is an example of using this function::

            >>> from sithom.plot import get_dim
            >>> dim_tuple = get_dim(fraction_of_line_width=1, ratio=(5 ** 0.5 - 1) / 2)
            >>> print("({:.2f},".format(dim_tuple[0]), "{:.2f})".format(dim_tuple[1]))
            (5.51, 3.41)

    """

    # Width of figure
    fig_width_pt = width * fraction_of_line_width

    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * ratio

    return (fig_width_in, fig_height_in)


def set_dim(
    fig: matplotlib.figure.Figure,
    width: float = REPORT_WIDTH,
    fraction_of_line_width: float = 1,
    ratio: float = (5**0.5 - 1) / 2,
) -> None:
    """Set aesthetic figure dimensions to avoid scaling in latex.

    Default width is `sithom.constants.REPORT_WIDTH`.
    Default ratio is golden ratio, with figure occupying full page width.

    Args:
        fig (matplotlib.figure.Figure): Figure object to resize.
        width (float): Textwidth of the report to make fontsizes match.
            Defaults to `sithom.constants.REPORT_WIDTH`.
        fraction_of_line_width (float, optional): Fraction of the document width
            which you wish the figure to occupy.  Defaults to 1.
        ratio (float, optional): Fraction of figure width that the figure height
            should be. Defaults to (5 ** 0.5 - 1)/2.

    Returns:
        void; alters current figure to have the desired dimensions

    Example:
        Here is an example of using this function::

            >>> import matplotlib.pyplot as plt
            >>> from sithom.plot import set_dim
            >>> fig, ax = plt.subplots(1, 1)
            >>> set_dim(fig, fraction_of_line_width=1, ratio=(5 ** 0.5 - 1) / 2)

    """
    fig.set_size_inches(
        get_dim(width=width, fraction_of_line_width=fraction_of_line_width, ratio=ratio)
    )


def cmap(variable_name: str) -> matplotlib.colors.LinearSegmentedColormap:
    """Get cmap from a variable name string.

    Ideally colormaps for variables should be consistent
    throughout the project, and changed in this function.
    The colormaps are set to be green where there are NaN values,
    as this has a high contrast with the colormaps used, and
    should ordinarily represent land, unless something has gone wrong.


    Args:
        variable_name (str): name of variable to give colormap.

    Returns:
        matplotlib.colors.LinearSegmentedColormap: sensible colormap

    Example:
        Usage example for sea surface temperature::

            >>> from sithom.plot import cmap
            >>> cmap_t = cmap("sst")
            >>> cmap_t = cmap("u")
            >>> cmap_t = cmap("ranom")

    """

    # make the function case insensitive
    variable_name = variable_name.lower()

    # collate the variables into a smaller number
    map_d = {
        "rain": "rain",
        "ranom": "tarn",
        "tarn": "tarn",
        "u": "speed",
        "v": "speed",
        "speed": "speed",
        "sst": "sst",
        "salt": "haline",
        "sss": "haline",
        "haline": "haline",
        "delta": "delta",
    }

    # map to cmocean colormaps
    cmap_map_d = {
        # pylint: disable=no-member
        "rain": cmocean.cm.rain,
        "tarn": cmocean.cm.tarn,
        "sst": cmocean.cm.thermal,
        "haline": cmocean.cm.haline,
        "speed": cmocean.cm.speed,
        "delta": cmocean.cm.balance,
    }

    # get cmap_t
    cmap_t = cmap_map_d[map_d[variable_name]]

    # make the map green-ish for nan values
    cmap_t.set_bad(color="#15b01a")

    return cmap_t


def axis_formatter() -> matplotlib.ticker.ScalarFormatter:
    """Returns axis formatter for scientific notation.

        Returns:
            matplotlib.ticker.ScalarFormatter: An object to pass in to a
                matplotlib operation.

    Examples:
        Using with xarray::

            >>> import xarray as xr
            >>> from sithom.plot import axis_formatter
            >>> da = xr.tutorial.open_dataset("air_temperature").air
            >>> quadmesh = da.isel(time=0).plot(cbar_kwargs={"format": axis_formatter()})

    """

    fit_obj = matplotlib.ticker.ScalarFormatter(useMathText=True)
    fit_obj.set_scientific(True)
    fit_obj.set_powerlimits((-1, 4))

    return fit_obj


def _balance(vmin: float, vmax: float) -> Tuple[float, float]:
    """Balance vmin, vmax.

    Args:
        vmin (float): Initial colorbar vmin.
        vmax (float): Initial colorbar vmax.

    Returns:
        Tuple[float, float]: balanced colormap.

    Example::
        >>> from sithom.plot import _balance
        >>> _balance(1.4, 2.5)
        (-2.5, 2.5)
        >>> _balance(-1.0, 0.5)
        (-1.0, 1.0)
    """
    assert vmax > vmin
    return float(np.min([-vmax, vmin])), float(np.max([-vmin, vmax]))


def lim(
    npa: np.ndarray, percentile: float = 5, balance: bool = False
) -> Tuple[float, float]:
    """Return colorbar limits.

    Args:
        npa (np.ndarray): A numpy ndarray with values in, including nans.
        percentile (float, optional): Ignoring nans, use 5th and 95th percentile. Defaults to "5perc".
        balance (bool, optional): Whether to balance limits around zero.

    Returns:
        Tuple[float, float]: (vmin, vmax)

    Example with a Gaussian distribution::
        >>> import numpy as np
        >>> from sithom.plot import lim
        >>> samples = np.random.normal(size=(100, 100, 100, 10))
        >>> vmin, vmax = lim(samples)
        >>> print("({:.1f},".format(vmin), "{:.1f})".format(vmax))
        (-1.6, 1.6)
        >>> vmin, vmax = lim(samples + 0.3, balance=True)
        >>> print("({:.1f},".format(vmin), "{:.1f})".format(vmax))
        (-1.9, 1.9)
    """

    vmin = np.nanpercentile(npa, percentile)
    vmax = np.nanpercentile(npa, 100 - percentile)

    assert vmax > vmin

    if balance:
        vmin, vmax = _balance(vmin, vmax)

    return (float(vmin), float(vmax))


def _pairplot_ds(
    ds: xr.Dataset,
    vars: Optional[List[str]] = False,
    label: bool = False,
) -> Tuple[matplotlib.figure.Figure, np.ndarray]:
    """_pairplot_ds for xarray Dataset.

    Args:
        ds (xr.Dataset): Dataset to plot.
        vars (Optional[List[str]], optional): Variables to plot. Defaults to False.
        label (bool, optional): Whether to label the subplots. Defaults to False.

    Returns:
        Tuple[matplotlib.figure.Figure, np.ndarray]: The figure and axes.
    """
    vars = vars if vars else list(ds.data_vars)
    ds = ds[vars]
    rn_dict = {}

    for var in ds:
        if "long_name" in ds[var].attrs:
            rn_dict[var] = ds[var].attrs["long_name"]
        else:
            rn_dict[var] = var
        if "units" in ds[var].attrs:
            rn_dict[var] += " [" + ds[var].attrs["units"] + "]"

    df = ds.rename(rn_dict).to_dataframe()[list(rn_dict.values())]
    return pairplot(df, label=label)


def _float_to_latex(x, precision=2):
    """
    Convert a float x to a LaTeX-formatted string with the given number of significant figures.

    Args:
        x (float): The number to format.
        precision (int): Number of significant figures (default is 2).

    Returns:
        str: A string like "2.2\\times10^{-6}" or "3.1" (if no exponent is needed).
    """
    # Handle the special case of zero.
    if x == 0:
        return "0"

    # Format the number using general format which automatically uses scientific notation when needed.
    s = f"{x:.{precision}g}"

    # If scientific notation is used, s will contain an 'e'
    if "e" in s:
        mantissa, exp = s.split("e")
        # Convert the exponent string to an integer (this removes any extra zeros)
        exp = int(exp)
        # Choose the multiplication symbol.
        mult = "\\times"
        return f"{mantissa}{mult}10^{{{exp}}}"
    else:
        # If no exponent is needed, just return the number inside math mode.
        return f"{s}"


def pairplot(
    inp: Union[xr.Dataset, pd.DataFrame],
    vars: Optional[List[str]] = None,
    label: bool = False,
) -> Tuple[matplotlib.figure.Figure, np.ndarray]:
    """
    Improved seaborn pairplot from:

    https://stackoverflow.com/a/50835066

    The lower triangle of the pairplot shows the scatter plots with the
    correlation coefficient annotated in the top middle of each subplot.
    The diagonal shows the distribution of each of the variables.
    The upper triangle is empty.
    The axs are returned in a 1D array.

    Args:
        inp (Union[xr.Dataset, pd.DataFrame]): A dataset or dataframe to plot.
        vars (Optional[List[str]], optional): Variables to plot. Defaults to None.
        label (bool, optional): Whether to label the subplots. Defaults to False.

    Returns:
        Tuple[matplotlib.figure.Figure, np.ndarray]: The figure and axes.
    """
    if isinstance(inp, xr.Dataset):
        return _pairplot_ds(inp, vars=vars, label=label)
    elif isinstance(inp, pd.DataFrame):
        if vars:
            df = inp[vars]
        else:
            df = inp
    else:
        raise ValueError("Input must be a pandas DataFrame or xarray Dataset.")

    ax_list = []

    def corrfunc(x, y, ax=None, **kws) -> None:
        """Plot the correlation coefficient in the
           top middle of a plot.

        A function to use with seaborn's `map_lower` api.
        """
        corr = ma.corrcoef(ma.masked_invalid(x), ma.masked_invalid(y))
        corr_coeff = corr[0, 1]
        ax = ax or plt.gca()
        ax.annotate(f"ρ = {corr_coeff:.2f}", xy=(0.35, 1.0), xycoords=ax.transAxes)

    # let's also work out the linear regression coefficient using the curve fit

    def gradfunc(x, y, ax=None, **kws) -> None:
        """Plot the linear regression coefficient in the
           top middle of a plot.

        A function to use with seaborn's `map_lower` api.
        """
        # get rid of nan values
        xt, yt = x[~np.isnan(x)], y[~np.isnan(x)]
        xt, yt = xt[~np.isnan(y)], yt[~np.isnan(y)]
        # normalize the data between 0 and 10
        xrange = np.max(xt) - np.min(xt)
        yrange = np.max(yt) - np.min(yt)
        xt = (xt - np.min(xt)) / xrange * 10
        yt = (yt - np.min(yt)) / yrange * 10
        # fit the data with linear fit using OLS
        param, _ = fit(xt, yt)  # defaults to y=mx+c fit
        ax = ax or plt.gca()
        # check if uncertainty is infinite or nan
        if param[0].s in (np.nan, np.inf, -np.inf):
            print(param[0], yrange, xrange)
            if param[0].n not in (np.nan, np.inf, -np.inf):
                m = param[0].n
                ax.annotate(
                    "$m={:}$".format(_float_to_latex(m * yrange / xrange)),
                    xy=(0.35, 0.01),
                    xycoords=ax.transAxes,
                )

        else:
            ax.annotate(
                "$m={:.2eL}$".format(param[0] * yrange / xrange),
                xy=(0.15, 0.01),
                xycoords=ax.transAxes,
            )

    g = sns.pairplot(df, corner=True)
    g.map_lower(corrfunc)
    g.map_lower(gradfunc)

    def get_ax_lower(x, y, ax=None, **kws) -> None:
        nonlocal ax_list
        ax = ax or plt.gca()
        ax_list.append(ax)

    i = -1
    j = -1

    def get_ax_diag(x, ax=None, **kws) -> None:
        nonlocal i
        nonlocal j
        nonlocal ax_list
        i += 1
        j += 1 + i
        ax = ax or plt.gca()
        ax_list.insert(j, ax)

    g.map_lower(get_ax_lower)
    g.map_diag(get_ax_diag)
    if label:
        label_subplots(ax_list, start_from=0, fontsize=10, x_pos=0.06, y_pos=1.03)
    return plt.gcf(), ax_list


def feature_grid(
    ds: xr.Dataset,
    fig_var: List[List[str]],
    units: List[List[str]],
    names: List[List[str]],
    vlim: List[List[Tuple[float, float, str]]],
    super_titles: List[str],
    figsize: Tuple[float, float] = (12, 6),  # in inches
    label_size: int = 12,
    supertitle_pos: Tuple[float, float] = (0.4, 1.3),
    xy: Optional[Tuple[Tuple[str, str, str], Tuple[str, str, str]]] = None,
) -> Tuple[matplotlib.figure.Figure, np.ndarray]:
    """Feature grid plot.

    Args:
        ds (xr.Dataset): Input dataset with single timeslice of data on lon/lat grid.
        fig_var (List[List[str]]): Figure variable names.
        units (List[List[str]]): Units of variables.
        names (List[List[str]]): Names of variables to plot.
        vlim (List[List[Tuple[float, float, str]]]): Colorbar limits, and colorbar cmap.
        super_titles (List[str]): The titles for each column.
        figsize (Tuple[float, float], optional): Defaults to (12, 6). x, y in inches.
        label_size (int, optional): Defaults to 12.
        supertitle_pos (Tuple[float, float], optional): Relative position for titles. Defaults to (0.4, 1.3).
        xy (Optional[Tuple[Tuple[str, str, str], Tuple[str, str, str]]], optional): coord name, display name, unit. Defaults to None.

    Returns:
        Tuple[matplotlib.figure.Figure, np.ndarray]: The figure and axes.
    """
    shape = np.array(fig_var).shape
    fig, axs = plt.subplots(*shape, sharex=True, sharey=True, figsize=figsize)
    if shape[0] == 1:  # expects 2D array
        axs = np.array([axs])
    if shape[1] == 1:
        axs = np.array([axs]).T
    for i in range(shape[0]):
        for j in range(shape[1]):
            ckwargs = {
                "label": "",
                "format": axis_formatter(),
                "extend": "neither",
                "extendrect": False,
                "extendfrac": 0,
            }
            if vlim[i][j] is None:
                if xy is not None:
                    ds[fig_var[i][j]].plot(
                        x=xy[0][0],
                        y=xy[1][0],
                        ax=axs[i, j],
                        cbar_kwargs=ckwargs,
                    )
                else:
                    ds[fig_var[i][j]].plot(
                        ax=axs[i, j],
                        cbar_kwargs=ckwargs,
                    )
            else:
                if xy is not None:
                    ds[fig_var[i][j]].plot(
                        x=xy[0][0],
                        y=xy[1][0],
                        ax=axs[i, j],
                        vmin=vlim[i][j][0],
                        vmax=vlim[i][j][1],
                        cmap=vlim[i][j][2],
                        cbar_kwargs=ckwargs,
                    )
                else:
                    ds[fig_var[i][j]].plot(
                        ax=axs[i, j],
                        vmin=vlim[i][j][0],
                        vmax=vlim[i][j][1],
                        cmap=vlim[i][j][2],
                        cbar_kwargs=ckwargs,
                    )
            axs[i, j].set_title("")
            if units[i][j] == "" or units[i][j] is None:
                axs[i, j].set_title(names[i][j], size=label_size)
            else:
                axs[i, j].set_title(
                    names[i][j] + "  [" + units[i][j] + "]    ", size=label_size
                )
            axs[i, j].set_xlabel("")
            axs[i, j].set_ylabel("")

    if xy is not None:  # label x and y axes
        for i in range(shape[1]):
            axs[shape[0] - 1, i].set_xlabel(xy[0][1] + " [" + xy[0][2] + "]")
        for j in range(shape[0]):
            axs[j, 0].set_ylabel(xy[1][1] + " [" + xy[1][2] + "]")

    def supertitle(j, title):
        axs[0, j].text(
            *supertitle_pos,
            title,
            transform=axs[0, j].transAxes,
            size=label_size + 5,
        )

    for i, title in enumerate(super_titles):
        supertitle(i, title)

    if "time" in ds:
        print(ds.time.values)
        fig.suptitle(ds.time.values)

    return fig, axs


def plot_poly_fit(
    x_values: Sequence[Union[float, int]],
    y_values: Sequence[Union[float, int]],
    reg_type: Literal["lin_0", "lin", "parab", "cubic"] = "lin",
    x_label: str = "x label",
    y_label: str = "y label",
    ext: float = 0.05,
    fig_path: Optional[str] = None,
    ax_format: Optional[Literal["both", "x", "y"]] = "both",
) -> Tuple[unp.uarray, Callable]:
    """
    Plot the polynomial.

    Args:
        x_values (Sequence[Union[float, int]]): The x values to fit.
        y_values (Sequence[Union[float, int]]): The y values to fit.
        reg_type (str, optional): Which regression to do. Defaults to "lin".
        x_label (str, optional): X label for plot. e.g.
            r"$\\Delta \\bar{T}_s$ over tropical pacific (pac) region [$\\Delta$ K]"
        y_label (str): Y labelsfor plot. e.g.
            r"$\\Delta \\bar{T}_s$ over nino3.4 region [$\\Delta$ K]"
        ext: how far in percentage terms to extend beyond data.
        fig_path (Optional[str], optional): Path to stor the figure in.
            Defaults to None.
        ax_format (Literal["both", "x", "y"], optional): which axes to format
            in scientific notation. Defaults to "both".

    Returns:
        Tuple[unp.uarray, Callable]: Paramaters with uncertainty,
            function to put data into.

    Example::
        >>> from sithom.plot import plot_poly_fit as plot
        >>> param, func = plot(
        ...                    [-0.1, 0.5, 1.0, 1.5, 2.3, 2.9, 3.5],
        ...                    [-0.7, 0.1, 0.3, 1.1, 1.5, 2.3, 2.2]
        ...                   )
        >>> "({:.3f}".format(param[0].n) + ", {:.3f})".format(param[0].s)
        '(0.842, 0.078)'
        >>> "({:.3f}".format(param[1].n) + ", {:.3f})".format(param[1].s)
        '(-0.424, 0.161)'
    """
    param, func = fit(x_values, y_values, reg_type=reg_type)
    min_x_data = min(x_values)
    max_x_data = max(x_values)
    min_x_pred = min_x_data - (max_x_data - min_x_data) * ext
    max_x_pred = max_x_data + (max_x_data - min_x_data) * ext
    x_pred = np.linspace(min_x_pred, max_x_pred, num=50)
    y_pred = func(x_pred)
    y_pred_n = unp.nominal_values(y_pred)
    y_pred_s = unp.std_devs(y_pred)
    if len(param) == 1:
        param = list(param)
        param.append(ufloat(0, 0))
    label = label_poly(param)
    plt.fill_between(
        x_pred, y_pred_n + y_pred_s, y_pred_n - y_pred_s, alpha=0.5, color=CAM_BLUE
    )
    plt.plot(x_pred, y_pred_n, label=label, color=BRICK_RED, alpha=0.7)
    plt.scatter(x_values, y_values, color=OX_BLUE, alpha=0.7)

    if ax_format is not None:
        plt.gca().ticklabel_format(
            axis=ax_format, style="sci", scilimits=(0, 0), useMathText=True
        )

    if len(param) >= 3:
        plt.legend(
            bbox_to_anchor=(-0.15, 1.02, 1.15, 0.102),
            loc="lower left",
            mode="expand",
        )
    else:
        plt.legend()

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xlim(min_x_pred, max_x_pred)
    plt.tight_layout()

    if fig_path is not None:
        plt.savefig(fig_path)
    if not in_notebook:
        plt.clf()

    return param, func
