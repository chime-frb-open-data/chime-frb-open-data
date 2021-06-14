import logging
import os
from pathlib import Path

from cfod.routines import catalogs

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)

BASE_DIR: Path = Path(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR: Path = BASE_DIR / "data"
CSV_CATALOG: Path = DATA_DIR / "catalog.csv"
FITS_CATALOG: Path = DATA_DIR / "catalog.fits"

if os.environ["DEBUG"]:
    log.setLevel(logging.DEBUG)
    log.debug("Logging Level: Debug")

if not len(list(DATA_DIR.glob("catalog.*"))):
    from cfod.utilities import fetch

    log.debug("Fetching CHIME/FRB Catalogs")
    fetch.csv_catalog()
    fetch.fits_catalog()

if CSV_CATALOG.exists():
    catalog = catalogs.Catalogs(filename=CSV_CATALOG.absolute().as_posix())
elif FITS_CATALOG.exists():
    catalog = catalogs.Catalogs(filename=FITS_CATALOG.absolute().as_posix())
else:
    log.error("Unable to locate CHIME/FRB Catalog.")
