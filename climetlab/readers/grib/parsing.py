# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
import datetime
import logging
import os
import sys
import time
from multiprocessing import Process, Queue

from tqdm import tqdm

from climetlab.utils import progress_bar
from climetlab.utils.humanize import plural, seconds

LOG = logging.getLogger(__name__)


def post_process_valid_date(field, h):
    date = h.get("validityDate")
    time = h.get("validityTime")
    field["datetime"] = datetime.datetime(
        date // 10000,
        date % 10000 // 100,
        date % 100,
        time // 100,
        time % 100,
    )
    # Note that we do not create a script here:
    # There is no ".isoformat()". Because the sql database
    # takes care of this conversion back and forth.
    return field


def post_process_parameter_level(field, h):
    param = field.get("param", None)
    if param is None:
        field["param_level"] = None
        return field

    level = field.get("levelist", None)
    if level is None:
        field["param_level"] = param
        return field

    field["param_level"] = f"{param}_{level}"
    return field


def post_process_statistics(field, h):
    values = h.get("values")
    field["mean"] = values.mean()
    field["std"] = values.std()
    field["min"] = values.min()
    field["max"] = values.max()
    field["shape"] = ",".join([str(_) for _ in values.shape])
    return field


def _index_grib_file(
    path,
    with_statistics=False,
    with_valid_date=True,
    with_parameter_level=True,
    position=0,
):
    import eccodes

    from climetlab.readers.grib.codes import CodesHandle

    post_process_mars = []
    if with_valid_date:
        post_process_mars.append(post_process_valid_date)
    if with_parameter_level:
        post_process_mars.append(post_process_parameter_level)
    if with_statistics:
        post_process_mars.append(post_process_statistics)

    def parse_field(h):
        field = h.as_mars()

        if post_process_mars:
            for f in post_process_mars:
                field = f(field, h)

        field["_path"] = path
        field["_offset"] = h.get_long("offset")
        field["_length"] = h.get_long("totalLength")
        field["_param_id"] = h.get_string("paramId")
        field["md5_grid_section"] = h.get("md5GridSection")

        # eccodes.codes_get_string(h, "number") returns "0"
        # when "number" is not in the iterator
        # remove? field["number"] = h.get("number")

        return field

    size = os.path.getsize(path)
    pbar = tqdm(
        desc=f"Parsing {path}",
        total=size,
        unit_scale=True,
        unit_divisor=1024,
        unit="B",
        leave=False,
        # position=TQDM_POSITION,
        position=position,
        dynamic_ncols=True,
    )

    with open(path, "rb") as f:
        old_position = f.tell()
        h = eccodes.codes_grib_new_from_file(f)

        while h:
            yield parse_field(CodesHandle(h, path, offset=old_position))

            position = f.tell()
            pbar.update(position - old_position)
            old_position = position
            h = eccodes.codes_grib_new_from_file(f)

    pbar.close()


def _index_url(url):
    import climetlab as cml

    path = cml.load_source("url", url).path
    # TODO: should use download_and_cache
    # path = download_and_cache(url)
    for entry in _index_grib_file(path):
        del entry["_path"]
        yield entry


def _index_path(path):
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for name in files:
                yield from _index_grib_file(os.path.join(root, name))
    else:
        yield from _index_grib_file(path)


class GribIndexingDirectoryParserIterator:
    """This class delays parsing the directory for the list of files
    until the iterator is actually used (calling __iter__)
    """

    def __init__(
        self,
        directory,
        db_path,
        relative_paths,
        extensions=[".grib", ".grib1", ".grib2"],
        followlinks=True,
        verbose=False,
        with_statistics=True,
    ):
        self.db_path = db_path
        self.extensions = set(extensions)
        self.directory = directory
        self.relative_paths = relative_paths
        self.followlinks = followlinks
        self.verbose = verbose
        self.with_statistics = with_statistics

        self._tasks = None

    def _new_db(self):
        from climetlab.indexing.database.sql import SqlDatabase

        return SqlDatabase(self.db_path)

    def worker(self, i):
        _i = i
        time.sleep(i)
        while True:
            task = self.q_in.get()
            if task is None:
                break
            n = self.process_path(_i, task)
            self.q_out.put(n)

    def load_database(self):
        start = datetime.datetime.now()

        n_proc = 5
        if sys.platform == "win32":
            n_proc = 1  # deactivate multiprocessing for window

        if n_proc == 1:
            count = 0
            for path in self.tasks:
                count += self.process_path(0, path)
        else:
            assert n_proc > 1, n_proc

            self.q_in = Queue()
            self.q_out = Queue()

            workers = []
            for i in range(n_proc):
                proc = Process(target=self.worker, args=(i,))
                proc.start()
                workers.append(proc)

            for path in self.tasks:
                self.q_in.put(path)

            for i in range(n_proc):
                self.q_in.put(None)

            count = 0
            for _ in progress_bar(iterable=self.tasks, total=len(self.tasks)):
                count += self.q_out.get()

            for p in workers:
                p.join()

            del self.q_in
            del self.q_out

        self._new_db().build_indexes()

        end = datetime.datetime.now()
        print(f"Indexed {plural(count,'field')} in {seconds(end - start)}.")

    def process_path(self, i, path):
        db = self._new_db()

        if db.already_loaded(self._format_path(path), self):
            LOG.warning(f"Skipping {path}, already loaded")
            return 0

        lst = []
        LOG.debug(f"Parsing file {path}")

        try:
            for field in _index_grib_file(
                path,
                with_statistics=self.with_statistics,
                position=i + 1,
            ):
                field["_path"] = self._format_path(path)
                lst.append(field)
        except PermissionError as e:
            LOG.error(f"Could not read {path}: {e}")
            return 0
        except Exception as e:
            LOG.exception(f"(grib-parsing) Ignoring {path}, {e}")
            return 0

        if not lst:
            LOG.warn(f"No entry found in {path}.")
            return 0

        return db.load_iterator(lst)

    @property
    def tasks(self):
        if self._tasks is not None:
            return self._tasks

        LOG.debug(f"Parsing files in {self.directory}")
        assert os.path.exists(self.directory), f"{self.directory} does not exist"
        assert os.path.isdir(self.directory), f"{self.directory} is not a directory"

        tasks = []
        for root, _, files in os.walk(self.directory, followlinks=self.followlinks):
            for name in files:
                path = os.path.join(root, name)
                _, ext = os.path.splitext(path)
                if ext not in self.extensions:
                    continue
                tasks.append(path)
        tasks = sorted(tasks)

        if tasks:
            if self.verbose:
                print(f"Found {len(tasks)} files to index.")
        else:
            LOG.error(f"Could not find any files to index in {self.directory}")

        self._tasks = tasks

        return self.tasks

    def _format_path(self, path):
        return {
            None: lambda x: x,
            True: lambda x: os.path.relpath(x, self.directory),
            False: lambda x: os.path.abspath(x),
        }[self.relative_paths](path)
