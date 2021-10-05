from matplotlib.pyplot import figure


class Backend:
    def __init__(self, options):

        self._options = options
        # self._actions = []

        # def finalize(self):
        #    fig = figure()
        #    for a in self._actions:
        #        a.execute(fig)

        self.figure = figure()
        self.ax = self.figure.add_subplot(1, 1, 1)

    # def finalize2(self):

    #     state = State(self)
    #     for a in self._actions:
    #         state = a.tranform(state)

    def plot_graph_pandas(self, frame, time: str, variable: str):
        print(time, variable)
        frame.plot(ax=self.ax)

    def option(self, name, default=None):
        return self._options(name, default)

    def apply_options(self, options):
        pass

    def show(self, display):
        self.figure.show()  # not usefull in jupyter lab
        # display(self.figure)

    def save(self, path):
        self.figure.savefig(path)
