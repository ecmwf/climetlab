# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def merge(
    sources=None,
    paths=None,
    reader_class=None,
    **kwargs,
):
    if paths is not None:
        if reader_class is not None and hasattr(reader_class, "to_tfdataset_multi"):
            return reader_class.to_tfdataset_multi(paths, **kwargs)

    ds = sources[0].to_tfdataset()
    for s in sources[1:]:
        ds = ds.concatenate(s.to_tfdataset())
    return ds
