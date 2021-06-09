"""CHIME/FRB Catalog."""
import logging
from pathlib import Path
from typing import Optional

from astropy.io import fits

from cfod.utilities import parse

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)


class Catalogs:
    """CHIME/FRB Catalogs."""

    def __init__(self, filename: str, debug: bool = False):
        """
        CHIME/FRB Catalog.

        Parameters
        ----------
        filename : str
            Name of the catalog file.
        """
        if debug:
            log.setLevel(logging.DEBUG)
        self.filename: str = filename
        self.format: Optional[str] = None
        self._filecheck()

    def _filecheck(self, filetypes: list = [".csv", ".fits"]):
        """
        Check if the file exists and is of valid format.

        Parameters
        ----------
        filetypes : list, optional
            Acceptable tile types, by default [".csv", ".fits"]

        Raises
        ------
        FileNotFoundError
            Raised when filename does not exist.
        ValueError
            Raised when filename is not of valid format.
        """
        exists = Path(self.filename).exists()
        suffix = Path(self.filename).suffix
        log.debug(f"File Format: {suffix}")
        if not exists:
            raise FileNotFoundError(f"{self.filename} does not exist.")
        if suffix not in filetypes:
            raise ValueError(f"{self.filename} does not have type {filetypes}.")
        self.format = suffix

    def as_dict(self) -> dict:
        """
        Return the CSV data as a dict.

        Note
        ----
        The format of the dictionary is,
            {
                FRB_NAME : FRB_PROPERTIES
            }

        Returns
        -------
        dict
        """
        self._filecheck(filetypes=[".csv"])
        return parse.csv_to_dict(self.filename)

    def as_json(self) -> str:
        """
        Return the CSV as a JSON string, follows the dictionary format.

        Returns
        -------
        str
        """
        self._filecheck(filetypes=[".csv"])
        return parse.csv_to_json(self.filename)

    def as_list(self) -> list:
        """
        Return a list of the CSV data .

        Returns
        -------
        list
        """
        self._filecheck(filetypes=[".csv"])
        return parse.csv_to_list(filename=self.filename)

    def as_dataframe(self):
        """
        Return the fits data as a pandas dataframe.

        Returns
        -------
        pandas.Dataframe
        """
        self._filecheck(filetypes=[".csv"])
        return parse.fits_to_dataframe(filename=self.filename)

    def as_fits(self) -> fits.HDUList:
        """
        Return a fits HDUList object for the catalog.

        Returns
        -------
        fits.HDUList
            CHIME/FRB Catalog
        """
        self._filecheck(filetypes=[".fits"])
        return fits.open(self.filename)

    def as_ndarray(self) -> NotImplementedError:
        """
        Would return a np.ndarray.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Currently not implemented. PRs are welcomed!")
