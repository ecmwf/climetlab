# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import pandas as pd


def merge(
    sources=None,
    paths=None,
    reader_class=None,
    **kwargs,
):
    options = dict(ignore_index=True)  # Renumber all indices
    options.update(kwargs)
    return pd.concat([s.to_pandas(**kwargs) for s in sources], **options)
