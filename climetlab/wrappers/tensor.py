# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab.utils import module_loaded
from climetlab.wrappers import get_wrapper


def wrapper(data, *args, **kwargs):
    if not module_loaded("torch"):
        return None

    import torch  # noqa

    if isinstance(data, torch.Tensor):
        return get_wrapper(data.detach().cpu().numpy(), *args, **kwargs)

    return None
