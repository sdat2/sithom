"""Polynomial curve fitting.

TODO: Could be improved so that we just have to referenc a polynomial by a boolean list:
    [True, False, False] -> [1, 0, 0] -> a * x**2
    [True, False, True] -> [1, 0, 1] -> a * x**2 + b 
    etc.

TODO: Could be improved by normalizing the input data, so that the fit is more stable.
"""

from typing import Callable, Tuple, Sequence, Union, Literal
import numpy as np
from uncertainties import unumpy as unp, ufloat
from scipy.optimize import curve_fit
from .unc import tex_uf

Flt = Union[float, ufloat]


def _cubic(x: float, a: Flt, b: Flt, c: Flt, d: Flt) -> Flt:
    """Fit cubic curve to data"""
    return a * (x**3) + b * (x**2) + c * x + d


def _parab(x: float, a: Flt, b: Flt, c: Flt) -> Flt:
    """Fit parabola to data."""
    return a * (x**2) + b * x + c


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


def label_poly(param: Sequence[ufloat]) -> str:
    """Label generator for polynomial.

    Args:
        param (Sequence[ufloat]): Polynomial fit to print out.

    Returns:
        str: Output of polynomial (e.g 'y  = ($2\\\\pm1$) x + 1\\\\pm 2' )

    Examples:
        >>> from sithom.curve import label_poly
        >>> from uncertainties import ufloat
        >>> label_poly([ufloat(1, 1), ufloat(1, 1), ufloat(1, 1)])
        'y =  + $\\\\left( 1.0 \\\\pm 1.0 \\\\right)$x$^{2}$ + $\\\\left( 1.0 \\\\pm 1.0 \\\\right)$x + $1.0 \\\\pm 1.0$'
        >>> label_poly([ufloat(1, 1), ufloat(1, 1), ufloat(0, 0)])
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

