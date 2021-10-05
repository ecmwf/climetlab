class Backend:
    def __init__(self, options):

        self._options = options

    def plot_graph_pandas(self, frame, time: str, variable: str):
        from bokeh.plotting import figure, show

        p = figure(title="Simple line example", x_axis_label="x", y_axis_label="y")
        p.line(frame[time], frame["value"])
        show(p)

    def option(self, name, default=None):
        return self._options(name, default)

    def apply_options(self, options):
        pass

    def show(self):
        pass
