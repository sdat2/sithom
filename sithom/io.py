"""Helper functions for reading and writing files."""

import json
import codecs
import numpy as np


def jsonize(inp: dict) -> dict:
    """
    JSONize data.

    Args:
        inp (dict): input data.

    Returns:
        dict: output data.

    Examples:
        >>> out = jsonize({"a": np.array([1, 2, 3])})
        >>> isinstance(out["a"], list)
        True
    """
    out = {}
    if isinstance(inp, dict):
        for i in inp:
            if isinstance(inp[i], np.ndarray):
                if (
                    not np.issubdtype(inp[i].dtype, np.float32)
                    and not np.issubdtype(inp[i].dtype, np.float64)
                    and not np.issubdtype(inp[i].dtype, np.float16)
                    and not np.issubdtype(inp[i].dtype, np.integer)
                ):
                    ## make it string
                    out[i] = np.array_str(inp[i])  # .to_list()
                else:
                    out[i] = inp[i].tolist()
            else:
                out[i] = inp[i]
    return out


def read_json(file_name: str) -> object:
    """
    Read JSON file.

    Args:
        file_name (str): file path.

    Returns:
        any: JSON serialized object.
    """
    with codecs.open(file_name, "rb", encoding="utf-8") as handle:
        json_object = json.load(handle)
    return json_object


def write_json(json_object: dict, file_name: str) -> None:
    """
    JSON serizable object to json file

    Args:
        json_object (any): JSON serializable object.
        file_name (str): Path to file.
    """
    with codecs.open(file_name, "w", encoding="utf-8") as handle:
        json.dump(
            jsonize(json_object),
            handle,
            separators=(",", ":"),
            sort_keys=True,
            indent=4,
        )
