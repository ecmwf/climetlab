from matplotlib.pyplot import figure


class Driver:
    def __init__(self, options):

        self._options = options
        self.figure = figure()
        self.ax = self.figure.add_subplot(1, 1, 1)

    def plot_graph_pandas(self, frame, time: str, variable: str):
        frame.plot(ax=self.ax)
        return self.figure

    def option(self, name, default=None):
        return self._options(name, default)

    def apply_options(self, options):
        pass

    def show(self, display):
        self.figure.show()
        display(self.figure)
        return self.figure

    def save(self, path):
        self.figure.savefig(path)
