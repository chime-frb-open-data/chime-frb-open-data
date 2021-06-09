"""
Python code for reading CHIME/FRB msgpack data.
"""

import msgpack
import numpy as np


class AssembledChunk:
    def __init__(self, msgpacked_chunk, debug=False):
        c = msgpacked_chunk
        # print('header', c[0])
        version = c[1]
        assert version in [1, 2]
        if version == 1:
            assert len(c) == 17
        if version == 2:
            assert len(c) == 21
        self.version = version
        compressed = c[2]
        compressed_size = c[3]

        if debug:
            print("data version", version)
            print("compressed? ", compressed)
            print("compressed size", compressed_size)

        self.beam = c[4]
        self.nupfreq = c[5]
        self.nt_per_packet = c[6]
        self.fpga_counts_per_sample = c[7]
        self.nt_coarse = c[8]
        self.nscales = c[9]
        self.ndata = c[10]
        self.fpga0 = c[11]
        self.fpgaN = c[12]
        self.binning = c[13]
        self.nt = self.nt_coarse * self.nt_per_packet

        scales = c[14]
        offsets = c[15]
        data = c[16]

        # version 2: extra arguments
        self.frame0_nano = 0
        self.nrfifreq = 0
        self.has_rfi_mask = False
        self.rfi_mask = None
        if self.version == 2:
            self.frame0_nano = c[17]
            self.nrfifreq = c[18]
            self.has_rfi_mask = c[19]
            mask = c[20]
            # to numpy
            mask = np.fromstring(mask, dtype=np.uint8)
            mask = mask.reshape((self.nrfifreq, self.nt // 8))
            # Expand mask!
            self.rfi_mask = np.zeros((self.nrfifreq, self.nt), bool)
            for i in range(8):
                self.rfi_mask[:, i::8] = (mask & (1 << i)) > 0

        # Convert to numpy arrays
        self.scales = np.fromstring(scales, dtype="<f4")
        self.offsets = np.fromstring(offsets, dtype="<f4")
        self.scales = self.scales.reshape((-1, self.nt_coarse))
        self.offsets = self.offsets.reshape((-1, self.nt_coarse))
        self.data = np.frombuffer(data, dtype=np.uint8)
        self.data = self.data.reshape((-1, self.nt))

    def __str__(self):
        if self.has_rfi_mask:
            h, w = self.rfi_mask.shape
            masked = np.sum(self.rfi_mask == 0)
            rfistr = "yes, %i freqs, %i%% masked" % (
                self.nrfifreq,
                int(100.0 * masked / (h * w)),
            )
        else:
            rfistr = "no"
        return "AssembledChunk: beam %i, nt %i, fpga0 %i, rfi %s" % (
            self.beam,
            self.nt,
            self.fpga0,
            rfistr,
        )

    def decode(self, debug=False):
        # Returns (intensities,weights) as floating-point
        nf = self.data.shape[1]

        if debug:
            print("Data shape:", self.data.shape)
            print("Scales shape:", self.scales.shape)
            print("nupfreq:", self.nupfreq)
            print("nt_per_packet:", self.nt_per_packet)
            print("nf: ", nf)

        intensities = (
            self.offsets.repeat(self.nupfreq, axis=0).repeat(self.nt_per_packet, axis=1)
            + self.data
            * self.scales.repeat(self.nupfreq, axis=0).repeat(
                self.nt_per_packet, axis=1
            )
        ).astype(np.float32)

        weights = ((self.data > 0) * (self.data < 255)) * np.float32(1.0)

        return intensities, weights

    def time_start(self):
        # Nanoseconds per FPGA count
        fpga_nano = 2560
        return 1e-9 * (
            self.frame0_nano + self.fpga_counts_per_sample * fpga_nano * self.fpga0
        )

    def time_end(self):
        # Nanoseconds per FPGA count
        fpga_nano = 2560
        return 1e-9 * (
            self.frame0_nano
            + self.fpga_counts_per_sample * fpga_nano * (self.fpga0 + self.fpgaN)
        )


def read_msgpack_file(fn):
    f = open(fn, "rb")
    m = msgpack.unpackb(f.read())
    return AssembledChunk(m)
