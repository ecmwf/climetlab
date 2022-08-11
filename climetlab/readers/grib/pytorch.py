# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

import numpy as np

LOG = logging.getLogger(__name__)


class PytorchMixIn:
    def to_pytorch(self, offset, data_loader_kwargs=None):
        import torch

        # sometimes (!) causes an Exception:
        # gribapi.errors.UnsupportedEditionError: Edition not supported.
        num_workers = 1

        out = self._to_pytorch_wrapper_class()(self, offset)

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

    def _to_pytorch_wrapper_class(self):
        import torch

        class WrapperWeatherBenchDataset(torch.utils.data.Dataset):
            def __init__(self, ds, offset) -> None:
                super().__init__()
                self.ds = ds
                self.stats = ds.statistics()
                self.offset = offset

            def __len__(self):
                """Returns the length of the dataset. This is important! Pytorch must know this."""
                return len(self.ds) - self.offset
                return self.ds.stats["count"] - self.ds.offset

            def __getitem__(self, i):  # -> Tuple[np.ndarray, ...]:
                """Returns the i-th sample (x, y). Pytorch will take care of the shuffling after each epoch."""
                # Q: if self is a iterator, would ds[i] read the data from 0 to i, just to provide i?

                x, Y = (
                    self.ds[i].to_numpy()[None, ...],
                    self.ds[i + self.offset].to_numpy()[None, ...],
                )
                x = x.astype(np.float32)
                Y = Y.astype(np.float32)
                return x, Y

        return WrapperWeatherBenchDataset
