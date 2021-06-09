# CHIME/FRB Open Data

Read utilties for CHIME/FRB Open Data Release.

## Installation
```
pip install cfod
```


## Usage
To read a single data file from the data release,
```python
from cfod import chime_intensity as ci

fn = ` astro_5941664_20180406203904337770_beam0147_00245439_02.msgpack `
(
    intensity,
    weights,
    fpga0,
    fpgaN,
    binning,
    frame0_nano,
    nrfifreq,
    rfi_mask,
) = ci.unpack_data(fn)
```
where:
  - `intensity` is a 2D Intensity array.
  - `weights ` are the corresponding 2D array weights to the intensity array.
  - `fpga0 (int)` is start fpga count of the data chunk. (Internally used to track time, can be ignored). The fpga count increments at the rate of 2.56us.
  - `fpgaN (int)` is number of fpga counts in the data chunk read
  - `binning (int)` is the downsampling of the data from the ringbuffer
  - `frame0_nano` is the conversion from fpga timestamp to utc timestamp (Currently not supported.)
  - `nrfifreq` is the number of frequences masked by the realtime rfi system (Currently not supported.)
  - `rfi_mask` is currently not supported

To read multiple data files at once, you can use the following command,
```python
from cfod import chime_intensity as ci

fns = ["file1", "file2", "file3"]
(
    intensity,
    weights,
    fpga0s,
    fpgaNs,
    binning,
    rfi_mask,
    frame0_nanos,
) = ci.unpack_datafiles(fns)
```

To convert `.msgpack` files into filterbank `.fil` format you can run `msgpack2fil` from the command line (scripts are installed through `pip`). You need to provide a pathname wildcard in quotation marks. To see all command line options run help:
```
msgpack2fil --help
```
CHIME/FRB data has 16384 frequency channels but PRESTO and sigproc by default allocate memory for only a maximum of 4096 channels. You would need to update `reader.h` and `header.h` in sigproc and recompile before trying to read a 16384 filterbank file, or you can let `msgpack2fil` subband data by at least a factor 4 (using the `--fscrunch` argument). Make sure to provide a DM for subband dedispersion (using the `--subdm` argument) to mitigate subband smearing.

## Removal
```
pip uninstall cfod
```
