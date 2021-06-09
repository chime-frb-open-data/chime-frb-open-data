from cfod.analysis import waterfall


class Waterfaller:
    def __init__(self, filename: str, save: bool = False) -> None:
        self.filename = filename
        self.data = waterfall.data(filename=self.filename)
