"""Sigproc header definitions and tools. Slightly modified version of:
https://github.com/scottransom/presto/blob/master/lib/python/sigproc.py
by Patrick Lazarus.

Ziggy Pleunis, ziggy.pleunis@physics.mcgill.ca

"""

import struct

header_params = {
    "HEADER_START": "flag",
    "telescope_id": "i",
    "machine_id": "i",
    "data_type": "i",
    "rawdatafile": "str",
    "source_name": "str",
    "barycentric": "i",
    "pulsarcentric": "i",
    "az_start": "d",
    "za_start": "d",
    "src_raj": "d",
    "src_dej": "d",
    "tstart": "d",
    "tsamp": "d",
    "nbits": "i",
    "nsamples": "i",
    "nbeams": "i",
    "ibeam": "i",
    "fch1": "d",
    "foff": "d",
    "FREQUENCY_START": "flag",
    "fchannel": "d",
    "FREQUENCY_END": "flag",
    "nchans": "i",
    "nifs": "i",
    "refdm": "d",
    "period": "d",
    "npuls": "q",
    "nbins": "i",
    "HEADER_END": "flag",
}


def prep_string(string):
    return struct.pack("i", len(string)) + string


def prep_double(name, value):
    return prep_string(name) + struct.pack("d", float(value))


def prep_int(name, value):
    return prep_string(name) + struct.pack("i", int(value))


def addto_hdr(parameter, value):
    """Prepare parameter and value for writing to binary file."""
    if header_params[parameter] == "d":
        return prep_double(parameter, value)
    elif header_params[parameter] == "i":
        return prep_int(parameter, value)
    elif header_params[parameter] == "str":
        return prep_string(parameter) + prep_string(value)
    elif header_params[parameter] == "flag":
        return prep_string(parameter)
    else:
        print(f"WARNING key '{parameter}' is unknown!")
