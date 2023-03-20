# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import datetime
import fnmatch
import logging
import os
from multiprocessing import Pool, Process, Queue
import time

import climetlab
from climetlab.utils import progress_bar
from climetlab.utils.humanize import plural, seconds

LOG = logging.getLogger(__name__)


def post_process_valid_date(field, h):
    date = h.get("validityDate")
    time = h.get("validityTime")
    field["valid_datetime"] = datetime.datetime(
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
        ignore=None,
        followlinks=True,
        verbose=False,
        with_statistics=True,
    ):
        self.db_path = db_path
        if ignore is None:
            ignore = []
        self.ignore = ignore
        self.directory = directory
        self.relative_paths = relative_paths
        self.followlinks = followlinks
        self.verbose = verbose
        self.with_statistics = with_statistics

        self._tasks = None

    def _new_db(self):
        return climetlab.indexing.database.sql.SqlDatabase(self.db_path)

    def load_database(self):
        start = datetime.datetime.now()

        q_in = Queue()
        q_out = Queue()

        def worker(q_in, q_out, i, func):
            _i = i
            time.sleep(i)
            while True:
                task = q_in.get()
                if task is None:
                    break
                n = func(_i, task)
                q_out.put(n)

        nproc = 3

        workers = []
        for i in range(nproc):
            proc = Process(target=worker, args=(q_in, q_out, i, self.process_one_task))
            proc.start()
            workers.append(proc)

        for path in self.tasks:
            db = self._new_db()

            if db.already_loaded(self._format_path(path), self):
                LOG.warn(f"Skipping {path}, already loaded")
                continue

            q_in.put(path)

        for i in range(nproc):
            q_in.put(None)

        count = 0
        for _ in tqdm(self.tasks, total=len(self.tasks), dynamic_ncols=True):
            count += q_out.get()

        for p in workers:
            p.join()

        self._new_db().build_indexes()

        end = datetime.datetime.now()
        print(f"Indexed {plural(count,'field')} in {seconds(end - start)}.")

    def process_one_task(self, i, path):
        db = self._new_db()

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

        def _ignore(path):
            for ignore in self.ignore:
                if fnmatch.fnmatch(os.path.basename(path), ignore):
                    return True
            return False

        tasks = []
        for root, _, files in os.walk(self.directory, followlinks=self.followlinks):
            for name in files:
                path = os.path.join(root, name)
                if _ignore(path):
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
