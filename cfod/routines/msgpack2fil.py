#!/bin/python

"""Script to convert a list of CHIME/FRB msgpack files to a filterbank file.

Ziggy Pleunis, ziggy.pleunis@physics.mcgill.ca

"""

import glob
import os

import click
import numpy as np

from cfod.analysis.filterbank import filterbank
from cfod.analysis.intensity import chime_intensity

# 16K channels, 1024 samples, intensity + weights, 32-bits = 4 bytes
MSGPACK_SIZE = 16e3 * 1024 * 2 * 4
SCRUNCH_FACTORS = [
    1,
    2,
    4,
    8,
    16,
    32,
    64,
    128,
    256,
    512,
    1024,
    2048,
    4096,
    8192,
    16384,
]


def filterbank_header(obsglob, dt, ftop, fbottom, nchan, source):
    """Create a filterbank header.

    Returns
    -------
    fil_header : dict
        Header in the filterbank format.

    Notes
    -----
    Basic implementation with a lot of unfilled header variables.

    """
    fil_header = {}
    fil_header["telescope_id"] = 20  # number for CHIME
    fil_header["machine_id"] = 20  # number for CHIME/FRB backend
    fil_header["data_type"] = 1  # filterbank
    # PRESTO and sigproc read at most 80 characters for header messages
    fil_header["rawdatafile"] = obsglob[:80]
    fil_header["source_name"] = source
    fil_header["barycentric"] = 0
    fil_header["pulsarcentric"] = 0
    fil_header["az_start"] = 0.0  # degrees
    fil_header["za_start"] = 0.0  # degrees
    fil_header["src_raj"] = 0.0  # [hhmmss.s]
    fil_header["src_dej"] = 0.0  # [ddmmss.s]
    fil_header["tstart"] = 0.0  # MJD
    fil_header["tsamp"] = dt  # s
    fil_header["nbits"] = 32
    fil_header["nbeams"] = 1
    fil_header["ibeam"] = 0
    # first channel `fch1` in sigproc is the highest frequency
    # `foff` is negative to signify this
    channel_bandwidth = float(np.abs(ftop - fbottom)) / nchan
    fil_header["fch1"] = ftop - channel_bandwidth / 2.0  # MHz
    fil_header["foff"] = -1.0 * channel_bandwidth  # MHz
    fil_header["nchans"] = nchan
    fil_header["nifs"] = 1

    return fil_header


def average(a, axis=None, weights=None):
    """Same as np.average, EXCEPT, if weights are all zero, it will
    return zero in the average without giving an error.

    Parameters
    ----------
    a : array_like
        The array to take the average off.
    axis : int, optional
        The axis to calculate the average over.
    weights : array_like, optional
        Data weights. Use equal weighting by default.

    Returns
    -------
    float
        The array average over the provided axis.

    """
    assert a.ndim >= 2

    if weights is None:
        weights = np.ones(a.shape, dtype=np.float)

    weight_sums = np.sum(weights, axis=axis)

    non_zero = np.where(weight_sums > 0)
    avg = np.zeros_like(weight_sums)
    avg[non_zero] = np.sum(a * weights, axis=axis)[non_zero] / weight_sums[non_zero]

    return avg, weight_sums


def delay_from_dm(dm, freq_emitted):
    """Return the delay in seconds caused by dispersion in the
    interstellar medium.

    Parameters
    ----------
    dm : float
        Dispersion measure, in pc cm-3.
    freq_emitted : float
        Observing frequency, in MHz.

    Returns
    -------
    float
        Dispersive delay, in seconds.

    """
    if isinstance(freq_emitted, float):
        if freq_emitted > 0.0:
            return dm / (0.000241 * freq_emitted * freq_emitted)
        else:
            return 0.0
    else:
        return np.where(
            freq_emitted > 0.0,
            dm / (0.000241 * freq_emitted * freq_emitted),
            0.0,
        )


def convert_chunk(msg_chunk, fscrunch=1, subdm=None):
    # load a list of msgpack files
    (
        intensity,
        weights,
        fpga0s,
        fpgaNs,
        binning,
        rfi_masks,
        frame0_nanos,
    ) = chime_intensity.unpack_datafiles(msg_chunk)

    dt = chime_intensity.dt * binning

    if fscrunch not in SCRUNCH_FACTORS:
        fscrunch = 4
        print("WARNING fscrunch is not a factor of 2.. setting it to 4!")

    nsub = 16384 / fscrunch
    # give warning when nchan > 4096
    if nsub > 4096:
        print(
            "WARNING sigproc spectrum lengths are capped at 4096 "
            + "channels by default, need to update `reader.h` and "
            + "`header.h` and recompile before reading this file!"
        )

    nchan = intensity.shape[0]

    nchan_per_sub = nchan / nsub

    # update frequency channel width
    df = nchan_per_sub * chime_intensity.df

    if nchan != nsub:
        old_frequencies = np.arange(
            chime_intensity.fbottom, chime_intensity.ftop, chime_intensity.df
        )
        old_center_frequencies = old_frequencies + chime_intensity.df / 2.0

        # calculate subband frequencies for subband dedispersion
        new_frequencies = np.arange(chime_intensity.fbottom, chime_intensity.ftop, df)
        new_center_frequencies = new_frequencies + df / 2.0

        # dedisperse channels *within* subbands to `subdm`
        if subdm is not None:
            # compute delays
            rel_delays = delay_from_dm(subdm, new_center_frequencies)
            delays = delay_from_dm(subdm, old_center_frequencies)
            # relative delays
            rel_delays = delays - rel_delays.repeat(nchan_per_sub)
            rel_bindelays = np.round(rel_delays / dt).astype("int")
            # shift channels
            for ii in range(nchan):
                # rotate channels
                intensity[ii, :] = np.roll(intensity[ii, :], -rel_bindelays[ii], axis=0)
                weights[ii, :] = np.roll(weights[ii, :], -rel_bindelays[ii], axis=0)

                # zero out rotated values in the weights array
                if rel_bindelays[ii] > 0:
                    weights[ii, -rel_bindelays[ii] :] = 0.0
                elif rel_bindelays[ii] < 0:
                    weights[ii, : -rel_bindelays[ii]] = 0.0

        # subband
        intensity = np.array(
            [
                average(sub, axis=0, weights=sub_weights)[0]
                for sub, sub_weights in zip(
                    np.vsplit(intensity, nsub), np.vsplit(weights, nsub)
                )
            ]
        )
        weights = np.array(
            [np.mean(weights, axis=0) for weights in np.vsplit(weights, nsub)]
        )

    return intensity, weights, dt, df


def msgpack2fil(fout, obsglob, fscrunch, subdm, source, ram):
    """Convert a list of CHIME/FRB msgpack files to a filterbank file.

    Parameters
    ----------
    fout : str
        Filterbank file name to write out, '.fil' is appended if missing.
    obsglob : str
        Unix pathname wildcard to .msgpack files to be converted.
    fscrunch : int
        Frequency scrunch factor, or the numbers of channels that will be
        scrunched together into one subband. Needs to be a power of 2.
    subdm : float
        Disperions measure, in pc cm-3, that channels withing a subband will
        be dedispersed to to avoid subband smearing. NB the filterbank file
        wil still be at DM=0.
    source : str
        Name of the source in the observation that will be put in the
        filterbank header.
    ram : float
        Random access memory available, in bytes, on your machine; used to
        calculate the chunk size of file reads. NB '8e9' for 8GB, etc.

    """
    # add extension to filename if it is not already there
    if fout[-4:] != ".fil":
        fout += ".fil"

    msg = glob.glob(obsglob)
    msg.sort(key=chime_intensity.natural_keys)

    if len(msg) == 0:
        print(f"No files found for wildcard '{obsglob}'..")
        return

    # indices of chunk number is different for `.msg` and `.msgpack` files
    _, extension = os.path.splitext(msg[0])
    if extension == ".msg":
        chidx1 = -12
        chidx2 = -4
    if extension == ".msgpack":
        chidx1 = -19
        chidx2 = -11

    # use 50% of availabe RAM; need 3x the msgpack size
    chunk_size = int(0.5 * ram / MSGPACK_SIZE / 3.0)

    limits = range(0, len(msg), chunk_size)
    limits.append(len(msg))

    reads = len(limits) - 1

    for i in range(reads):
        print("Reading {} of {} msgpack chunks..".format(i + 1, reads))

        msg_chunk = msg[limits[i] : limits[i + 1]]

        intensity, weights, dt, df = convert_chunk(
            msg_chunk, fscrunch=fscrunch, subdm=subdm
        )

        if i > 0:
            print(f"Appending to filterbank file '{fout}'..")
            filterbank.append_spectra(outfile, intensity * weights)
        else:
            print(f"Creating filterbank file '{fout}'..")
            outfile = open(fout, "wb")
            fil_header = filterbank_header(
                obsglob,
                dt,
                chime_intensity.ftop,
                chime_intensity.fbottom,
                intensity.shape[0],
                source,
            )
            filterbank.create_filterbank_file(outfile, fil_header, intensity * weights)

    outfile.close()
    return


@click.command()
@click.option(
    "-o",
    "--outfile",
    "fout",
    default="chimefrb.fil",
    type=click.STRING,
    help="Filterbank file name.",
)
@click.option(
    "--obsglob",
    default="./*.msgpack",
    type=click.STRING,
    help="Glob for the observation msgpack files in quotes.",
)
@click.option(
    "--fscrunch",
    default=4,
    type=click.INT,
    help="Frequency scrunch factor, needs to be a power of 2.",
)
@click.option(
    "--subdm",
    default=None,
    type=click.FLOAT,
    help="Before subbanding dedisperse subband channels to this DM.",
)
@click.option(
    "--source",
    default="CHIME/FRB candidate",
    type=click.STRING,
    help="Name of the source that is in the observation.",
)
@click.option(
    "--ram",
    default=8e9,
    type=click.FLOAT,
    help="RAM available, in bytes. 8GB by default.",
)
def runner(fout, obsglob, fscrunch, subdm, source, ram):
    msgpack2fil(fout, obsglob, fscrunch, subdm, source, ram)


if __name__ == "__main__":
    runner()
