import json
import numpy as np
import tqdm
import climetlab as cml
import math
import queue
import threading

from climetlab.utils import humanize

from mydatasets.ecpoint_test import EcpointTest
from mydatasets.s2s_test import S2sTest


def worker(queue):
    while True:
        task = queue.get()
        if task is None:
            queue.task_done()
            return
        task.execute()
        queue.task_done()


class FieldsToRead:
    def __init__(self, j_slice, runner):
        self.size = j_slice.stop - j_slice.start
        self.j_slice = j_slice
        self.runner = runner

        self.lst = [None] * self.size
        self._filled = 0

        self.lock = threading.Lock()
        self.pbar = None

    def append(self, j, arr):
        offset = self.j_slice.start
        with self.lock:
            if self.pbar is None:
                self.pbar = tqdm.tqdm(
                    total=self.size,
                    desc=f"Reading {self.j_slice.start}-{self.j_slice.stop}",
                    smoothing=0.0,
                    unit_scale=True,
                    leave=False,
                )
                self.pbar.get_lock()
            self.lst[j - offset] = arr
            self._filled += 1
            self.pbar.update(1)

            # when reading all the fields in j_slice, trigger writing
            #            print(self._filled, self.size)
            assert self._filled <= self.size
            if self._filled == self.size:
                self.runner.trigger_writing(self)
                self.lst = None

    def get_sliced(self, i, i_last):
        return [b[i:i_last] for b in self.lst]


class FakeField:
    def __init__(self, value, shape):
        self.value = value
        self.shape = shape

    def to_numpy(self, *args, **kwargs):
        if len(self.shape) == 1:
            return np.arange(self.shape[0]).astype(np.float32) * 100 + self.value
        return np.zeros(self.shape, np.float32) + self.value


class FakeSource:
    def __init__(self, *ns, shape):
        self.ns = ns
        self.shape = shape
        self.coords = {n: list(range(n)) for n in ns}

    def order_by(self, *args, **kwargs):
        return self

    def __getitem__(self, j):
        return FakeField(value=j, shape=self.shape)

    def __len__(self):
        return math.prod(self.ns)


class Timeseries:
    _size = None
    dtype = "float32"
    # dtype = 'float16'

    @property
    def metadata_filename(self):
        return self.filename + ".metadata"

    @property
    def size(self):
        if self._size is None:
            n = math.prod(self.shape)
            self._size = n * np.dtype(self.dtype).itemsize
            print(f"Array: {self.shape}({self.dtype},{humanize.bytes(self.size)})")
        return self._size


class TimeseriesWriter(Timeseries):
    def __init__(
        self,
        source,
        filename=None,
        nthreads_write=10,
        nthreads_read=4,
        n_gridpoints=1024,
        n_fields=1024,
    ):
        # threads, n_fields, ETA
        # 1      , 1024  , 2h30
        print(f"Reading from {len(source)} fields")

        if filename is None:
            filename = source.path_ts
        assert isinstance(filename, str), filename

        self.itemsize = np.dtype(self.dtype).itemsize

        self.nthreads_write = nthreads_write
        self.nthreads_read = nthreads_read
        self.n_gridpoints = n_gridpoints
        self.n_fields = n_fields

        self.filename = filename

        self.source = source

        self.shape_i = self.infer_shape_i()

        self.shape_j = len(source)
        self.coords = source.coords
        self.coords_j = self.coords
        self.shape = (self.shape_i, self.shape_j)

        with open(self.filename, "a+") as f:
            pass

        print(f"shape_i = {self.shape_i} values on each field (dim i)")
        print(f"shape_j = {self.shape_j} fields (dim j)")
        print(
            f"Total shape = {self.shape[0]} x {self.shape[1]} = {self.shape[0]*self.shape[1]}"
        )

        n_expected_fields = math.prod([len(v) for k, v in self.coords_j.items()])
        if n_expected_fields != len(self.source):
            raise ValueError(
                f"Expecting {n_expected_fields} fields but got {len(self.source)}."
            )

    def infer_shape_i(self):
        return math.prod(self.read_one_field(0).to_numpy().shape)

    def read_one_field(self, j):
        return self.source[j]

    def reader(self):
        while True:
            task = self.rqueue.get()
            if task is None:
                self.rqueue.task_done()
                return
            self.read_fields(task)
            self.rqueue.task_done()

    def writer(self):
        file_handle = open(self.filename, "r+b")  # , buffering=0)
        while True:
            task = self.queue.get()
            if task is None:
                self.queue.task_done()
                file_handle.close()
                return
            self.write_block(task, file_handle)
            self.queue.task_done()

    def read_fields(self, task):
        blocks, j = task

        field = self.read_one_field(j)
        arr = field.to_numpy()

        # arr = arr.flatten()  # make a copy
        arr = arr.ravel()  # make a view

        arr = arr.astype(self.dtype)
        assert arr.shape == (self.shape_i,), (
            field,
            j,
            arr.shape,
            self.shape_i,
        )
        del field

        blocks.append(j, arr)

    def write_block(self, task, file_handle):
        j_slice, i_slice, blocks, pbar_gridpoints = task
        if not blocks:
            return

        arr = np.array(blocks).T

        # print(f'writing at {i_slice, j_slice}: ', end='')
        for i in range(i_slice.start, i_slice.stop):
            seek = i * self.shape_j + j_slice.start
            file_handle.seek(seek * self.itemsize)
            assert len(arr.shape) == 2, arr.shape
            a = arr[i - i_slice.start, :]
            # print(f'{seek}({seek * self.itemsize})-', end='')
            file_handle.write(a.tobytes())
            # self.pbar_gridpoints.update(1)
        # print()
        pbar_gridpoints.update(i_slice.stop - i_slice.start)
        self.pbar.update(math.prod(arr.shape))

    def run(self):

        self.queue = queue.Queue(
            maxsize=50
        )  # (self.shape_i // self.n_gridpoints) * 2 + 2)
        self.rqueue = queue.Queue()

        self.pbar = tqdm.tqdm(
            total=math.prod(self.shape),
            desc="values",
            smoothing=0.0,
            unit_scale=True,
        )
        self.pbar.get_lock()  # Workaround on pbar race condition

        for i in range(0, self.nthreads_write):
            threading.Thread(target=self.writer, daemon=True).start()

        for i in range(0, self.nthreads_read):
            threading.Thread(target=self.reader, daemon=True).start()

        range_j = range(0, self.shape_j, self.n_fields)
        for j in range_j:  # each batch of fields
            j_last = min(j + self.n_fields, self.shape_j)

            blocks = FieldsToRead(slice(j, j_last), self)

            for j_ in range(j, j_last):
                self.rqueue.put((blocks, j_))

        for i in range(0, self.nthreads_read):
            self.rqueue.put(None)
        self.rqueue.join()

        for i in range(0, self.nthreads_write):
            self.queue.put(None)
        self.queue.join()

        self.write_metadata()

    def trigger_writing(self, fields_to_write):

        length = fields_to_write.j_slice.stop - fields_to_write.j_slice.start
        pbar_gridpoints = tqdm.tqdm(
            total=length,
            desc=f"Writing",
            smoothing=0.0,
            unit_scale=True,
        )
        pbar_gridpoints.get_lock()

        range_i = range(0, self.shape_i, self.n_gridpoints)
        for i in range_i:  # each grid point by batch of self.n_gridpoints
            i_last = min(i + self.n_gridpoints, self.shape_i)

            self.queue.put(  # write queue
                (
                    fields_to_write.j_slice,
                    slice(i, i_last),
                    fields_to_write.get_sliced(i, i_last),
                    pbar_gridpoints,
                ),
            )

    def write_metadata(self):
        metadata = {}
        metadata["dtype"] = self.dtype
        metadata["shape"] = self.shape
        metadata["coords"] = self.coords

        map_coords = dict(values=list(range(0, self.shape_i)))
        metadata["map_coords"] = map_coords

        with open(self.metadata_filename, "w") as f:
            json.dump(metadata, indent=4, fp=f)
        print(f"Wrote metadata {self.metadata_filename}")


class TimeseriesReader(Timeseries):
    def __init__(self, filename):
        self.filename = filename

        with open(self.metadata_filename) as f:
            metadata = json.loads(f.read())

        self.dtype = metadata["dtype"]
        self.coords = metadata["coords"]
        self.map_coords = metadata["map_coords"]
        print("**********************")

        self.all_coords = {}
        for k, v in self.map_coords.items():
            self.all_coords[k] = v
        for k, v in self.coords.items():
            self.all_coords[k] = v
        self.shape = tuple([len(v) for k, v in self.all_coords.items()])

        print(
            f"Reading file {self.filename}, expecting {self.shape} = {math.prod(self.shape) * np.dtype(self.dtype).itemsize} bytes"
        )
        self.array = np.memmap(
            self.filename, dtype=np.dtype(self.dtype), mode="r", shape=self.shape
        )

    def to_xarray(self):
        import xarray as xr

        print("all coords keys", [(k, len(v)) for k, v in self.all_coords.items()])
        dims = list(self.all_coords.keys())
        return xr.DataArray(data=self.array, dims=dims, coords=self.all_coords)

    def to_pandas(self):
        raise NotImplementedError()


class HdfTimeseries(TimeseriesWriter):
    @property
    def array(self):
        if self._array:
            return self._array
        import h5py

        f = h5py.File(self.filename, "w")  # , driver='core')
        self._array = f.create_dataset("data", self.shape, dtype=self.dtype)
        return self.array


class HdfTimeseriesWriter(HdfTimeseries, TimeseriesWriter):
    pass


class HdfTimeseriesReader(HdfTimeseries, TimeseriesReader):
    pass


# class NCTimeseriesWriter(TimeseriesWriter):
#    @property
#    def array(self):
#        if self._array:
#            return self._array
#
#        from netCDF4 import Dataset
#
#        f = Dataset(self.filename, mode="w")
#        keys = tuple()
#        chunks = []
#        assert len(self.shape_i) == 1 # TODO: else create lat/lon
#        f.createDimension('values', range(0, self.shape_i[0]))
#        for k,values in self.coords:
#            f.createDimension(k, values)
#            keys.append(k)
#
#        assert self.dtype == 'float32' # TODO: else ...
#
#
#        ds = f.createVariable(
#                "all",
#                "f4",221G
#                tuple(keys)
#                chunksizes=(1, 1, FINAL_DATE_CHUNKSIZE),
#                # ("date", "lat", "lon"),
#                # chunksizes=(1, lat_, lon_),
#            )
#        print("Writing this:")
#        print(ds.shape)
#        print(ds.chunking())
#        return f, ds

WritterClass = TimeseriesWriter


def test1():
    source = FakeSource(5, shape=(9,))
    # source = FakeSource(5, shape=(3, 3))
    t = WritterClass(source, filename="transpose.1.bin", n_gridpoints=5, n_fields=3)
    t.run()
    r = TimeseriesReader(filename="transpose.1.bin")
    xds = r.to_xarray()


def test2():
    source = FakeSource(18, shape=(24))
    t = WritterClass(source, filename="transpose.2.bin", n_gridpoints=200, n_fields=10)
    t.run()
    r = TimeseriesReader(filename="transpose.2.bin")
    xds = r.to_xarray()


def test3():
    source = FakeSource(6, shape=(24, 36))
    t = WritterClass(source, filename="transpose.3.bin", n_gridpoints=200, n_fields=4)
    t.run()
    r = TimeseriesReader(filename="transpose.3.bin")
    xds = r.to_xarray()
    # print(xds)


def test4():
    source = FakeSource(6, 5, shape=(24, 36))
    t = WritterClass(
        source, filename="transpose.4.bin", n_gridpoints=20000, n_fields=5000
    )
    t.run()
    r = TimeseriesReader(filename="transpose.4.bin")
    xds = r.to_xarray()


def ecpoint_full_write():
    data = cml.load_dataset("ecpoint-test", "full")

    print(len(data), "fields")

    t = WritterClass(data)
    t.run()


def ecpoint_full_read():
    data = cml.load_dataset("ecpoint-test", "full")
    r = TimeseriesReader(data.path_ts)
    xds = r.to_xarray()
    print(xds)


def test5_write(subset):
    data = cml.load_dataset("ecpoint-test", subset)

    print(len(data), "fields")

    t = WritterClass(data)
    t.run()


def test5_read(subset):
    data = cml.load_dataset("ecpoint-test", subset)
    r = TimeseriesReader(data.path_ts)
    # print(r.array[-2:,-2:])
    xds = r.to_xarray()
    print(xds)


# write in auxiliary file when writers has finished
# to parallelise and to help reading

# split grib key for filename and in matrix coordinate (lat/lon/values always outer loop)

# check size are uniform
# with grib.get("md5GridSection")


def test6():

    source = cml.load_source("directory", DATA2)
    source = source.sel(step=24)
    source = source.order_by("date")

    t = GribTransposer(source)
    t.filename = path_ts2
    shape = t.shape

    t.run()
    array = read_output(path_ts2, shape)
    check(array)


def tests2s():
    selection = dict(
        param=["tp"],
        step=[24, 48],
        origin=["ecmf"],
        number=[0, 1, 2],
        date=[20200102],
        # hdate="20000102/20010102/20020102/20030102/20040102/20050102/20060102/20070102/20080102/20090102/20100102/20110102/20120102/20130102/20140102/20150102/20160102/20170102/20180102/20190102".split(
        #    "/"
        # ),
        hdate="20000102/20010102/20020102".split("/"),
    )
    source = S2STest(**selection)
    for k, v in selection.items():
        assert v == source.coords[k]
    for k, v in source.coords.items():
        assert v == selection[k]

    selection = source.coords

    print(source.coords)

    source = source.sel(selection)
    print(len(source), "fields")
    print(source.coord("hdate"))
    print(source.coords)

    t = WritterClass(source, filename="transposition.s2s.bin", coords=selection)
    t.run()


def check(array):
    print()
    print(f"Loaded ok: {array.shape}")
    print(array[12, 12, :])
    print(array[12, 12, :].mean())
    return array


if __name__ == "__main__":
    # print("- TEST 1 -")
    # test1()

    ##  print("- TEST 2 -")
    ##  test2()

    # print("- TEST 3 -")
    # test3()

    # print("- TEST 4 -")
    # test4()

    # print("- TEST 5 - small")
    # test5_write('small')
    # test5_read('small')

    # print("- TEST 5 - medium")
    # test5_write("medium")
    # test5_read("medium")

    # print("- TEST 5 - large")
    # test5_write("large")
    # 5 min without writing.
    # ETA~1h30 with Timeseries
    # ETA~1h with Timeseries2
    # note: with early astype(): ETA~55 min with Timeseries2
    # test5_read("large")

    # print("- TEST 5 - per year")
    # for i in range(2000, 2019):
    #    print("year ", i)
    #    data = cml.load_dataset("ecpoint-test",i)
    #    print(len(data), "fields")
    #    t = WritterClass(data, nthreads_write=1, write_i_chunk_size=1024*1024*1024, nfields_chunks=1464)
    #    t.run()

    print("- TEST ECPOINT -")
    ecpoint_full_write()
    # ETA with TimeSeries: 9k min (450k / 512 * 10min)
    # ETA with TimeSeries2: 12k min (540k/8k * 240min)
    ecpoint_full_read()

# test2()
# test3()
# check(read_output(path_ts, (121, 240, 3180)))
