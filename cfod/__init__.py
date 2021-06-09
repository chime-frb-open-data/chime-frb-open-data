import os
from pathlib import Path

from cfod.routines import catalogs

BASE_DIR: Path = Path(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR: Path = BASE_DIR / "data"

catalog = catalogs.Catalogs()
