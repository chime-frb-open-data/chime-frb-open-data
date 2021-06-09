""" Creates a HEALPix map from CHIME/FRB Exposure Map."""
import logging

import astropy.units as u
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord

log = logging.getLogger(__name__)


def render(filename: str, save: bool = False, debug: bool = False) -> None:
    """
    Renders CHIME/FRB Exposure Map in Mollweide projection.

    Parameters
    ----------
    filename : str
        Filename of the exposure map.
    debug : bool, optional
        Enables debug logging, by default False
    """
    if debug:
        log.setLevel(logging.DEBUG)
    with np.load(filename) as data:
        exposure = data["exposure"]
        log.debug(f"{filename} opened.")

    # Setting parameters for map resolution
    # Spatial
    nside = 4096
    npix = hp.nside2npix(nside)

    # Temporal
    t_res = 4

    # Initializing a healpy map
    hpxmap = np.zeros(npix, dtype=np.float64)
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

    # Obtaining a lower resolution map ###
    nside_out = 1024
    log.info(
        "Resolution of new map : %.2f arcmin" % (hp.nside2resol(nside_out, arcmin=True))
    )
    # Degrade healpix resolution to nside_out
    hpxmap_dg = hp.ud_grade(hpxmap, nside_out)
    hp.mollview(hpxmap_dg, coord=["C", "G"], norm="log", unit="Hours")
