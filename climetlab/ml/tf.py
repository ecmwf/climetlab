# (C) Copyright 2022 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

import tensorflow as tf
from tensorflow.keras.layers import Conv2D

LOG = logging.getLogger(__name__)


class PeriodicConv2D(Conv2D):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.kernel_size

    def call(self, inputs):
        w, h = self.kernel_size
        inputs = tf.concat([inputs, inputs[:, :, :w, :]], axis=2)
        inputs = tf.pad(
            inputs, [[0, 0], [h // 2, h // 2], [0, 0], [0, 0]], constant_values=0
        )
        return super().call(inputs)
