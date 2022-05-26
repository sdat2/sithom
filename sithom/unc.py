"""Uncertainties utils."""
import numpy as np
import matplotlib
from uncertainties import ufloat


def tex_uf(
    uf: ufloat,
    bracket: bool = False,
    force_latex: bool = False,
    exponential: bool = True,
) -> str:
    """
    A function to take an uncertainties.ufloat, and return a tex containing string
    for plotting, which has the right number of decimal places.

    Args:
        uf (ufloat): The uncertainties ufloat object.
        bracket (bool, optional): Whether or not to add latex brackets around
            the parameter. Defaults to False.
        force_latex (bool, optional): Whether to force latex output.
            Defaults to False. If false will check matplotlib.rcParams first.
        exponential (bool, optional): Whether to put in scientific notation.
            Defaults to True.


    Returns:
        str: String ready to be added to a graph label.
    """
    if exponential:
        e_str = "e"
    else:
        e_str = ""
    dp = round(np.log10(abs(uf.n)) - np.log10(abs(uf.s)))
    # check if Latex is engaged
    if matplotlib.rcParams["text.usetex"] is True or force_latex:
        if bracket:
            fs = "$\\left( {:." + str(dp) + e_str + "L} \\right)$"
        else:
            fs = "${:." + str(dp) + e_str + "L}$"
    else:
        if bracket:
            fs = "({:." + str(dp) + e_str + "P})"
        else:
            fs = "{:." + str(dp) + e_str + "P}"
    return fs.format(uf)
