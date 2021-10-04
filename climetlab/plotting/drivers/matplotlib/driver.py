
class Driver:
    def __init__(self, options):

        self._options = options

    def plot_graph_pandas(self, frame, time: str, variable: str):
        frame.plot()

    def option(self, name, default=None):
        return self._options(name, default)

    def apply_options(self, options):
        pass

    def show(self):
        pass