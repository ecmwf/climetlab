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
import os

import numpy as np
from tqdm import tqdm

from climetlab.core.settings import SETTINGS
from climetlab.decorators import alias_argument
from climetlab.readers.grib.fieldset import FieldSet
from climetlab.scripts.grib import _index_grib_file

LOG = logging.getLogger(__name__)


# TODO: rename 'local' to a more meaningful name
class IndexedSource(FieldSet):

    _reader_ = None

    @alias_argument("levelist", ["level"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", "klass")
    def __init__(self, path=None, dic=None, filter=None, merger=None, **kwargs):
        self.path = path
        self.abspath = os.path.abspath(path)
        self._climetlab_index_file = os.path.join(self.abspath, "climetlab.index")
        self._index = None
        self.filter = filter
        self.merger = merger

        if dic:
            assert isinstance(
                dic, dict
            ), f"Expected a dict, but argument was dic={dic}."
            for k, v in dic.items():
                assert k not in kwargs, f"Duplicated key {k}={v} and {k}={kwargs[k]}"
                kwargs[k] = v

        self.kwargs_selection = kwargs

        fields = self.kwargs_to_fields(kwargs)
        LOG.debug("Got iterator")
        fields = list(fields)
        LOG.debug("Transformed into list")
        super().__init__(fields=fields)

    def kwargs_to_fields(self, kwargs):
        for path, parts in tqdm(self.index.lookup_request(kwargs)):
            assert path[:5] == "file:", path
            path = path[5:]  # hack to remove 'file:'
            for offset, length in parts:
                yield (path, offset, length)

    def sel(self, **kwargs):
        new_kwargs = {k: v for k, v in self.kwargs_selection.items()}
        new_kwargs.update(kwargs)
        return IndexedSource(
            self.path, filter=self.filter, merger=self.merger, **new_kwargs
        )

    def __repr__(self):
        cache_dir = SETTINGS.get("cache-directory")
        if hasattr(self, "path"):
            path = self.path
        else:
            path = "..."
        if hasattr(self, "abspath"):
            abspath = self.abspath
        else:
            abspath = "..."

        if isinstance(path, str):
            path = path.replace(cache_dir, "CACHE:")
        return f"{self.__class__.__name__}({path}, {abspath})"

    def _create_index(self):
        assert os.path.isdir(self.path)
        for root, _, files in os.walk(self.path):
            for name in files:
                if name == "climetlab.index":
                    continue
                p = os.path.abspath(os.path.join(root, name))
                yield from _index_grib_file(p, path_name=name)

    @property
    def index(self):
        if self._index is not None:
            return self._index

        from climetlab.indexing import DirectoryGlobalIndex

        if os.path.exists(self._climetlab_index_file):
            self._index = DirectoryGlobalIndex(
                self._climetlab_index_file, path="file://" + self.abspath
            )
            return self._index

        print("Creating index for", self.path, " into ", self._climetlab_index_file)
        entries = self._create_index()
        # TODO: create .tmp file and move it (use cache_file)
        with open(self._climetlab_index_file, "w") as f:
            for e in entries:
                json.dump(e, f)
                print("", file=f)

        print("Created index file", self._climetlab_index_file)
        return self.index

    def to_pytorch(self, offset, data_loader_kwargs=None):
        import torch

        # Settings num_workers > 1 sometimes lead to GRIB read error
        #   line 382, in raise_grib_error raise ERROR_MAP[errid](errid) gribapi.errors.UnsupportedEditionError: Edition not supported.
        # Will work on it if speed is needed.
        num_workers = 10

        out = get_wrapper_class()(self, offset)

        DATA_LOADER_KWARGS_DEFAULT = dict(
            batch_size=128,
            # multi-process data loading
            # use as many workers as you have cores on your machine
            num_workers=num_workers,
            # default: no shuffle, so need to explicitly set it here
            shuffle=True,
            # uses pinned memory to speed up CPU-to-GPU data transfers
            # see https://pytorch.org/docs/stable/notes/cuda.html#cuda-memory-pinning
            pin_memory=True,
            # function used to collate samples into batches
            # if None then Pytorch uses the default collate_fn (see below)
            collate_fn=None,
        )
        data_loader_kwargs_ = {k: v for k, v in DATA_LOADER_KWARGS_DEFAULT.items()}
        if data_loader_kwargs:
            data_loader_kwargs_.update(data_loader_kwargs)

        return torch.utils.data.DataLoader(out, **data_loader_kwargs_)


global WRAPPER
WRAPPER = None


def get_wrapper_class():
    global WRAPPER
    if WRAPPER is not None:
        return WRAPPER
    import torch

    class WrapperWeatherBenchDataset(torch.utils.data.Dataset):
        def __init__(self, ds, offset) -> None:
            super().__init__()

            self.ds = ds

            self.stats = self.ds.statistics()
            self.offset = offset

        def __len__(self):
            """Returns the length of the dataset. This is important! Pytorch must know this."""
            return self.stats["count"] - self.offset

        def __getitem__(self, i):  # -> Tuple[np.ndarray, ...]:
            # Q: if ds[i] is a iterator, would ds[i] read the data from 0 to i, just to provide i?
            """Returns the i-th sample (x, y). Pytorch will take care of the shuffling after each epoch."""
            # print('getting',i)
            x, Y = (
                self.ds[i].to_numpy()[None, ...],
                self.ds[i + self.offset].to_numpy()[None, ...],
            )
            x = x.astype(np.float32)
            Y = Y.astype(np.float32)
            return x, Y

    WRAPPER = WrapperWeatherBenchDataset
    return get_wrapper_class()


source = IndexedSource
