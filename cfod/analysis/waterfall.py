from typing import Optional, Tuple

import h5py
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal


def data(filename: str) -> h5py.File:
    """
    Create a h5py File object for the given filename .

    Parameters
    ----------
    filename : str
        Path to the filename.

    Returns
    -------
    h5py.File
        h5py File object.
    """
    return h5py.File(filename, "r")


def contents(data: h5py.File) -> list:
    """
    Returns the list of the contents of a h5py file.

    Parameters
    ----------
    data : h5py.File

    Returns
    -------
    list
    """
    return list(data.keys())


def metadata(data: h5py.File) -> list:
    """
    Returns the metadata for the given CHIME/FRB Waterfall.

    Parameters
    ----------
    data : h5py.File

    Returns
    -------
    list
    """
    return list(data["frb"].attrs)


def data_arrays(data: h5py.File) -> list:
    """
    List of all the FRB data arrays in a file .

    Parameters
    ----------
    data : h5py.File

    Returns
    -------
    list
    """
    return list(data["frb"].keys())


def remove_rfi(
    spec: np.ndarray, wfall: np.ndarray, model_wfall: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Set any frequency channel that has a higher variance than
    the mean variance (averaged across all frequency channels)
    to a np.nan.

    Parameters
    ----------
    spec : np.ndarray
    wfall : np.ndarray
    model_wfall : np.ndarray

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
    """
    q1 = np.nanquantile(spec, 0.25)
    q3 = np.nanquantile(spec, 0.75)
    iqr = q3 - q1

    # additional masking of channels with RFI
    rfi_masking_var_factor = 3

    channel_variance = np.nanvar(wfall, axis=1)
    mean_channel_variance = np.nanmean(channel_variance)

    with np.errstate(invalid="ignore"):
        rfi_mask = (
            (channel_variance > rfi_masking_var_factor * mean_channel_variance)
            | (spec[::-1] < q1 - 1.5 * iqr)
            | (spec[::-1] > q3 + 1.5 * iqr)
        )
    wfall[rfi_mask, ...] = np.nan
    model_wfall[rfi_mask, ...] = np.nan
    spec[rfi_mask[::-1]] = np.nan

    # remake time-series after RFI masking
    ts = np.nansum(wfall, axis=0)
    model_ts = np.nansum(model_wfall, axis=0)

    return ts, model_ts


def boxcar_kernel(width: int) -> np.ndarray:
    """
    Returns the boxcar kernel of given width normalized by
    sqrt(width) for S/N reasons.

    Parameters
    ----------
    width : int
        Width of the boxcar.
    Returns
    -------
    boxcar : np.ndarray
        Boxcar of width `width` normalized by sqrt(width).
    """
    width = int(round(width, 0))
    return np.ones(width, dtype="float32") / np.sqrt(width)


def find_burst(ts, min_width=1, max_width=128) -> Tuple[int, int, float]:
    """
    Find burst peak and width using boxcar convolution.

    Parameters
    ----------
    ts : array_like
        Time-series.
    min_width : int, optional
        Minimum width to search from, in number of time samples.
        1 by default.
    max_width : int, optional
        Maximum width to search up to, in number of time samples.
        128 by default.
    plot : bool, optional
        If True, show figure to summarize burst finding results.
    Returns
    -------
    peak : int
        Index of the peak of the burst in the time-series.
    width : int
        Width of the burst in number of samples.
    snr : float
        S/N of the burst.

    """
    min_width = int(min_width)
    max_width = int(max_width)

    # do not search widths bigger than timeseries
    widths = list(range(min_width, min(max_width + 1, len(ts) - 2)))

    # envelope finding
    snrs = np.empty_like(widths, dtype=float)
    peaks = np.empty_like(widths, dtype=int)

    for i in range(len(widths)):
        convolved = scipy.signal.convolve(ts, boxcar_kernel(widths[i]), mode="same")
        peaks[i] = np.nanargmax(convolved)
        snrs[i] = convolved[peaks[i]]

    best_idx = np.nanargmax(snrs)

    return peaks[best_idx], widths[best_idx], snrs[best_idx]


def bin_freq_channels(data: np.ndarray, fbin_factor: int = 4) -> np.ndarray:
    """
    Bin Data. Sum groups of frequency channels

    Parameters
    ----------
    data : [2D ndarray]
    num_tbin : int, optional
        [number of time samples to bins], by default 100
    fbin_factor : int, optional
        [factor by which frequencies to be binned], by default 1

    Returns
    -------
    [ndarray]

    Raises
    ------
    ValueError
        [frequency binning factor should be even]
    """

    num_chan = data.shape[0]
    if num_chan % fbin_factor != 0:
        raise ValueError("frequency binning factor `fbin_factor` should be even")
    data = np.nanmean(
        data.reshape((num_chan // fbin_factor, fbin_factor) + data.shape[1:]), axis=1
    )
    return data


def plot(
    ts: np.ndarray,
    extent: np.ndarray,
    plot_time: np.ndarray,
    dt: np.float64,
    wfall: np.ndarray,
    spec: np.ndarray,
    plot_freq: np.ndarray,
    scatterfit: bool,
    model_spec: np.ndarray,
    model_ts: np.ndarray,
    peak: int,
    width: int,
    snr: float,
    eventname: str,
    dm: float,
    savepath: Optional[str] = None,
) -> None:
    """
    Plot the time series of the given CHIME/FRB Event Data.


    Parameters
    ----------
    ts : np.ndarray
    extent : np.ndarray
    plot_time : np.ndarray
    dt : np.float64
    wfall : np.ndarray
    spec : np.ndarray
    plot_freq : np.ndarray
    scatterfit : bool
    model_spec : np.ndarray
    model_ts : np.ndarray
    peak : int
    width : int
    snr : float
    eventname : str
    dm : float
    save : bool, optional
    """
    fig = plt.figure(figsize=(6, 6))

    # Set up the image grid
    gs = gridspec.GridSpec(
        ncols=2,
        nrows=2,
        figure=fig,
        width_ratios=[3, 1],
        height_ratios=[1, 3],
        hspace=0.0,
        wspace=0.0,
    )

    data_im = plt.subplot(gs[2])
    data_ts = plt.subplot(gs[0], sharex=data_im)
    data_spec = plt.subplot(gs[3], sharey=data_im)

    # time stamps relative to the peak
    peak_idx = np.argmax(ts)
    extent[0] = extent[0] - plot_time[peak_idx]
    extent[1] = extent[1] - plot_time[peak_idx]
    plot_time -= plot_time[peak_idx]

    # prepare time-series for histogramming
    plot_time -= dt / 2.0
    plot_time = np.append(plot_time, plot_time[-1] + dt)

    cmap = plt.cm.viridis

    # plot dynamic spectrum
    wfall[np.isnan(wfall)] = np.nanmedian(wfall)
    # replace nans in the data with the data median
    # use standard deviation of residuals to set color scale
    vmin = np.nanpercentile(wfall, 1)
    vmax = np.nanpercentile(wfall, 99)

    data_im.imshow(
        wfall,
        aspect="auto",
        interpolation="none",
        extent=extent,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
    )

    # plot time-series
    data_ts.plot(
        plot_time, np.append(ts, ts[-1]), color="tab:gray", drawstyle="steps-post"
    )

    # plot spectrum
    data_spec.plot(spec, plot_freq, color="tab:gray")

    # plot model time-series and spectrum
    if scatterfit:
        data_spec.plot(model_spec, plot_freq, color=cmap(0.25))
        data_ts.plot(
            plot_time,
            np.append(model_ts, model_ts[-1]),
            color=cmap(0.25),
            drawstyle="steps-post",
            lw=2,
        )
    else:
        data_spec.plot(model_spec, plot_freq, color=cmap(0.5))
        data_ts.plot(
            plot_time,
            np.append(model_ts, model_ts[-1]),
            color=cmap(0.5),
            drawstyle="steps-post",
            lw=1,
        )

    # BEautify plot
    # remove some labels and ticks for neatness
    plt.setp(data_ts.get_xticklabels(), visible=False)
    data_ts.set_yticklabels([], visible=True)
    data_ts.set_yticks([])
    data_ts.set_xlim(extent[0], extent[1])
    plt.setp(data_spec.get_yticklabels(), visible=False)
    data_spec.set_xticklabels([], visible=True)
    data_spec.set_xticks([])
    data_spec.set_ylim(extent[2], extent[3])
    plt.setp(data_im.get_xticklabels(), fontsize=9)
    plt.setp(data_im.get_yticklabels(), fontsize=9)

    # highlighting the width of the pulse
    data_ts.axvspan(
        max(plot_time.min(), plot_time[peak] + 0.5 * dt - (0.5 * width) * dt),
        min(plot_time.max(), plot_time[peak] + 0.5 * dt + (0.5 * width) * dt),
        facecolor="tab:blue",
        edgecolor=None,
        alpha=0.1,
    )

    # add event ID and DM labels
    xlim = data_ts.get_xlim()
    ylim = data_ts.get_ylim()

    # add 20% extra white space at the top
    span = np.abs(ylim[1]) + np.abs(ylim[0])
    data_ts.set_ylim(ylim[0], ylim[1] + 0.2 * span)
    ylim = data_ts.get_ylim()

    ypos = (ylim[1] - ylim[0]) * 0.9 + ylim[0]
    xpos = (xlim[1] - xlim[0]) * 0.98 + extent[0]
    data_ts.text(
        xpos,
        ypos,
        f"{eventname}\nDM: {dm:.1f} pc/cc\nSNR: {snr:.2f}",
        ha="right",
        va="top",
        fontsize=9,
    )

    data_im.locator_params(axis="x", min_n_ticks=3)
    data_im.set_yticks([400, 500, 600, 700, 800])
    data_im.set_ylabel("Frequency [MHz]", fontsize=9)
    data_im.set_xlabel("Time [ms]", fontsize=9)
    if savepath:
        plt.savefig(f"{savepath}/{eventname}_wfall.png", dpi=300, bbox_inches="tight")


def cal_plot(
    cal_wfall: np.ndarray,
    dt: np.float64,
    extent: np.ndarray,
    eventname: str,
    cal_source_name: str,
    cal_obs_date: str,
    savepath: Optional[str] = None,
):
    """
    Plot the calibrated CHIME/FRB Event Data.

    Parameters
    ----------
    cal_wfall : np.ndarray
    dt : np.float64
    extent : np.ndarray
    eventname : str
    cal_source_name : str
    cal_obs_date : str
    save : bool, optional
    """
    cal_ts = np.nanmean(cal_wfall, axis=0)
    cal_wfall[np.isnan(cal_wfall)] = np.nanmedian(
        cal_wfall
    )  # replace nans in the data with the data median
    # bin frequency channels such that we have 16,384/16 = 1024 frequency channels
    cal_wfall = bin_freq_channels(cal_wfall, 16)
    vmin = np.nanpercentile(cal_wfall, 1)
    vmax = np.nanpercentile(cal_wfall, 99)

    times = np.arange(len(cal_ts)) * dt
    peak_idx = np.argmax(cal_ts)
    times -= times[peak_idx]
    times -= dt / 2.0

    extent[0] = times[0]
    extent[1] = times[-1]

    fig = plt.figure(figsize=(5, 5), constrained_layout=True)
    layout = """
    A
    C
    """
    ax_dict = fig.subplot_mosaic(layout)
    ax_dict["A"].imshow(cal_wfall, aspect="auto", vmin=vmin, vmax=vmax, extent=extent)
    ax_dict["A"].set_title(
        f"Waterfall of {eventname} \n Calibrated to {cal_source_name} on {cal_obs_date}"
    )
    ax_dict["A"].set_yticks([400, 500, 600, 700, 800])
    ax_dict["C"].plot(times, cal_ts, drawstyle="steps-post")
    ax_dict["C"].set_xlabel("Time [ms]")
    ax_dict["C"].set_title(
        f"Time Series of {eventname} \nCalibrated to {cal_source_name} on {cal_obs_date} \
            \n Peak flux = {cal_ts[peak_idx]:.3f} Jy"
    )
    ax_dict["A"].set_ylabel("Frequency [MHz]")
    ax_dict["C"].set_ylabel("Flux [Jy]")
    if savepath:
        plt.savefig(
            f"{savepath}/{eventname}_cal_wfall.png", dpi=300, bbox_inches="tight"
        )
