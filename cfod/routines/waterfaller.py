import logging
from typing import Optional

import numpy as np

from cfod.analysis import waterfall

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)


class Waterfaller:
    def __init__(self, filename: str) -> None:
        """
        Initialize the Waterfaller.

        Parameters
        ----------
        filename : str
            h5 file, container the CHIME/FRB waterfall data.
        """
        self.filename = filename
        self.datafile = waterfall.data(filename=self.filename)
        self._unpack()

    def _unpack(self):
        """
        Unpack the attributes of the datafile.
        """
        self.data = self.datafile["frb"]
        self.eventname = self.datafile.attrs["tns_name"].decode()
        self.wfall = self.datafile["wfall"][:]
        self.model_wfall = self.datafile["model_wfall"][:]
        self.plot_time = self.datafile["plot_time"][:]
        self.plot_freq = self.datafile["plot_freq"][:]
        self.ts = self.datafile["ts"][:]
        self.model_ts = self.datafile["model_ts"][:]
        self.spec = self.datafile["spec"][:]
        self.model_spec = self.datafile["model_spec"][:]
        self.extent = self.datafile["extent"][:]
        self.dm = self.datafile.attrs["dm"][()]
        self.scatterfit = self.datafile.attrs["scatterfit"][()]
        self.cal_obs_date = self.datafile.attrs["calibration_observation_date"].decode()
        self.cal_source_name = self.datafile.attrs["calibration_source_name"].decode()
        self.cal_wfall = self.datafile["calibrated_wfall"][:]
        self.dt = np.median(np.diff(self.plot_time))

    @property
    def contents(self) -> list:
        """
        Return the contents of the datafile as a list of strings .

        Returns
        -------
        list
        """
        return waterfall.contents(self.datafile)

    @property
    def metadata(self) -> list:
        """
        Return the metadata for the datafile .

        Returns
        -------
        list
        """
        return waterfall.metadata(self.datafile)

    @property
    def data_arrays(self) -> list:
        """
        List of data arrays in the data file .

        Returns
        -------
        list
        """
        return waterfall.data_arrays(self.datafile)

    def plot(self, savepath: Optional[str] = None):
        """
        Plot the spectrum.

        Parameters
        ----------
        savepath : Optional[str], optional
            If provided, plot saved as {savepath}/{filename}.png, by default None
        """
        log.info("Removing Remaining RFI")
        ts, model_ts = waterfall.remove_rfi(self.spec, self.wfall, self.model_wfall)
        log.info("Determining the peaks and SNR of the pulse")
        peak, width, snr = waterfall.find_burst(ts)
        log.info(f"Peak: {peak}, Width: {width*self.dt} ms, SNR: {snr}")
        wfall = waterfall.bin_freq_channels(self.wfall, fbin_factor=16)
        log.info("Plotting Dynamic Spectrum")
        waterfall.plot(
            ts=ts,
            extent=self.extent,
            plot_time=self.plot_time,
            dt=self.dt,
            wfall=wfall,
            spec=self.spec,
            plot_freq=self.plot_freq,
            scatterfit=self.scatterfit,
            model_spec=self.model_spec,
            model_ts=model_ts,
            peak=peak,
            width=width,
            snr=snr,
            eventname=self.eventname,
            dm=self.dm,
            savepath=savepath,
        )

    def cal_plot(self, savepath: Optional[str] = None):
        """
        Plot the calibrated spectrum.

        Parameters
        ----------
        savepath : Optional[str], optional
            If provided, plot saved as {savepath}/{filename}.png, by default None
        """
        waterfall.cal_plot(
            cal_wfall=self.cal_wfall,
            dt=self.dt,
            extent=self.extent,
            eventname=self.eventname,
            cal_source_name=self.cal_source_name,
            cal_obs_date=self.cal_obs_date,
            savepath=savepath,
        )
