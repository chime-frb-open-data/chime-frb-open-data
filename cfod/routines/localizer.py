import logging
from typing import Optional

import h5py as h5

from cfod.analysis import localization

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)


class Localizer:
    def __init__(self, filename: str):
        """
        Initialize localization object.

        Parameters
        ----------
        filename : str
            Path to localization h5 localization data.
        """
        self.filename = filename
        self.datafile = h5.File(filename, "r")

    def describe(self, group: str, attribute: Optional[str], recurse: bool = False):
        """
        Describes a localization data.

        Parameters
        ----------
        group : str
            Name of the root group
        attribute : Optional[str]
            Name of the attribute
        recurse : bool, optional
            by default False

        Example
        -------
        >>> describle("/healpix", "comments")
        """
        if attribute:
            localization.describe(
                group=self.datafile[group].attrs[attribute], recurse=recurse
            )
        else:
            localization.describe(group=self.datafile[group], recurse=recurse)

    def plot(self):
        """
        Plot the localization data.
        """
        localization.plot(data=self.datafile)

    def coutour_plot(self):
        """
        Draw the localization coutour plot
        """
        localization.countours(data=self.datafile)
