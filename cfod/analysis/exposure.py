""" Creates a HEALPix map from CHIME/FRB Exposure Map."""
import numpy as np
import matplotlib.pyplot as plt
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import logging

log = logging.getLogger(__name__)


def render(filepath: str) -> None:
    """
    Creates a new HEALPix map from a file and displays it.

    Args:
        filepath (str): Location of the CHIME/FRB exposure map.
    """
    with np.load(filepath) as data:
        exposure = data["exposure"]

    # Setting parameters for map resolution
    # Spatial
    nside = 4096
    npix = hp.nside2npix(nside)

    # Temporal
    t_res = 4

    # Initializing a healpy map
    hpxmap = np.zeros(npix, dtype=np.float)
    hpxmap[0 : len(exposure)] += t_res * exposure / (3600.0)  # seconds to hours
    hpxmap[hpxmap == 0] = hp.UNSEEN  # masking pixels with zero exposure

    # Plotting
    hp.mollview(hpxmap, coord=["C", "G"], norm="log", unit="Hours")
    # Check exposure time in hours for R1 repeater
    coord = SkyCoord("05:31:58.70", "+33:08:52.5", frame="icrs", unit=u.deg)
    log.info(
        "Exposure (in hours): %.2f"
        % hpxmap[hp.ang2pix(nside, coord.ra.deg, coord.dec.deg, lonlat=True)]
    )

    ### Obtaining a lower resolution map ###
    nside_out = 1024
    log.info(
        "Resolution of new map : %.2f arcmin" % (hp.nside2resol(nside_out, arcmin=True))
    )
    # Degrade healpix resolution to nside_out
    hpxmap_dg = hp.ud_grade(hpxmap, nside_out)
    hp.mollview(hpxmap_dg, coord=["C", "G"], norm="log", unit="Hours")
