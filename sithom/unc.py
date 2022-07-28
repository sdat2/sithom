"""Uncertainties Utilities Module."""
import numpy as np
import matplotlib
from uncertainties import ufloat


def tex_uf(
    ufloat_input: ufloat,
    bracket: bool = False,
    force_latex: bool = False,
    exponential: bool = True,
) -> str:
    """
    A function to take an uncertainties.ufloat, and return a tex containing string
    for plotting, which has the right number of decimal places.

    Args:
        ufloat_input (ufloat): The uncertainties ufloat object.
        bracket (bool, optional): Whether or not to add latex brackets around
            the parameter. Defaults to False.
        force_latex (bool, optional): Whether to force latex output.
            Defaults to False. If false will check matplotlib.rcParams first.
        exponential (bool, optional): Whether to put in scientific notation.
            Defaults to True.

    Returns:
        str: String ready to be added to a graph label.

    Example usage::
        >>> from uncertainties import ufloat
        >>> from sithom.unc import tex_uf
        >>> uf = ufloat(1, 0.5)
        >>> tex_uf(uf, bracket=True, force_latex=True)
            '$\\\\left( 1.0 \\\\pm 0.5 \\\\right)$'
        >>> uf = ufloat(10, 5)
        >>> tex_uf(uf, bracket=True, force_latex=True)
            '$\\\\left( \\\\left(1.0 \\\\pm 0.5\\\\right) \\\\times 10^{1} \\\\right)$'
        >>> tex_uf(ufloat(0.0, 0.0), bracket=True, force_latex=True) # works weirdly
            '$\\\\left( 0.0 \\\\pm 0 \\\\right)$'
        >>> tex_uf(ufloat(2, 0.06), bracket=True, force_latex=True)
            '$\\\\left( 2.0 \\\\pm 0.1 \\\\right)$'

    (Had to add twice as many backslashes for pytest to run.)

    TODO: Fix connsistency to get bullet points right.
    """
    # trying to deal with divide by zero possibility.
    if ufloat_input.n == 0.0:
        exponential_str = ""
    else:
        if exponential and round(np.log10(abs(ufloat_input.n))) != 0:
            exponential_str = "e"
        else:
            exponential_str = ""

    if ufloat_input.n == 0.0 or ufloat_input.s == 0.0:
        decimal_point = 0
    else:
        # ensure that 1 s.f for error means both agree on decimal points.
        decimal_point = round(
            np.log10(abs(ufloat_input.n)) - np.log10(abs(ufloat_input.s))
        )

        # enforce rule that if it starts with a 1, add an extra decimal point.

        if str(ufloat_input.n)[0] == "1":
            if exponential_str == "e":
                decimal_point += 1
            else:
                decimal_point += 2  # weird behaviour

    # check if Latex is engaged
    if matplotlib.rcParams["text.usetex"] is True or force_latex:
        if bracket:
            format_string = (
                "$\\left( {:." + str(decimal_point) + exponential_str + "L} \\right)$"
            )
        else:
            format_string = "${:." + str(decimal_point) + exponential_str + "L}$"
    else:
        if bracket:
            format_string = "({:." + str(decimal_point) + exponential_str + "P})"
        else:
            format_string = "{:." + str(decimal_point) + exponential_str + "P}"
    return format_string.format(ufloat_input)
