# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import json
import logging
from collections import defaultdict

from climetlab.core.caching import auxiliary_cache_file
from climetlab.core.index import ScaledIndex
from climetlab.utils.bbox import BoundingBox

from .pandas import PandasMixIn
from .pytorch import PytorchMixIn
from .tensorflow import TensorflowMixIn
from .xarray import XarrayMixIn

LOG = logging.getLogger(__name__)


class FieldSetMixin(PandasMixIn, XarrayMixIn, PytorchMixIn, TensorflowMixIn):
    _statistics = None

    def _find_all_coords_dict(self):
        from climetlab.indexing.database.sql import GRIB_INDEX_KEYS

        coords = defaultdict(set)
        for f in self:
            for k in GRIB_INDEX_KEYS:
                v = f.metadata(k)
                if v is None:
                    continue
                coords[k].add(v)

        return {k: list(v) for k, v in coords.items()}

    @property
    def all_coords(self):
        if not self._coords:
            self._coords = self._find_all_coords_dict()
        return self._coords

    @property
    def coords(self):
        # squeeze coords with only 1 value.
        return {k: v for k, v in self.all_coords.items() if len(v) > 1}

    @property
    def first(self):
        return self[0]

    def to_metview(self):
        from climetlab.metview import mv_read

        return mv_read(self.path)

    def to_numpy(self):
        import numpy as np

        return np.array([f.to_numpy() for f in self])

    def plot_map(self, backend):
        return self.first.plot_map(backend)

    def plot_graph(self, backend):
        import numpy as np

        what = backend._options("what", "global_average")
        what = dict(
            global_average=np.mean,
        )[what]

        # initialize list of lists
        data = [[s.valid_datetime(), what(s.to_numpy())] for s in self]
        import pandas as pd

        df = pd.DataFrame(data, columns=["date", "param"])

        backend.plot_graph_add_timeserie(df)

    # Used by normalisers
    def to_datetime(self):
        times = self.to_datetime_list()
        assert len(times) == 1
        return times[0]

    def to_datetime_list(self):
        # TODO: check if that can be done faster
        result = set()
        for s in self:
            result.add(s.valid_datetime())
        return sorted(result)

    def to_bounding_box(self):
        return BoundingBox.multi_merge([s.to_bounding_box() for s in self])

    def statistics(self):
        import numpy as np

        if self._statistics is not None:
            return self._statistics

        if False:
            cache = auxiliary_cache_file(
                "grib-statistics--",
                self.path,
                content="null",
                extension=".json",
            )

            with open(cache) as f:
                self._statistics = json.load(f)

            if self._statistics is not None:
                return self._statistics

        stdev = None
        average = None
        maximum = None
        minimum = None
        count = 0

        for s in self:
            v = s.values
            if count:
                stdev = np.add(stdev, np.multiply(v, v))
                average = np.add(average, v)
                maximum = np.maximum(maximum, v)
                minimum = np.minimum(minimum, v)
            else:
                stdev = np.multiply(v, v)
                average = v
                maximum = v
                minimum = v

            count += 1

        nans = np.count_nonzero(np.isnan(average))
        assert nans == 0, "Statistics with missing values not yet implemented"

        maximum = np.amax(maximum)
        minimum = np.amin(minimum)
        average = np.mean(average) / count
        stdev = np.sqrt(np.mean(stdev) / count - average * average)

        self._statistics = dict(
            minimum=minimum,
            maximum=maximum,
            average=average,
            stdev=stdev,
            count=count,
        )

        if False:
            with open(cache, "w") as f:
                json.dump(self._statistics, f)

        return self._statistics

    def save(self, filename):
        with open(filename, "wb") as f:
            self.write(f)

    def write(self, f):
        for s in self:
            s.write(f)

    def scaled(self, method=None, offset=None, scaling=None):
        if method == "minmax":
            assert offset is None and scaling is None
            stats = self.statistics()
            offset = stats["minimum"]
            scaling = 1.0 / (stats["maximum"] - stats["minimum"])

        return ScaledIndex(self, offset, scaling)
