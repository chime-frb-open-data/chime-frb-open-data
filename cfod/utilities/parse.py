from csv import DictReader
from json import dumps
from logging import getLogger

log = getLogger(__name__)


def fits_to_dataframe(filename):
    try:
        import pandas as pd
    except ImportError as error:
        log.error(error)
        log.error("Run 'pip install cfod[pandas]'")
        raise error
    columns = [
        "tns_name",
        "previous_name",
        "repeater_name",
        "ra",
        "ra_err",
        "ra_notes",
        "dec",
        "dec_err",
        "dec_notes",
        "gl",
        "gb",
        "exp_up",
        "exp_up_err",
        "exp_up_notes",
        "exp_low",
        "exp_low_err",
        "exp_low_notes",
        "bonsai_snr",
        "bonsai_dm",
        "low_ft_68",
        "up_ft_68",
        "low_ft_95",
        "up_ft_95",
        "snr_fitb",
        "dm_fitb",
        "dm_fitb_err",
        "dm_exc_ne2001",
        "dm_exc_ymw16",
        "bc_width",
        "scat_time",
        "scat_time_err",
        "flux",
        "flux_err",
        "flux_notes",
        "fluence",
        "fluence_err",
        "fluence_notes",
        "sub_num",
        "mjd_400",
        "mjd_400_err",
        "mjd_inf",
        "mjd_inf_err",
        "width_fitb",
        "width_fitb_err",
        "sp_idx",
        "sp_idx_err",
        "sp_run",
        "sp_run_err",
        "high_freq",
        "low_freq",
        "peak_freq",
        "excluded_flag",
    ]
    return pd.read_csv(filename, usecols=columns)


def csv_to_list(filename: str) -> list:
    reader = DictReader(open(filename))
    data = []
    for datapoint in reader:
        data.append(datapoint)
    return data


def csv_to_dict(filename: str) -> dict:
    reader = DictReader(open(filename))
    data = {}
    for datapoint in reader:
        data[datapoint["tns_name"]] = datapoint
    return data


def csv_to_json(filename: str) -> str:
    dictionary = csv_to_dict(filename)
    return dumps(dictionary)
