"""Place objects."""
import numpy as np
from typing import List
import matplotlib.axes


class BoundingBox:
    """
    BoundingBox class to deal with the varying output requirments often needed to
    describe the same geographical box to different APIs.

    Example::
        >>> from sithom.place import BoundingBox
        >>> bbox = BoundingBox([-30, 30], [10, 30], desc="")
        >>> bbox.cartopy() # [lon-, lon+, lat-, lat+]
        [-30, 30, 10, 30]
        >>> bbox.ecmwf() # [lat+, lon-, lat-, lon+]
        [30, -30, 10, 30]
    """

    def __init__(self, lon: List[float], lat: List[float], desc: str = "No Description Given.") -> None:
        """
        Create BBOX.

        Args:
            lon (List[float]): Longitude bounds. Degrees East.
            lat (List[float]): Latitude bounds. Degrees North.
            desc (str): Description of boundary box for debugging. Defaults to "No Description Given.".
        """
        assert len(lon) == 2
        assert len(lat) == 2
        self.lon = lon
        self.lat = lat
        self.desc = desc

    def __repr__(self) -> str:
        """
        Representation string.
        """
        return str(
            [
                ("Latitude bounds", self.lat, "degrees_north"),
                ("Longitude bounds", self.lon, "degrees_east"),
                self.desc,
            ]
        )

    def cartopy(self) -> List[float]:
        """
        Cartopy style bounding box.

        Returns:
            List[float]: [lon-, lon+, lat-, lat+] # [degE, degE, degN, degN]
        """
        return self.lon + self.lat

    def ecmwf(self) -> List[float]:
        """
        ECMWF style bounding box.

        Returns:
            List[float]: [lat+, lon-, lat-, lon+] # [degN, degE, degN, degE]
        """
        return [self.lat[1], self.lon[0], self.lat[0], self.lon[1]]

    def ax_lim(self, ax: matplotlib.axes.Axes) -> None:
        """
        Apply BoundingBox as ax limit to your graph.

        Args:
            ax (matplotlib.axes.Axes): Axes to limit.
        """
        ax.set_xlim(self.lon)
        ax.set_ylim(self.lat)


    def ax_label(self, ax: matplotlib.axes.Axes) -> None:
        """
        Apply BoundingBox as labels to your graph.

        Args:
            ax (matplotlib.axes.Axes): Axes to limit.
        """
        ax.set_xlabel(self.lon)
        ax.set_ylabel(self.lat)

    def pad(self, buffer: float = 1) -> "BoundingBox":
        """
        Pad the BoundingBox by some number of degrees.

        Args:
            buffer (float, optional): How many degrees East and North
                to go out from existing buffer. Defaults to 1.

        Returns:
            BoundingBox: A bounding box that is padded by the buffer.
        """
        return BoundingBox([self.lon[0] - buffer, self.lon[1] + buffer], 
                            [self.lat[0] - buffer, self.lat[1] + buffer], 
                            desc=self.desc + " padded by " + str(buffer) + " degrees")

    def indices_inside(self, lons: np.ndarray, lats: np.ndarray) -> np.ndarray:
        """
        Get indices of points inside the bounding box.

        Args:
            lons (np.ndarray): Longitudes of points to check.
            lats (np.ndarray): Latitudes of points to check.

        Returns:
            np.ndarray: Indices of points inside the bounding box.
        """
        return np.where(
            (lons >= self.lon[0])
            & (lons <= self.lon[1])
            & (lats >= self.lat[0])
            & (lats <= self.lat[1]))


class Point:
    def __init__(self, lon: float, lat: float, desc: str = "No Description Given.") -> None:
        """
        Initialise point.

        Args:
            lon (float): Longitude. Degrees East.
            lat (float): Latitude. Degrees North.
            desc (str): description. Defaults to "No Description Given.".
        """
        self.lon = lon
        self.lat = lat
        self.desc = desc

    def __repr__(self) -> str:
        """
        Representation string.
        """
        return str(
            [
                ("Latitude", self.lat, "degrees_north"),
                ("Longitude", self.lon, "degrees_east"),
                self.desc,
            ]
        )

    def bbox(self, buffer: float = 3) -> BoundingBox:
        """
        Get `BoundingBox` by padding around the `Point` by the buffer of some number of degrees.

        Size of the square is 4 * buffer**2.

        Args:
            buffer (float, optional): How many degrees East and North
                to go out from loc. Defaults to 3.

        Returns:
            BoundingBox: A bounding box like [-91.0715, 28.9511, -89.0715, 30.9511].

        Example::
            >>> from sithom.place import Point
            >>> point = Point(20, 30)
            >>> bbox = point.bbox(2)
            >>> bbox.cartopy() # [lon-, lon+, lat-, lat+]
            [18, 22, 28, 32]
            >>> bbox.ecmwf() # [lat+, lon-, lat-, lon+]
            [32, 18, 28, 22]

        """
        return BoundingBox(
            [self.lon - buffer, self.lon + buffer],
            [self.lat - buffer, self.lat + buffer],
            desc="Bounding Box around point: " + self.desc,
        )
