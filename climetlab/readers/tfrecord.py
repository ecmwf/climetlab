# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

from . import Reader

LOG = logging.getLogger(__name__)


class TfRecordReader(Reader):
    def to_tfdataset(self, **kwargs):
        import tensorflow as tf

        tfrecord = tf.data.TFRecordDataset(self.path)
        return tfrecord


def reader(source, path, magic, deeper_check):
    if path.endswith(".tfrecord"):
        return TfRecordReader(source, path)
