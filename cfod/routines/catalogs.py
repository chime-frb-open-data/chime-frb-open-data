from typing import Optional


class Catalogs:
    def __init__(self, filename: str):
        self.filename: str = filename
        self.format: Optional[str] = None

    def _check_filename():
        pass

    def as_dict(self):
        pass

    def as_json(self):
        pass

    def as_list(self):
        pass

    def as_dataframe(self):
        pass

    def as_fits(self):
        pass

    def as_ndarray(self):
        raise NotImplementedError("Currently not implemented.")
