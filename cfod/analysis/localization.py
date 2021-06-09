import h5py as h5
import matplotlib.pyplot as plt
import numpy as np


def describe(group, recurse=False):
    """
    Describes a HDF5 group object

    Parameters
    ----------
    group : [type]
        [description]
    recurse : bool, optional
        [description], by default False
    """

    print(group.name)

    # First print header-like attributes (if exist)
    if group.attrs:
        print("\n  attrs: {")
    for key, value in group.attrs.items():
        if key in ["comments", "history"]:
            print("    %s:" % key)
            for line in value:
                print("      " + str(line))
        else:
            print("    %s:" % key, value)
    if group.attrs:
        print("  }")

    # Then print constituent groups & datasets
    print()
    for key, value in group.items():
        if isinstance(value, h5.Group):
            if recurse:
                print("-" * 60)
                describe(value, True)
            else:
                print("  " + key + "/")
        else:
            print("  " + key + ":", value.shape, value.dtype)
    print()


def plot(data):
    hdr = data["projection"].attrs
    CL = data["projection/data"][:]
    extent = (
        np.array(
            [-hdr["xsize"] / 2, hdr["xsize"] / 2, -hdr["ysize"] / 2, hdr["ysize"] / 2]
        )
        * hdr["reso"]
        / 60
    )

    plt.rc("font", family="serif", size=14)
    plt.figure(figsize=(10, 4))

    # Note: RA increases to the left!
    im = plt.imshow(CL, vmin=0, origin="lower", extent=extent, cmap="magma")
    plt.contour(
        CL,
        levels=[0.68, 0.95],
        linestyles=["-", "--"],
        colors="k",
        linewidths=2,
        extent=extent,
    )

    plt.colorbar(
        im, pad=0.25, shrink=0.4, orientation="horizontal", label="Confidence Level"
    )
    plt.arrow(2.4, -0.4, 0, 0.2, head_width=0.04, color="k")
    plt.text(2.39, -0.1, "N", ha="center", size=10)
    plt.arrow(2.4, -0.4, -0.2, 0.0, head_width=0.04, color="k")
    plt.text(2.1, -0.4, "E", va="center", ha="right", size=10)
    plt.title("Centered @ {:.3f}, {:.2f}".format(hdr["clon"], hdr["clat"]))
    plt.xlabel("dx (deg)")
    plt.ylabel("dy (deg)")


def countours(data):
    # example 0: getting points
    ra, dec = data["contours/68/A"]

    # example 2: plotting contours
    plt.figure(figsize=(10, 2))

    for name, contour in data["contours/68"].items():
        contour = contour[:]
        plt.plot(*contour)
        plt.plot(*contour.mean(1), "wo", mec="k", ms=20, alpha=0.5)
        plt.text(*contour.mean(1), s=name, ha="center", va="center")
    for contour in data["contours/95"].values():
        plt.plot(*contour[:], "--")

    plt.xlim(*plt.xlim()[::-1])
    plt.xlabel("R.A. (deg)")
    plt.ylabel("Dec. (deg)")
