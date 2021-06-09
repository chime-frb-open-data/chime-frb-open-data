"""Functions to handle CHIME/FRB intensity data."""


import numpy as np

from cfod.analysis.intensity import assemble_chunk

# CHIME/FRB Constants

# ADC sampling frequency, in MSPS or Hz
adc_sampling_freq = float(800e6)
# number of samples in the initial FFT
fpga_num_samp_fft = 2048
# parameters for alias sampling in second Nyquist zone
fpga_num_freq = fpga_num_samp_fft / 2
# bin centre of the highest frequency channel
fpga_freq0_mhz = adc_sampling_freq / 1e6
# channel bandwidth
fpga_delta_freq_mhz = -adc_sampling_freq / 2 / fpga_num_freq / 1e6
# top of the highest-frequency channel
# (NB the FGPA-channel around 800 MHz is contaminated by aliasing)
freq_top_mhz = fpga_freq0_mhz - fpga_delta_freq_mhz / 2.0
# bottom of the lowest-frequency channel
freq_bottom_mhz = freq_top_mhz - adc_sampling_freq / 2.0 / 1e6
# bin centres of FPGA channels, in MHz (ordered 800 to 400 MHz)
fpga_freq = np.linspace(
    fpga_freq0_mhz, fpga_freq0_mhz / 2.0, num=round(fpga_num_freq), endpoint=False
)

# X-engine
# upchannelization
l0_upchan_factor = 16
l0_num_frames_sample = 8 * 3
# CHIME/FRB output data parameters
num_channels = fpga_num_freq * l0_upchan_factor
channel_bandwidth_mhz = adc_sampling_freq / 2 / num_channels / 1e6
fpga_frequency_hz = adc_sampling_freq / fpga_num_samp_fft
sampling_time_ms = (
    1.0 / fpga_frequency_hz * l0_upchan_factor * l0_num_frames_sample
) * 1e3
fpga_counts_per_sample = int(sampling_time_ms / 1e3 / (1.0 / fpga_frequency_hz))

# bin centres of L0 channels, in MHz (ordered 400 to 800 MHz)
freq = np.arange(
    freq_bottom_mhz + channel_bandwidth_mhz / 2.0, freq_top_mhz, channel_bandwidth_mhz
)
bandwidth = adc_sampling_freq / 1e6 / 2.0  # MHz
fbottom = freq_bottom_mhz  # MHz
ftop = freq_top_mhz  # MHz
df = channel_bandwidth_mhz  # MHz
dt = sampling_time_ms / 1e3  # s
nchan = num_channels
fpga_counts_per_sample = fpga_counts_per_sample


def unpack_data(fn):
    """
    Unpacks and de-compresses Intensity and Weights from the
    L1 call-back data.
    Parameters
    ----------
    fn : string
        Filename of the function to unpack.
        For CHIME/FRB this has the following format:
        astro_5941664_20180406203904337770_beam0147_00245439_02.msgpack
              event_no_YYYYMMDDHHMMSSssss_beamxxxx_something_binning.msgpack
    Returns
    -------
    intensity : 2D array
        A 2D Intensity array.
    weights : 2D array
        Corresponding weights to the intensity array.
    fpga0 : int
        Start fpga count of that chunk.
    fpgaN : int
        number of fpga counts in that chunk.
    binning : int
        Downsampling of the data from the ringbuffer
    """

    chunk = assemble_chunk.read_msgpack_file(fn)
    intensity, weights = chunk.decode()
    frame0_nano = None
    nrfifreq = None
    rfi_mask = np.ones_like(intensity)
    version = chunk.version
    if version == 2:
        frame0_nano = chunk.frame0_nano
        nrfifreq = chunk.nrfifreq
        rfi_mask = chunk.rfi_mask
    return (
        intensity,
        weights,
        chunk.fpga0,
        chunk.fpgaN,
        chunk.binning,
        frame0_nano,
        nrfifreq,
        rfi_mask,
    )


def unpack_datafiles(fns, downsample=True):
    """
    Unpacks a list of functions from a beam and appends to the
    list of intensities and weights. If mixed binning chunks are provided,
    downsampled chunks are upsampled to the finest time resolution
    (lowest binning) available.
    Parameters
    ----------
    fns : list
        A list of function names from a beam corresponsing
        to different time chunks.
    Return
    ------
    intensities : list
        A list of 2D intensity arrays.
    weights : list
        A list of 2D weight arrays.
    fpga0s : int
        A list start fpga count of those chunks.
    fpgaNs : int
        A list of number of fpga counts in those chunks.
    binning : int
        The downsampling used for the chunks.
        If a mixture of binnings is used, the intensity data is duplicated
        to the finest time resolution.
    """
    intensities = []
    weights = []
    fpga0s = []
    fpgaNs = []
    rfi_masks = []
    bin_list = []
    frame0_nanos = []
    for fn in fns:
        print(fn)
        (
            intensity,
            weight,
            fpga0,
            fpgaN,
            binning,
            frame0_nano,
            nrfifreq,
            rfi_mask,
        ) = unpack_data(fn)
        intensities.append(intensity)
        weights.append(weight)
        fpga0s.append(fpga0)
        fpgaNs.append(fpgaN)
        bin_list.append(binning)
        frame0_nanos.append(frame0_nano)
        rfi_masks.append(rfi_mask)
    print("files read...")
    output_bin = 1

    if (
        len(set(bin_list)) == 1 and bin_list[0] == 1
    ):  # if bin_list has only one unique item and it is 1
        return (
            np.hstack(intensities)[::-1],
            np.hstack(weights)[::-1],
            fpga0s,
            fpgaNs,
            output_bin,
            np.hstack(rfi_masks)[::-1],
            frame0_nanos,
        )
    else:
        print("else condition triggered")
        # get all of the intensities to the same
        # get the output shape:

        # Downsample
        if downsample:
            raise NotImplementedError("data downsampling is not supported.")

        # Upsample
        else:
            total_samples = np.sum(
                [
                    (binning / output_bin) * intensity_chunk.shape[1]
                    for binning, intensity_chunk in zip(bin_list, intensities)
                ]
            )

            output_intensities = np.empty([intensities[0].shape[0], total_samples])
            output_weights = np.empty_like(output_intensities)
            output_rfi_masks = np.empty_like(output_intensities)
            current_idx = 0

            for i in range(len(bin_list)):
                binning = bin_list[i]
                intensity = intensities[i].repeat(binning / output_bin, axis=1)
                chunk_samples = intensity.shape[1]
                output_intensities[
                    :, current_idx : current_idx + chunk_samples
                ] = intensity
                weight = weights[i].repeat(binning / output_bin, axis=1)
                output_weights[:, current_idx : current_idx + chunk_samples] = weight
                current_idx += chunk_samples
                rfi_mask = rfi_masks[i].repeat(binning / output_bin, axis=1)
                output_rfi_masks[
                    :, current_idx : current_idx + chunk_samples
                ] = rfi_mask
                current_idx += chunk_samples
        print("all is well")
        return (
            output_intensities,
            output_weights,
            fpga0s,
            fpgaNs,
            output_bin,
            output_rfi_masks,
            frame0_nanos,
        )


# sort files in natural order
def atoi(text: str):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    import re

    """alist.sort(key=natural_keys) sorts in human order"""
    return [atoi(c) for c in re.split(r"(\d+)", text)]
