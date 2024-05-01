# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

LOG = logging.getLogger(__name__)


def _find_device():
    try:
        import torch
    except ImportError:
        LOG.debug("Torch not found")
        return None

    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return "mps"
    if torch.cuda.is_available() and torch.backends.cuda.is_built():
        return "cuda"
    LOG.debug("Found no GPU, using CPU")
    return "cpu"


device = _find_device()


def to_pytorch_dataloader(dataset, **kwargs):
    import torch

    default_kwargs = dict(
        batch_size=128,
        # multi-process data loading
        # use as many workers as you have cores on your machine
        num_workers=1,
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
    if kwargs:
        merged_kwargs.update(kwargs)

    return torch.utils.data.DataLoader(dataset, **merged_kwargs)
