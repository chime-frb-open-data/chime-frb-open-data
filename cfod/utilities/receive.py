"""Receive VOEvents and perform actions."""

from cfod.routines.receiver import Receiver

if __name__ == "__main__":
    r = Receiver()
    r.start()
    r.stop()
