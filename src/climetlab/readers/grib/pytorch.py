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

from .tensorflow import default_merger, to_funcs

LOG = logging.getLogger(__name__)


def to_pytorch(
    total_size=None,
    features=None,
    targets=None,
    options=None,
    targets_options=None,
    merger=default_merger,
    targets_merger=default_merger,
    #
    num_parallel_calls=10,
    prefetch=1024,
    shuffle_buffer_size=100,
    **kwargs,
):
    if total_size is None:
        total_size = len(features[0])
        print("totalsize", total_size)

    import torch

    func, func_targets = to_funcs(
        features, targets, options, targets_options, merger, targets_merger
    )

    class ClimetlabTorchDataset(torch.utils.data.Dataset):
        def __len__(self):
            """Returns the length of the dataset. Pytorch must know this."""
            return total_size

        def __getitem__(self, i):  # -> Tuple[np.ndarray, ...]:
            """Returns the i-th sample (x, y). Pytorch will take care of the shuffling after each epoch."""
            x = func(i)
            Y = func_targets(i)
            x = x.astype(np.float32)  # not needed ?
            Y = Y.astype(np.float32)  # not needed ?
            return x, Y

        # def __iter__(self):
        #    raise NotImplementedError('TODO')

    return ClimetlabTorchDataset()


class PytorchMixIn:
    def to_pytorch_dataloader(self, *args, dataloader_kwargs=None, **kwargs):
        from climetlab.ml.torch import to_pytorch_dataloader

        if dataloader_kwargs is None:
            dataloader_kwargs = {}
        dataset = self.to_pytorch(*args, **kwargs)
        return to_pytorch_dataloader(dataset, **dataloader_kwargs)

    def to_pytorch(self, *args, **kwargs):
        if "features" not in kwargs:
            kwargs["features"] = [self]

        return to_pytorch(*args, **kwargs)
