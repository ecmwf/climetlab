class CSVReader:
    def __init__(self, source, path):
        self.path = path

    def to_pandas(self, **kwargs):
        import pandas

        return pandas.read_csv(self.path, **kwargs)
