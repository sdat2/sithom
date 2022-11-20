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
from typing import Sequence, Tuple, Optional, Literal
import itertools
from shutil import which
import numpy as np
import numpy.ma as ma
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn as sns
from jupyterthemes import jtplot
import cmocean
from sithom.misc import in_notebook


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
    matplotlib.style.use("seaborn-colorblind")

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
    labels: Sequence[str] = [chr(ord("`") + z) for z in range(1, 27)],
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
    ratio: float = (5 ** 0.5 - 1) / 2,
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
    ratio: float = (5 ** 0.5 - 1) / 2,
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
    fit_obj.set_powerlimits((0, 0))

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
    return np.min([-vmax, vmin]), np.max([-vmin, vmax])


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
        >>> vmin, vmax = lim(samples, balance=True)
        >>> print("({:.1f},".format(vmin), "{:.1f})".format(vmax))
        (-1.6, 1.6)
    """

    vmin = np.nanpercentile(npa, percentile)
    vmax = np.nanpercentile(npa, 100 - percentile)

    assert vmax > vmin

    if balance:
        _balance(vmin, vmax)

    return (vmin, vmax)


def pairplot(df: pd.DataFrame) -> None:
    """
    Improved seaborn pairplot from:

    https://stackoverflow.com/a/50835066

    Args:
        df (pd.DataFrame): A data frame.
    """

    def corrfunc(x, y, ax=None, **kws) -> None:
        """Plot the correlation coefficient in the
           top left hand corner of a plot.

        A function to use with seaborn's `map_lower` api.
        """
        corr = ma.corrcoef(ma.masked_invalid(x), ma.masked_invalid(y))
        corr_coeff = corr[0, 1]
        ax = ax or plt.gca()
        ax.annotate(f"ρ = {corr_coeff:.2f}", xy=(0.05, 1.0), xycoords=ax.transAxes)

    g = sns.pairplot(df, corner=True)
    g.map_lower(corrfunc)
