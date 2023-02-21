# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

from itertools import zip_longest
import logging

import numpy as np

LOG = logging.getLogger(__name__)

from .tensorflow import default_merger, as_numpy_func


class PytorchMixIn:
    def to_pytorch_dataloader(self, *args, dataloader_kwargs=None, **kwargs):
        import torch

        num_workers = 1

        dataset = self.to_pytorch(self, *args, **kwargs)

        default_kwargs = dict(
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
        merged_kwargs = {k: v for k, v in default_kwargs.items()}
        if dataloader_kwargs:
            merged_kwargs.update(dataloader_kwargs)

        return torch.utils.data.DataLoader(dataset, **merged_kwargs)

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

    def to_pytorch(self, *args, **kwargs):
        if "features" not in kwargs:
            kwargs["features"] = [self]

        if "total_size" not in kwargs:
            kwargs["total_size"] = len(self)

        return to_pytorch2(*args, **kwargs)


def to_pytorch2(
    *args,
    total_size,
    features=None,
    targets=None,
    num_parallel_calls=10,
    prefetch=1024,
    merger=default_merger,
    targets_merger=default_merger,
    shuffle_buffer_size=100,
    options=None,
    targets_options=None,
    **kwargs,
):
    import torch

    assert not args, args
    import tensorflow as tf

    if targets is None:
        targets = []

    if options is None:
        options = [{} for i in features]

    if targets_options is None:
        targets_options = [{} for i in targets]

    assert isinstance(features, (list, tuple)), features
    assert len(features) == len(options), (len(features), len(options))
    funcs = [
        as_numpy_func(_, opt) for _, opt in zip_longest(features, options, fillvalue={})
    ]
    funcs_targets = [
        as_numpy_func(_, opt)
        for _, opt in zip_longest(targets, targets_options, fillvalue={})
    ]

    func = merger(*funcs)
    func_targets = targets_merger(*funcs_targets)

    class ClimetlabTorchDataset(torch.utils.data.Dataset):
        def __len__(self):
            """Returns the length of the dataset. Pytorch must know this."""
            return total_size

        def __getitem__(self, i):  # -> Tuple[np.ndarray, ...]:
            """Returns the i-th sample (x, y). Pytorch will take care of the shuffling after each epoch."""
            x = func(i)
            Y = func_targets(Y)
            x = x.astype(np.float32)  # not needed ?
            Y = Y.astype(np.float32)  # not needed ?
            return x, Y

        # def __iter__(self):
        #    raise NotImplementedError('TODO')

    return ClimetlabTorchDataset()
