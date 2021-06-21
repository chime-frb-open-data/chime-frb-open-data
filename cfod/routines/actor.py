"""Base Actor Class."""
from typing import NoReturn, Union


class Actor:
    """Base Actor."""

    def __init__(self, **kwargs) -> None:
        """Actor Initialization."""
        self.args = kwargs

    def action(self, event: Union[str, dict]) -> NoReturn:
        """Work to be performed.

        Parameters
        ----------
        event : Union[str, dict]
            CHIME/FRB VOE Event.

        Returns
        -------
        NoReturn

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("No action Implemented.")
