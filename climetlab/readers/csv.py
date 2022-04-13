# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import csv
import io
import logging
import mimetypes
import os
import zipfile

from climetlab.wrappers import get_wrapper

from . import Reader

LOG = logging.getLogger(__name__)


class ZipProbe:
    def __init__(self, path, newline=None, encoding=None):
        zip = zipfile.ZipFile(path)
        members = zip.infolist()
        self.f = zip.open(members[0].filename)
        self.encoding = encoding

    def read(self, size):
        bytes = self.f.read(size)
        return bytes.decode(self.encoding)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        pass


def probe_csv(
    path,
    probe_size=4096,
    compression=None,
    for_is_csv=False,
    minimum_columns=2,
    minimum_rows=2,
):

    OPENS = {
        None: open,
        "zip": ZipProbe,
    }

    try:
        import gzip

        OPENS["gzip"] = gzip.open
    except ImportError:
        pass

    try:
        import bz2

        OPENS["bz2"] = bz2.open
    except ImportError:
        pass

    try:
        import lzma

        OPENS["lzma"] = lzma.open
    except ImportError:
        pass

    _open = OPENS[compression]

    try:
        with _open(path, newline="", encoding="utf-8") as f:
            sample = f.read(probe_size)
            sniffer = csv.Sniffer()
            dialect, has_header = sniffer.sniff(sample), sniffer.has_header(sample)

            LOG.debug("dialect = %s", dialect)
            LOG.debug("has_header = %s", has_header)
            if hasattr(dialect, "delimiter"):
                LOG.debug("delimiter = '%s'", dialect.delimiter)

            if for_is_csv:
                # Check that it is not a trivial text file.
                reader = csv.reader(io.StringIO(sample), dialect)
                if has_header:
                    header = next(reader)
                    LOG.debug("for_is_csv header %s", header)
                    if len(header) < minimum_columns:
                        return None, False
                cnt = 0
                length = None
                for row in reader:
                    cnt += 1
                    LOG.debug("for_is_csv row %s %s", cnt, row)
                    if length is None:
                        length = len(row)
                    if length != len(row):
                        return None, False
                    if cnt >= minimum_rows:
                        break

                if cnt < minimum_rows:
                    return None, False

            return dialect, has_header

    except UnicodeDecodeError:
        return None, False

    except csv.Error:
        return None, False


def is_csv(path, probe_size=4096, compression=None):

    _, extension = os.path.splitext(path)

    if extension in (".xml",):
        return False

    dialect, _ = probe_csv(path, probe_size, compression, for_is_csv=True)
    return dialect is not None


class CSVReader(Reader):
    def __init__(self, source, path, compression=None):
        super().__init__(source, path)
        self.compression = compression
        self.dialect, self.has_header = probe_csv(path, compression=compression)

    def to_pandas(self, **kwargs):
        import pandas

        pandas_read_csv_kwargs = kwargs.get("pandas_read_csv_kwargs", {})
        if self.compression is not None:
            pandas_read_csv_kwargs = dict(**pandas_read_csv_kwargs)
            pandas_read_csv_kwargs["compression"] = self.compression

        LOG.debug("pandas.read_csv(%s,%s)", self.path, pandas_read_csv_kwargs)
        return pandas.read_csv(self.path, **pandas_read_csv_kwargs)

    def to_tfdataset(self, batch_size=1000, **kwargs):
        # See https://www.tensorflow.org/api_docs/python/tf/data/experimental/make_csv_dataset
        import tensorflow as tf

        # TODO: uncompress in cache
        assert self.compression in (None, "gzip")

        options = {}
        if self.dialect is not None:
            COMPRESSIONS = {
                None: None,
                "gzip": "GZIP",
                "????": "ZLIB",  # Which one is that? zip?
            }
            options = dict(
                # column_names=None,
                # column_defaults=None,
                # label_name=None,
                # select_columns=None,
                # # Do not trust the delimiter found by csv sniffer,
                # # as it is wrong for files with only one column.
                # field_delim=self.dialect.delimiter,
                use_quote_delim=self.dialect.doublequote,  # Not sure about that one
                # na_value="",
                header=self.has_header,
                compression_type=COMPRESSIONS[self.compression],
                # ignore_errors=False,
            )

        return tf.data.experimental.make_csv_dataset(
            self.path,  # Can be a pattern
            batch_size,
            **options,
        )

    @classmethod
    def to_tfdataset_multi(cls, paths, batch_size=1000, **kwargs):
        # See https://www.tensorflow.org/api_docs/python/tf/data/experimental/make_csv_dataset
        import tensorflow as tf

        options = {}
        # TODO: read dialect(s) in options

        return tf.data.experimental.make_csv_dataset(
            paths,
            batch_size,
            **options,
        )

    def plot_graph(self, backend):
        get_wrapper(self.to_pandas()).plot_graph(backend)

    def plot_map(self, backend):
        get_wrapper(self.to_pandas()).plot_map(backend)

    def to_metview(self):
        from climetlab.metview import mv_read_table

        assert self.compression is None
        # TODO: use dialect
        return mv_read_table(table_filename=self.path)


def reader(source, path, magic, deeper_check, fwf=False):
    kind, compression = mimetypes.guess_type(path)

    if kind == "text/csv":
        return CSVReader(source, path, compression=compression)

    if deeper_check and False:
        if is_csv(path):
            return CSVReader(source, path)
