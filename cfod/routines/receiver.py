"""VOEvent Receiver."""

import logging
import os

from cfod.routines.actor import Actor

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)


class Receiver:
    """
    VOEvent Receiver Class.

    Parameters
    ----------
    test : bool, default=False
        Whether to configure the receiver in testing mode.

    Attributes
    ----------
    start_cmd : str
        Command to launch the Comet VOEvent broker.

    stop_cmd : str
        Command to stop the Comet VOEvent broker.
    """

    def __init__(
        self,
        test: bool = False,
        debug: bool = False,
        actor: Actor = Actor(),
    ) -> None:
        """
        VOEvent Receiver initialization.

        Parameters
        ----------
        test : bool, default = False
            Testing mode publishes a test version of
            each CHIME/FRB VOEvent from the localhost
            to the background Comet broker.

        debug : bool, default = False
            Toggle logging level.

        actor : cfod.routines.actor.Actor
            Actor or its subclasses, to instruct this
            class on what to do with received VOEvents.

        Returns
        -------
        None
        """
        self.test = test
        self.debug = debug
        self.actor = actor
        self.module = actor.__module__.split(".")[-1]
        self.script = self.module + ".py"
        self.start_cmd = f"twistd -n comet --receive --author-whitelist 127.0.0.1 --local-ivo=ivo://cfod_receiver --print-event --{self.module}"
        self.stop_cmd = "kill -9 $(pgrep -f 'twistd')"
        self._introspect()

    def _introspect(self) -> None:
        if self.debug:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.ERROR)

    def start(self):
        """
        Start the Comet broker as a background daemon.

        Launches the Comet VOEvent broker in daemonized
        mode using ``os.system(cmd)`` where the `cmd` is
        the usual one to launch comet with twistd.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        None
        """
        log.info(f"Starting Comet broker with {self.start_cmd}")
        os.system(self.start_cmd)

    def stop(self):
        """
        Stop the Comet broker by killing its twistd process.

        Use pgrep to search for the twistd process ID of the
        daemonized Comet broker on the local machine and kill it.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        None
        """
        log.info(f"Stopping Comet broker with {self.stop_cmd}")
        os.system(self.stop_cmd)
