# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


def _concat(sources, *args, **kwargs):
    ds = sources[0].to_tfdataset(**kwargs)
    for s in sources[1:]:
        ds = ds.concatenate(s.to_tfdataset(**kwargs))
    return ds


def _zip(sources, *args, **kwargs):
    import tensorflow as tf

    return tf.data.Dataset.zip(tuple(s.to_tfdataset(**kwargs) for s in sources))


def merge(
    sources=None,
    paths=None,
    reader_class=None,
    **kwargs,
):
    if paths is not None:
        if reader_class is not None and hasattr(reader_class, "to_tfdataset_multi"):
            return reader_class.to_tfdataset_multi(paths, **kwargs)

    method = "_" + kwargs.get("method", "concat")
    return globals()[method](sources, paths, reader_class, **kwargs)
