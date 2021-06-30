"""CSVWriter Actor Class."""

import comet
import xmltodict

from cfod.routines.actor import Actor


class CSVWriter(Actor):
    """
    CSVWriter extends base Actor class.

    Write the received VOEvent to CSV.

    Attributes
    ----------
    fname : str
        File name for CSV.
    header : str
        Column headers to print to CSV.
    data : str
        Row data to print to CSV.
    """

    def __init__(self, **kwargs) -> None:
        """Actor initialization from super class."""
        super(Actor, self).__init__()
        self.fname = ""
        self.header = "\n"
        self.data = "\n"

    def add(
        self,
        name: str,
        value: str,
    ) -> None:
        """
        Add a new column and its value to the `data` possessed by the instance.

        Parameters
        ----------
        name : str
            New column name.
        value : str
            Row value of the corresponding column.

        Returns
        -------
        None
        """
        # Update header with new named column
        self.header.replace("\n", "")
        self.header += f"{name},\n"

        # Update line with value at corresponding column
        self.data.replace("\n", "")
        self.data += f"{value},\n"

    def xml_to_csv(
        self,
        event: str,
    ) -> None:
        """
        Write string format of VOEvent XML to CSV.

        Parameters
        ----------
        event : str
            String format of the VOEvent XML document.

        Returns
        -------
        None
        """
        event = event.replace(
            "b'<?xml version=\\'1.0\\' encoding=\\'UTF-8\\'?>\\n", ""
        ).replace("'", "")
        xml_dict = xmltodict(event)["voe:VOEvent"]
        self.dict_to_csv(xml_dict)

    def dict_to_csv(
        self,
        xml_dict,
    ) -> None:
        """
        Write dict format of VOEvent XML to CSV.

        Parameters
        ----------
        xml_dict : dict
            Dictionary format of the VOEvent XML document.

        Returns
        -------
        None
        """
        self.fname = str(xml_dict["@ivorn"].split(".frb/")[1])
        # VOEvent properties
        self.add("IVORN", xml_dict["@ivorn"])
        self.add("Role", xml_dict["@role"])
        self.add("Origin", xml_dict["Who"]["Description"])
        # TODO: Who, What, WhereWhen, Why, How, Citations
        with open(self.fname, "w") as f:
            f.write(self.header)
            f.write(self.data)

    def action(
        self,
        event: comet.utility.xml.xml_document,
    ) -> None:
        """
        Write received VOEvent to CSV file.

        Parameters
        ----------
        event : comet.utility.xml.xml_document
            CHIME/FRB VOEvent XML document.

        Returns
        -------
        None
        """
        self.xml_to_csv(str(event))

    def __call__(
        self,
        event: comet.utility.xml.xml_document,
    ) -> None:
        """
        Call this event handler when a VOEvent is received by the Comet broker.

        Parameters
        ----------
        event : comet.utility.xml.xml_document
            CHIME/FRB VOEvent XML document.

        Returns
        -------
        None
        """
        self.action(event)
