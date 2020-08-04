class CSVReader:
    def __init__(self, path):
        self.path = path

    def to_pandas(self, **kwargs):
        import pandas

        return pandas.read_csv(self.path, **kwargs)
