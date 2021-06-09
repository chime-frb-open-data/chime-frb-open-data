import logging
import urllib.request

from cfod import DATA_DIR

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)


def _download(url: str, destination: str) -> None:
    """
    Download a file from a URL .

    Parameters
    ----------
    url : str
        Url to the data product.
    destination : str
        Save path for the downloaded file.
    """
    log.info("Download: Started")
    log.info(f"URL: {url}")
    log.info(f"Destination: {destination}")
    urllib.request.urlretrieve(url, destination)
    log.info("Download: Complete")


def csv_catalog():
    """
    Download CSV catalog.
    """
    url = "https://storage.googleapis.com/chimefrb-dev.appspot.com/catalog1/chimefrbcat1.csv"
    datapath = DATA_DIR / "catalog.csv"
    destination = datapath.absolute().as_posix()
    _download(url, destination)


def fits_catalog():
    """
    Download the fits catalog .
    """
    url = "https://storage.googleapis.com/chimefrb-dev.appspot.com/catalog1/chimefrbcat1.fits"
    datapath = DATA_DIR / "catalog.fits"
    destination = datapath.absolute().as_posix()
    _download(url, destination)


def data_product(url: str) -> None:
    """
    Download data from a URL.

    Parameters
    ----------
    url : str
        URL for the data file.
    """
    datapath = DATA_DIR / url.split("/")[-1]
    destination = datapath.absolute().as_posix()
    _download(url, destination)
