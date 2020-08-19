class ZIPReader:
    def __init__(self, source, path):
        self.source = source
        self.path = path

    def to_pandas(self, **kwargs):
        import pandas

        options = dict()
        options.update(self.source.read_csv_options)
        options.update(kwargs)

        return pandas.read_csv(self.path, **options)
