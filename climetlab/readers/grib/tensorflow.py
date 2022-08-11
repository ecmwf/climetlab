# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from climetlab.profiling import call_counter

LOG = logging.getLogger(__name__)


class TensorflowMixIn:
    def to_tfdataset(
        self,
        split=None,
        shuffle=None,
        normalize=None,
        batch_size=0,
        **kwargs,
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

        if isinstance(label, str):
            label_ = label
            label = lambda s: s.handle.get(label_)  # noqa: E731

        @call_counter
        def generate():
            for s in self:
                yield s.to_numpy(), label(s)

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
