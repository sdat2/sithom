"""Polynomial curve fitting."""
from typing import Callable, Tuple, Sequence, Union, Optional, Literal
import numpy as np
from uncertainties import unumpy as unp, ufloat
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from sithom.misc import in_notebook
from sithom.plot import CAM_BLUE, BRICK_RED, OX_BLUE
from sithom.unc import tex_uf

Flt = Union[float, ufloat]


def _cubic(x: float, a: Flt, b: Flt, c: Flt, d: Flt) -> Flt:
    """Fit cubic curve to data"""
    return a * (x ** 3) + b * (x ** 2) + c * x + d


def _parab(x: float, a: Flt, b: Flt, c: Flt) -> Flt:
    """Fit parabola to data."""
    return a * (x ** 2) + b * x + c


def _lin(x: float, a: Flt, b: Flt) -> Flt:
    """Fit line to data using curve_fit."""
    return (a * x) + b


def _lin_0(x: float, a: Flt) -> Flt:
    """Fit line through zero data using curve_fit."""
    return a * x


def _return_func(param: unp.uarray, reg_type: str = "lin") -> Callable:
    """
    Return function so that the linear function only has to be referenced once.

    Args:
        param (np.ndarray): the param.
        reg_type (str, optional): Which fit occured. Defaults to "lin".

    Returns:
        Callable: Function.

    Example of returning the linear function::
        >>> from sithom.curve import _return_func
        >>> func = _return_func(unp.uarray([1, 2], [0.5, 1]), reg_type="lin")
    """

    def lin(x: Sequence[Flt]) -> np.array:
        return _lin(np.array(x), param[0], param[1])

    def lin_0(x: Sequence[Flt]) -> np.array:
        return _lin_0(np.array(x), param[0])

    def parab(x: Sequence[Flt]) -> np.array:
        return _parab(np.array(x), param[0], param[1], param[2])

    def cubic(x: Sequence[Flt]) -> np.array:
        return _cubic(np.array(x), param[0], param[1], param[2], param[3])

    func_dict = {"lin": lin, "lin0": lin_0, "parab": parab, "cubic": cubic}

    assert reg_type in func_dict
    return func_dict[reg_type]


def fit(
    x_npa: Sequence[Union[float, int]],
    y_npa: Sequence[Union[float, int]],
    reg_type: Literal["lin_0", "lin", "parab", "cubic"] = "lin",
) -> Tuple[unp.uarray, Callable]:
    """
    Fit a polynomial curve, with an estimate of the uncertainty.

    Args:
        x_npa (Sequence[Union[float, int]]): The x values to fit.
        y_npa (Sequence[Union[float, int]]): The y values to fit.
        reg_type (str, optional): Which regression to do. Defaults to "lin".

    Returns:
        Tuple[unp.uarray, Callable]: Paramaters with uncertainty,
            and function to put input data into.

    Example of usage::
        >>> import numpy as np
        >>> from sithom.curve import fit
        >>> param, func = fit(np.array([0, 1, 2]), np.array([1, 4, 7]))
        >>> assert np.isclose(param[0].n, 3.0)
        >>> assert np.isclose(param[1].n, 1.00)

    """
    func_dict = {"lin": _lin, "lin0": _lin_0, "parab": _parab, "cubic": _cubic}

    assert reg_type in func_dict

    popt, pcov = curve_fit(func_dict[reg_type], x_npa, y_npa)
    perr = np.sqrt(np.diag(pcov))
    param = unp.uarray(popt, perr)

    return param, _return_func(param, reg_type=reg_type)


def _label(param: Sequence[ufloat]) -> str:
    """Label generator for polynomial.

    Args:
        param (Sequence[ufloat]): Polynomial fit to print out.

    Returns:
        str: Output of polynomial (e.g 'y  = ($2\pm1$) x + 1\pm 2' )

    Examples:
        >>> from sithom.curve import _label
        >>> from uncertainties import ufloat
        >>> _label([ufloat(1, 1), ufloat(1, 1), ufloat(1, 1)])
        'y =  + $\\\\left( 1.0 \\\\pm 1.0 \\\\right)$x$^{2}$ + $\\\\left( 1.0 \\\\pm 1.0 \\\\right)$x + $1.0 \\\\pm 1.0$'
        >>> _label([ufloat(1, 1), ufloat(1, 1), ufloat(0, 0)])
        'y =  + $\\\\left( 1.0 \\\\pm 1.0 \\\\right)$x$^{2}$ + $\\\\left( 1.0 \\\\pm 1.0 \\\\right)$x + $0.0 \\\\pm 0$'
    """
    output = "y = "
    for i in range(len(param)):
        if len(param) - 1 == i:
            output += " + " + tex_uf(param[i], bracket=False, force_latex=True)
        elif len(param) - 2 == i:
            output += " + " + tex_uf(param[i], bracket=True, force_latex=True) + "x"
        else:
            output += (
                " + "
                + tex_uf(param[i], bracket=True, force_latex=True)
                + "x$^{"
                + str(len(param) - 1)
                + "}$"
            )
    return output


def plot(
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
        >>> from sithom.curve import plot
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
    label = _label(param)
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
            bbox_to_anchor=(-0.15, 1.02, 1.15, 0.102), loc="lower left", mode="expand",
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
