"""Base Actor Class."""

import comet
from comet.icomet import IHandler
from comet.utility.xml import xml_document
from twisted.plugin import IPlugin
from zope.interface import implementer


@implementer(IPlugin, IHandler)
class Actor:
    """Base Actor."""

    def __init__(self, **kwargs) -> None:
        """Actor Initialization."""
        self.args = kwargs

    def action(
        self,
        event: xml_document,
    ) -> None:
        """Work to be performed.

        Parameters
        ----------
        event : xml_document
            CHIME/FRB VOEvent XML document.

        Returns
        -------
        NoReturn

        Raises
        ------
        NotImplementedError
        """
        # TODO: print event
        raise NotImplementedError("No action implemented.")

    def __call__(self, event) -> None:
        """
        Call this event handler when a VOEvent is received by the Comet broker.

        Parameters
        ----------
        event : comet.utility.xml.xml_document
            CHIME/FRB VOEvent XML document.

        Returns
        -------
        None

        Notes
        -----
        This script must be installed in comet/plugins.
        Use `--actor` as a command line option when running
        the comet via
        $ twistd -n comet --actor
        """
        self.action(event)
