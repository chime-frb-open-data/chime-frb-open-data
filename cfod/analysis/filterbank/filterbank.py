"""A module to write filterbank files. Slightly modified version of:
https://github.com/scottransom/presto/blob/master/lib/python/filterbank.py
by Patrick Lazarus.

Ziggy Pleunis, ziggy.pleunis@physics.mcgill.ca

"""

import numpy as np

from cfod.analysis.filterbank import sigproc


def create_filterbank_file(outfile, header, spectra=None, nbits=32, verbose=False):
    """Write filterbank header and spectra to file.

    Parameters
    ----------
    outfile : file
        The filterbank file.
    header : dict
        Dictionary of header parameters and values.
    spectra : Spectra
        Spectra to write to file.
        (Default: don't write any spectra, i.e. write out header only.)
    nbits : int
        The number of bits per sample of the filterbank file. This value
        always overrides the value in the header dictionary.
        (Default: 32, i.e. each sample is a 32-bit float.)
    verbose : bool
        If `True`, be verbose.
        (Default: be quiet.)

    """
    dtype = get_dtype(nbits)
    header["nbits"] = nbits

    if is_float(nbits):
        tinfo = np.finfo(dtype)
    else:
        tinfo = np.iinfo(dtype)
    dtype_min = tinfo.min
    dtype_max = tinfo.max

    outfile.write(sigproc.addto_hdr("HEADER_START", None))

    for parameter in list(header.keys()):
        if parameter not in sigproc.header_params:
            # only add recognized parameters
            continue
        if verbose:
            print(f"Writing header parameter '{parameter}'")
        value = header[parameter]
        outfile.write(sigproc.addto_hdr(parameter, value))

    outfile.write(sigproc.addto_hdr("HEADER_END", None))

    if spectra is not None:
        # CHIME/FRB spectra have shape (channels, time_samples) so tranpose
        data = spectra.T
        nspec, nchans = data.shape
        # first channel in filterbank should be highest frequency, so flip band
        fil_data = np.fliplr(data).ravel()
        np.clip(fil_data, dtype_min, dtype_max, out=fil_data)
        fil_data.tofile(outfile, format=dtype)


def append_spectra(outfile, spectra, nbits=32, verbose=False):
    """Append filterbank spectra to file.

    Parameters
    ----------
    outfile : file
        The filterbank file.
    spectra : Spectra
        Spectra to append to file.
    nbits : int
        The number of bits per sample of the filterbank file. This value
        always overrides the value in the header dictionary.
        (Default: 32, i.e. each sample is a 32-bit float.)
    verbose : bool
        If `True`, be verbose.
        (Default: be quiet.)

    """
    dtype = get_dtype(nbits)
    if is_float(nbits):
        tinfo = np.finfo(dtype)
    else:
        tinfo = np.iinfo(dtype)
    dtype_min = tinfo.min
    dtype_max = tinfo.max

    # CHIME/FRB spectra have shape (channels, time_samples) so tranpose
    data = spectra.T
    nspec, nchans = data.shape
    # first channel in filterbank should be highest frequency so flip band
    fil_data = np.fliplr(data).ravel()
    np.clip(fil_data, dtype_min, dtype_max, out=fil_data)
    # outfile.seek(0, os.SEEK_END)
    outfile.write(fil_data.astype(dtype))


def is_float(nbits):
    """For a given number of bits per sample return `True` if it
    corresponds to floating-point samples in filterbank files.

    Parameters
    ----------
    nbits: int
        Number of bits per sample, as recorded in the filterbank file's
        header.

    Returns
    -------
    isfloat : bool
        `True`, if `nbits` indicates the data in the file are encoded
        as floats.

    """
    check_nbits(nbits)
    if nbits == 32:
        return True
    else:
        return False


def check_nbits(nbits):
    """Given a number of bits per sample check to make sure
    `filterbank.py` can cope with it.

    Parameters
    ----------
    nbits : int
        Number of bits per sample, as recorded in the filterbank file's
        header.

    Raises
    ------
    ValueError
        If `filterbank.py` cannot cope.

    """
    if nbits not in [32, 16, 8]:
        raise ValueError(
            "`filterbank.py` only supports files with 8- or "
            "16-bit integers, or 32-bit floats "
            "(nbits provided: {})!".format(nbits)
        )


def get_dtype(nbits):
    """For a given number of bits per sample return a numpy-recognized
    dtype.

    Parameters
    ----------
    nbits : int
        Number of bits per sample, as recorded in the filterbank file's
        header.

    Returns
    -------
    dtype : dtype
        A numpy dtype string.

    """
    check_nbits(nbits)

    if is_float(nbits):
        dtype = f"float{nbits}"
    else:
        dtype = f"uint%d"

    return dtype
