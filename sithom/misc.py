"""Miscillanious Utilities Module."""

from typing import Optional
import inspect
from sys import getsizeof
import subprocess


def in_notebook() -> bool:
    """
    Check if in jupyter notebook.

    Taken from this answer:
    https://stackoverflow.com/a/22424821

    Returns:
        bool: whether in jupyter notebook.

    Example of triggering from python terminal::
        >>> from sithom.misc import in_notebook
        >>> in_notebook()
        False
    """
    try:
        # pylint: disable=import-outside-toplevel
        from IPython import get_ipython

        if "IPKernelApp" not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


def human_readable_size(num: int, suffix: str = "B") -> str:
    """Convert a number of bytes into human readable format.

    This function is meant as a helper function for `get_byte_size`.

    Args:
        num (int): The number of bytes to convert
        suffix (str, optional): The suffix to use for bytes. Defaults to 'B'.

    Returns:
        str: A human readable version of the number of bytes.

    Example of using human readable sizes::
        >>> from sithom.misc import human_readable_size
        >>> assert human_readable_size(int(10e5)) == "977 KB"
        >>> assert human_readable_size(int(10e13)) == "91 TB"
    """
    assert num >= 0, "Size cannot be negative."
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if num < 1024:
            return f"{num:.0f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:1f} Y{suffix}"


def calculate_byte_size_recursively(obj: object, seen: set = None) -> int:
    """Recursively calculate size of objects in memory in bytes.

    From: https://github.com/bosswissam/pysize.
    Meant as a helper function for `get_byte_size`.

    Args:
        obj (object): The python object to get the size of
        seen (set, optional): This variable is needed to for the recusrive
            function evaluations, to ensure each object only gets counted once.
            Leave it at "None" to get the full byte size of an object. Defaults to None.

    Returns:
        int: The size of the object in bytes.
    """

    # Note: getsizeof alone is not enough, as it only returns the size of the top
    #  level object, not of its member variables/objects. Hence the recursive calls.
    size = getsizeof(obj)
    if seen is None:
        # At first iteration (top level object), initialize 'seen' as empty set
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        # If object was already counted, return 0 size to avoid double counting.
        return 0

    # Important: Mark as seen *before* entering recursion to handle
    # self-referential objects
    seen.add(obj_id)

    if hasattr(obj, "__dict__"):
        # handles class objects
        for cls in obj.__class__.__mro__:
            if "__dict__" in cls.__dict__:
                dictionary = cls.__dict__["__dict__"]
                if inspect.isgetsetdescriptor(dictionary) or inspect.ismemberdescriptor(
                    dictionary
                ):
                    # Recursively calculate size of member objects & variables
                    size += calculate_byte_size_recursively(obj.__dict__, seen)
                break

    if isinstance(obj, dict):
        # handles dictionaries
        size += sum((calculate_byte_size_recursively(v, seen) for v in obj.values()))
        size += sum((calculate_byte_size_recursively(k, seen) for k in obj.keys()))
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        # handles array like objects (need to exclude str, bytes bytearray since they
        #  also implement __iter__)
        size += sum((calculate_byte_size_recursively(i, seen) for i in obj))

    if hasattr(obj, "__slots__"):  # can have __slots__ with __dict__
        size += sum(
            calculate_byte_size_recursively(getattr(obj, s), seen)
            for s in obj.__slots__
            if hasattr(obj, s)
        )
    return size


def get_byte_size(obj: object) -> str:
    """Return human readable size of a python object in bytes.

    Args:
        obj (object): The python object to analyse

    Returns:
        str: Human readable string with the size of the object

    Examples of using for numpy array::
        >>> import numpy as np
        >>> from sithom.misc import get_byte_size
        >>> assert isinstance(get_byte_size(np.zeros(int(10e4))), str)
    """
    return human_readable_size(calculate_byte_size_recursively(obj))


def get_git_revision_hash(path: Optional[str] = None) -> str:
    """Get the git revision hash.

    Args:
        path (Optional[str], optional): The path to the git repository. Defaults to None.
            If None then check use current path.

    Returns:
        str: The git revision hash.
    """
    git_command = ["git", "rev-parse", "HEAD"]
    if path:
        # Add the --git-dir option if a path is provided
        git_command = ["git", "--git-dir", f"{path}/.git", "rev-parse", "HEAD"]
    return subprocess.check_output(git_command).decode("ascii").strip()
