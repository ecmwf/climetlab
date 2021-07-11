# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.wrappers import get_wrapper

from . import Reader

LOG = logging.getLogger(__name__)


class CSVReader(Reader):
    def __init__(self, source, path, compression=None):
        super().__init__(source, path)
        self.compression = compression

    def to_pandas(self, **kwargs):
        import pandas

        pandas_read_csv_kwargs = kwargs.get("pandas_read_csv_kwargs", {})
        if self.compression is not None:
            pandas_read_csv_kwargs = dict(**pandas_read_csv_kwargs)
            pandas_read_csv_kwargs["compression"] = self.compression

        LOG.debug("pandas.read_csv(%s,%s)", self.path, pandas_read_csv_kwargs)
        return pandas.read_csv(self.path, **pandas_read_csv_kwargs)

    def to_tfdataset(self, batch_size=1000, **kwargs):
        # See https://www.tensorflow.org/api_docs/python/tf/data/experimental/make_csv_dataset
        import tensorflow as tf

        return tf.data.experimental.make_csv_dataset(
            self.path,
            batch_size,
        )

    def plot_map(self, driver):
        get_wrapper(self.to_pandas()).plot_map(driver)


def reader(source, path, magic, deeper_check):
    if path.endswith(".csv"):
        return CSVReader(source, path)
