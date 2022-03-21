# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import copy
import json
import logging
import math
import warnings

from climetlab.core.caching import auxiliary_cache_file
from climetlab.profiling import call_counter
from climetlab.sources import Source
from climetlab.utils.bbox import BoundingBox

from .codes import CodesReader, GribField, GribIndex

LOG = logging.getLogger(__name__)


def missing_is_none(x):
    return None if x == 2147483647 else x


def mix_kwargs(
    user,
    default,
    forced={},
    logging_owner="",
    logging_main_key="",
):
    kwargs = copy.deepcopy(default)

    for k, v in user.items():
        if k in forced and v != forced[k]:
            LOG.warning(
                (
                    f"In {logging_owner} {logging_main_key},"
                    f"ignoring attempt to override {k}={forced[k]} with {k}={v}."
                )
            )
            continue

        if k in default and v != default[k]:
            LOG.warning(
                (
                    f"In {logging_owner} {logging_main_key}, overriding the default value "
                    f"({k}={default[k]}) with {k}={v} is not recommended."
                )
            )

        kwargs[k] = v

    kwargs.update(forced)

    return kwargs


class FieldAdapter:
    def __init__(self, field, ignore_keys):
        self.field = field
        self.ignore_keys = ignore_keys

    def __getitem__(self, name):
        if name in self.ignore_keys:
            return None
        return self.field[name]


class FieldsetAdapter:
    def __init__(self, fieldset, ignore_keys):
        self.fieldset = fieldset
        self.ignore_keys = ignore_keys

    def __getitem__(self, n):
        return FieldAdapter(self.fieldset[n], self.ignore_keys)

    def __len__(self):
        return len(self.fieldset)


class FieldSet(Source):
    def __init__(self, *, paths=None):
        self._statistics = None
        self.readers = {}
        self.fields = []
        if paths is not None:
            if not isinstance(paths, (list, tuple)):
                paths = [paths]
            for path in paths:
                index = GribIndex(path)
                for offset, length in zip(index.offsets, index.lengths):
                    self.fields.append((path, offset, length))

    def reader(self, path):
        if path not in self.readers:
            self.readers[path] = CodesReader(path)
        return self.readers[path]

    def __getitem__(self, n):
        path, offset, length = self.fields[n]
        return GribField(self.reader(path), offset, length)

    def __len__(self):
        return len(self.fields)

    @property
    def first(self):
        return self[0]

    def to_tfdataset(
        self, split=None, shuffle=None, normalize=None, batch_size=0, **kwargs
    ):
        # assert "label" in kwargs
        if "offset" in kwargs:
            return self._to_tfdataset_offset(**kwargs)
        if "label" in kwargs:
            return self._to_tfdataset_supervised(**kwargs)
        else:
            return self._to_tfdataset_unsupervised(**kwargs)

    def _to_tfdataset_offset(self, offset, **kwargs):

        # μ = self.statistics()["average"]
        # σ = self.statistics()["stdev"]

        def normalise(a):
            return a
            # return (a - μ) / σ

        def generate():
            fields = []
            for s in self:
                fields.append(normalise(s.to_numpy()))
                if len(fields) >= offset:
                    yield fields[0], fields[-1]
                    fields.pop(0)

        import tensorflow as tf

        shape = self.first.shape

        dtype = kwargs.get("dtype", tf.float32)
        return tf.data.Dataset.from_generator(
            generate,
            output_signature=(
                tf.TensorSpec(shape, dtype=dtype, name="input"),
                tf.TensorSpec(shape, dtype=dtype, name="output"),
            ),
        )

    def _to_tfdataset_unsupervised(self, **kwargs):
        def generate():
            for s in self:
                yield s.to_numpy()

        import tensorflow as tf

        # TODO check the cost of the conversion
        # maybe default to float64
        dtype = kwargs.get("dtype", tf.float32)
        return tf.data.Dataset.from_generator(generate, dtype)

    def _to_tfdataset_supervised(self, label, **kwargs):
        @call_counter
        def generate():
            for s in self:
                yield s.to_numpy(), s.handle.get(label)

        import tensorflow as tf

        # with timer("_to_tfdataset_supervised shape"):
        shape = self.first.shape

        # TODO check the cost of the conversion
        # maybe default to float64
        dtype = kwargs.get("dtype", tf.float32)
        # with timer("tf.data.Dataset.from_generator"):
        return tf.data.Dataset.from_generator(
            generate,
            output_signature=(
                tf.TensorSpec(shape, dtype=dtype, name="data"),
                tf.TensorSpec(tuple(), dtype=tf.int64, name=label),
            ),
        )

    def to_xarray(self, **kwargs):

        import xarray as xr

        xarray_open_dataset_kwargs = {}

        if "xarray_open_mfdataset_kwargs" in kwargs:
            warnings.warn(
                "xarray_open_mfdataset_kwargs is deprecated, please use xarray_open_dataset_kwargs instead."
            )
            kwargs["xarray_open_dataset_kwargs"] = kwargs.pop(
                "xarray_open_mfdataset_kwargs"
            )

        user_xarray_open_dataset_kwargs = kwargs.get("xarray_open_dataset_kwargs", {})

        # until ignore_keys is included into cfgrib,
        # it is implemented here directly
        ignore_keys = user_xarray_open_dataset_kwargs.get("backend_kwargs", {}).pop(
            "ignore_keys", []
        )

        for key in ["backend_kwargs"]:
            xarray_open_dataset_kwargs[key] = mix_kwargs(
                user=user_xarray_open_dataset_kwargs.pop(key, {}),
                default={"errors": "raise"},
                forced={},
                logging_owner="xarray_open_dataset_kwargs",
                logging_main_key=key,
            )
        xarray_open_dataset_kwargs.update(
            mix_kwargs(
                user=user_xarray_open_dataset_kwargs,
                default={"squeeze": False},
                forced={
                    "errors": "raise",
                    "engine": "cfgrib",
                },
            )
        )

        result = xr.open_dataset(
            FieldsetAdapter(self, ignore_keys=ignore_keys),
            **xarray_open_dataset_kwargs,
        )

        def math_prod(lst):
            if not hasattr(math, "prod"):
                # python 3.7 does not have math.prod
                n = 1
                for x in lst:
                    n = n * x
                return n
            return math.prod(lst)

        def number_of_gribs(da):
            # Assumes last two dimensions are lat/lon coordinates
            skip = 2
            if da.dims[-1] == "values":
                # Assumes last dimension is the one-dimensional
                # lat/lon coordinate (non-regular grid)
                skip = 1
            return math_prod(list(da.shape)[:-skip])

        two_d_fields = sum(number_of_gribs(result[v]) for v in result.data_vars)

        # Make sure all the fields are converted
        # There may be more 2D xarray fields than GRB fields
        # if some missing dimension are filled with NaN values

        assert two_d_fields >= len(self), (
            "Not all GRIB fields were converted to xarray"
            f" ({len(self)} GRIBs > {two_d_fields} 2D-field(s) in xarray)"
        )

        return result

    def to_metview(self):
        from climetlab.metview import mv_read

        return mv_read(self.path)

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

    # def graph(self):
    #     # Compatibility with multi
    #     print("FieldSet.graph() not yet implemented")

    def save(self, filename):
        with open(filename, "wb") as f:
            self.write(f)

    def write(self, f):
        for s in self:
            s.write(f)
