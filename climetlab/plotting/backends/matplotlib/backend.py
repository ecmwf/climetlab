# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


class Backend:
    def __init__(self, options):

        self._options = options

        from matplotlib.pyplot import figure

        self.figure = figure()
        self.ax = self.figure.add_subplot(1, 1, 1)

    # def finalize2(self):

    #     state = State(self)
    #     for a in self._actions:
    #         state = a.tranform(state)
    def plot_graph_add_timeserie(self, frame):
        frame.plot(x="date", ax=self.ax)

    def plot_graph_pandas(self, frame, time: str, variable: str):
        k = self._options("k", "pandas")

        import pandas

        frame.date = pandas.to_datetime(frame.date)

        # TODO: need to set variable ?
        # print(time, variable)

        if k == "seaborn":
            import seaborn as sns

            sns.lineplot(data=frame, x="date", y="value")

            return

        if k == "pandas":
            kwargs = self._options("pandas_dataframe_plot_kwargs", {})

            frame.plot(x="date", ax=self.ax, **kwargs)
            return

    def option(self, name, default=None):
        return self._options(name, default)

    def apply_options(self, options):
        pass

    def show(self, display):
        self.figure.show()  # not usefull in jupyter lab
        # display(self.figure)

    def save(self, path):
        self.figure.savefig(path)
