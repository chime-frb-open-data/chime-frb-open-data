"""CHIME/FRB Virtual Observatory Event."""
import logging
from typing import Union

from cfod.routines.actor import Actor

logging.basicConfig(format="%(levelname)s:%(message)s")
log = logging.getLogger(__name__)


class VOE:
    """CHIME/FRB Virtual Observatory Event Handler."""

    def __init__(
        self,
        email: str,
        action: Actor,
        format: str = "dict",
        testing: bool = False,
        debug: bool = False,
        **kwargs
    ) -> None:
        """
        CHIME/FRB Virtual Observatory Event Handler.

        Parameters
        ----------
        email : str
            Registered email with CHIME/FRB VOEvent Service.
        actor : Actor
            Action to take, upon recieveing an event.
        format : str, optional
            Format of the VOEvent, by default "dict".
            Valid Options:
        testing : bool, optional
            Enable test mode, by default False.
        debug : bool, optional
            Enable deeper logging, by default False.
        """
        self.email = email
        self.actor = Actor(**kwargs)
        self.format = format
        self.testing = testing
        self.debug = debug
        self._introspect()

    def _introspect(self):
        if self.debug:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.ERROR)

    def perform_action(self, event: Union[str, dict]):
        """
        Perform action.

        Parameters
        ----------
        event : [type]
            [description]
        """
        self.actor.action(event)
