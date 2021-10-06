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

    _tfrecord = None
    _len = None

    @property
    def tfrecord(self):
        return type(self).to_tfdataset_multi([self.path])

    def to_tfdataset(self, **kwargs):
        return self.tfrecord

    @classmethod
    def to_tfdataset_multi(cls, paths, **kwargs):
        import tensorflow as tf

        files_ds = tf.data.Dataset.list_files(paths)
        options = tf.data.Options()
        # options.experimental_deterministic = False
        files_ds = files_ds.with_options(options)
        return tf.data.TFRecordDataset(
            files_ds,
            num_parallel_reads=tf.data.experimental.AUTOTUNE,
        )

    def __len__(self):
        if self._len is None:
            record = self.tfrecord
            try:
                self._len = len(record)
            except TypeError:
                self._len = 0
                for _ in record:
                    self._len += 1
        return self._len


def reader(source, path, magic=None, deeper_check=False):
    if magic is None or path.endswith(".tfrecord"):
        return TfRecordReader(source, path)
