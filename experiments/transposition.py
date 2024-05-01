# flake8: noqa
import json
import math
import queue
import sys
import threading

import numpy as np
import tqdm
from mydatasets.ecpoint_test import EcpointTest  # noqa
from mydatasets.s2s_test import S2sTest  # noqa

import climetlab as cml
from climetlab.utils import humanize


def worker_on_file(queue, filename):
    def target():
        # n = 10
        # count, file_handle = n, open(filename, "r+b")# , buffering=0)
        file_handle = open(filename, "r+b")  # , buffering=0)
        while True:
            task = queue.get()
            if task is None:
                queue.task_done()
                file_handle.close()
                return
            try:
                # count -= 1
                # if count == 0:
                #    file_handle.close()
                #    count, file_handle = n, open(filename, "r+b")#  , buffering=0)
                task.execute(file_handle)
            except Exception as e:
                print(e)
                raise (e)

            queue.task_done()

    return target


def worker(queue):
    def target():
        while True:
            task = queue.get()
            if task is None:
                queue.task_done()
                return
            try:
                task.execute()
            except Exception as e:
                print(e)
                raise (e)

            queue.task_done()

    return target


class ReadField:
    def __init__(self, j, runner, batches_of_fields):
        self.j = j
        self.runner = runner
        self.bofs = batches_of_fields

    def execute(self):
        field = self.runner.read_one_field(self.j)
        arr = field.to_numpy()

        # arr = arr.flatten()  # make a copy
        arr = arr.ravel()  # make a view

        arr = arr.astype(self.runner.dtype)
        assert arr.shape == (self.runner.shape_i,), (
            field,
            self.j,
            arr.shape,
            self.runner.shape_i,
        )
        del field

        self.runner.read_pbar.update(math.prod(arr.shape))
        # print(f"  +field", self.j)
        self.bofs.append(self.j, arr)


class AllBatchesOfFields:
    def __init__(self, next_queue, max, n_features, runner):
        self.runner = runner
        self.dic = dict()
        self.condition = threading.Condition()
        # self.condition = threading.Lock()
        self.next_queue = next_queue
        self.max = max
        self.n_features = n_features

    def append(self, j, arr):
        k = j // self.n_features  # batch_number

        with self.condition:
            while not (k in self.dic or len(self.dic) < self.max):
                self.condition.wait()

            if not k in self.dic:
                bof = OneBatchOfFields(k, self.runner)
                # print('Created bof', bof, 'j',j,'n_features', self.n_features)
                assert len(self.dic) < self.max
                self.dic[k] = bof

            self.dic[k].append(j, arr)

            if self.dic[k].is_full():
                # print(f"bof {self.dic[k]} is full")
                self.next_queue.put(self.dic[k])
                del self.dic[k]
                self.condition.notify_all()


class OneBatchOfFields:
    def __init__(self, k, runner):
        self.k = k
        self.runner = runner

        self.j_start = k * self.runner.n_features
        self.j_stop = min(self.runner.shape_j, (k + 1) * self.runner.n_features)
        self.length = self.j_stop - self.j_start

        self.lst = [None] * self.length
        self.count = 0

    def __str__(self):
        return f"Bof({self.k}, {self.j_start}-{self.j_stop}){self.count}/{self.length}"

    def append(self, j, arr):
        assert self.j_start <= j < self.j_stop, (j, self.j_start, self.j_stop)
        assert self.count <= self.length

        relative_j = j % self.runner.n_features

        assert self.lst[relative_j] is None, (j, relative_j)

        self.lst[relative_j] = (j, arr)
        self.count += 1

    def is_full(self):
        return self.count == self.length

    def execute(self):
        # print(f'->building blocks for {self.j_start}-{self.j_stop}')
        range_i = range(0, self.runner.shape_i, self.runner.n_gridpoints)
        for i in range_i:  # each batch of grid points
            i_last = min(i + self.runner.n_gridpoints, self.runner.shape_i)

            b = Block(
                slice(i, i_last),
                slice(self.j_start, self.j_stop),
                [arr[i:i_last] for b, arr in self.lst],
                self.runner,
            )
            self.runner.block_queue.put(b)
            # self.pbar = tqdm.tqdm( total=self.size, desc=f"Reading {self.j_slice.start}-{self.j_slice.stop}", smoothing=0.0, unit_scale=True, leave=False,)
            # self.pbar.get_lock()


class Block:
    def __init__(self, i_slice, j_slice, array_list, runner):
        self.i_slice = i_slice
        self.j_slice = j_slice
        self.array_list = array_list
        self.runner = runner

    def execute(self, file_handle):
        # print(f"writing block fields={self.j_slice}, gridpoints={self.i_slice}")
        arr = np.array(self.array_list).T
        # arr = arr.copy() # because .T makes a view.

        assert len(arr.shape) == 2, arr.shape

        for i in range(self.i_slice.start, self.i_slice.stop):
            i_relative = i - self.i_slice.start

            seek = i * self.runner.shape_i + self.j_slice.start
            bit_seek = seek * self.runner.itemsize
            # assert bit_seek % 4096 == 0, (bit_seek, seek, i)
            file_handle.seek(bit_seek)

            a = arr[i_relative, :]
            # print(f" . writing {i}({len(a)} values) on {seek}-{seek+a.shape[0]}  ... {i}*{self.runner.shape_i}+{self.j_slice.start}")
            file_handle.write(a.tobytes())
        self.runner.write_pbar.update(math.prod(arr.shape))

    def __str__(self):
        return f"({self.j_slice.start}-{self.j_slice.stop}/{self.i_slice.start}-{self.i_slice.stop})"


class FakeField:
    def __init__(self, value, shape):
        self.value = value
        if not isinstance(shape, (tuple, list)):
            shape = (shape,)
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
        nthreads_write=16,
        nthreads_read=2,
        n_gridpoints=512,
        n_features=2048,
    ):
        # threads, n_features, ETA
        # 1      , 1024  , 2h30
        print(f"Reading from {len(source)} fields")
        print(f"nthreads_write={nthreads_write}")
        print(f"nthreads_read={nthreads_read}")
        print(f"n_gridpoints={n_gridpoints}")
        print(f"n_features={n_features}")

        if filename is None:
            filename = source.path_ts
        assert isinstance(filename, str), filename

        self.itemsize = np.dtype(self.dtype).itemsize

        self.nthreads_write = nthreads_write
        self.nthreads_read = nthreads_read
        self.nthreads_ready = 1
        self.n_gridpoints = n_gridpoints
        self.n_features = n_features

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
        print(f"Total shape = {self.shape[0]} x {self.shape[1]} = {self.shape[0]*self.shape[1]}")

        n_expected_fields = math.prod([len(v) for k, v in self.coords_j.items()])
        if n_expected_fields != len(self.source):
            raise ValueError(f"Expecting {n_expected_fields} fields but got {len(self.source)}.")

    def infer_shape_i(self):
        return math.prod(self.read_one_field(0).to_numpy().shape)

    def read_one_field(self, j):
        return self.source[j]

    def run(self):
        self.field_queue = queue.Queue()
        self.ready_batch_of_fields_queue = queue.Queue(1)
        self.block_queue = queue.Queue(10)
        # (self.shape_i // self.n_gridpoints) * 2 + 2)

        self.read_pbar = tqdm.tqdm(
            total=math.prod(self.shape),
            desc="values (read) ",
            smoothing=0.1,
            unit_scale=True,
        )
        self.write_pbar = tqdm.tqdm(
            total=math.prod(self.shape),
            desc="values (write)",
            smoothing=0.4,
            unit_scale=True,
        )
        # Workaround on pbar race condition
        self.read_pbar.get_lock()
        self.write_pbar.get_lock()

        for i in range(0, self.nthreads_read):
            threading.Thread(target=worker(self.field_queue), daemon=True).start()

        for i in range(0, self.nthreads_write):
            threading.Thread(target=worker_on_file(self.block_queue, self.filename), daemon=True).start()

        for i in range(0, self.nthreads_ready):
            threading.Thread(target=worker(self.ready_batch_of_fields_queue), daemon=True).start()

        all_bofs = AllBatchesOfFields(
            self.ready_batch_of_fields_queue,
            max=1,
            n_features=self.n_features,
            runner=self,
        )

        range_j = range(0, self.shape_j, self.n_features)
        for j_start in range_j:  # each batch of fields
            j_stop = min(j_start + self.n_features, self.shape_j)

            for j in range(j_start, j_stop):  # each field
                task = ReadField(j, self, batches_of_fields=all_bofs)
                self.field_queue.put(task)

        for i in range(0, self.nthreads_read):
            self.field_queue.put(None)
        self.field_queue.join()

        for i in range(0, self.nthreads_ready):
            self.ready_batch_of_fields_queue.put(None)
        self.ready_batch_of_fields_queue.join()

        for i in range(0, self.nthreads_write):
            self.block_queue.put(None)
        self.block_queue.join()

        print(f"Wrote data {self.filename}")

        self.write_metadata()

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
        print("**********************")
        self.filename = filename

        with open(self.metadata_filename) as f:
            metadata = json.loads(f.read())

        self.dtype = metadata["dtype"]
        self.coords = metadata["coords"]
        self.map_coords = metadata["map_coords"]

        self.all_coords = {}
        for k, v in self.map_coords.items():
            self.all_coords[k] = v
        for k, v in self.coords.items():
            self.all_coords[k] = v
        self.shape = tuple([len(v) for k, v in self.all_coords.items()])

        print(
            f"Reading file {self.filename}, expecting {self.shape} = {math.prod(self.shape) * np.dtype(self.dtype).itemsize} bytes"
        )
        self.array = np.memmap(self.filename, dtype=np.dtype(self.dtype), mode="r", shape=self.shape)

    def to_xarray(self):
        import xarray as xr

        print("all coords keys", [(k, len(v)) for k, v in self.all_coords.items()])
        dims = list(self.all_coords.keys())
        return xr.DataArray(data=self.array, dims=dims, coords=self.all_coords)

    def to_pandas(self):
        raise NotImplementedError()


# class HdfTimeseries(TimeseriesWriter):
#     @property
#     def array(self):
#         if self._array:
#             return self._array
#         import h5py
#
#         f = h5py.File(self.filename, "w")  # , driver='core')
#         self._array = f.create_dataset("data", self.shape, dtype=self.dtype)
#         return self.array
#
#
# class HdfTimeseriesWriter(HdfTimeseries, TimeseriesWriter):
#     pass
#
#
# class HdfTimeseriesReader(HdfTimeseries, TimeseriesReader):
#     pass

WritterClass = TimeseriesWriter


def test1():
    source = FakeSource(5, shape=(10,))
    t = WritterClass(
        source,
        filename="transpose.1.bin",
        n_gridpoints=5,
        n_features=3,
        nthreads_read=1,
        nthreads_write=1,
    )
    t.run()
    r = TimeseriesReader(filename="transpose.1.bin")
    xds = r.to_xarray()


def test2():
    source = FakeSource(18, shape=(24))
    t = WritterClass(source, filename="transpose.2.bin", n_gridpoints=200, n_features=10)
    t.run()
    r = TimeseriesReader(filename="transpose.2.bin")
    xds = r.to_xarray()


def test3():
    source = FakeSource(6, shape=(24, 36))
    t = WritterClass(source, filename="transpose.3.bin", n_gridpoints=200, n_features=4)
    t.run()
    r = TimeseriesReader(filename="transpose.3.bin")
    xds = r.to_xarray()
    # print(xds)


def test4():
    source = FakeSource(6, 5, shape=(24, 36))
    t = WritterClass(source, filename="transpose.4.bin", n_gridpoints=200, n_features=50)
    t.run()
    r = TimeseriesReader(filename="transpose.4.bin")
    xds = r.to_xarray()


def ecpoint_full_write():
    data = cml.load_dataset("ecpoint-test", "full")
    t = WritterClass(data)
    t.run()


def ecpoint_full_read():
    data = cml.load_dataset("ecpoint-test", "full")
    r = TimeseriesReader(data.path_ts)
    xds = r.to_xarray()
    print(xds)


def test5_write(subset):
    data = cml.load_dataset("ecpoint-test", subset)
    t = WritterClass(data)
    t.run()


def test5_read(subset):
    data = cml.load_dataset("ecpoint-test", subset)
    r = TimeseriesReader(data.path_ts)
    xds = r.to_xarray()
    print(xds)


# write in auxiliary file when writers has finished
# to parallelise and to help reading

# split grib key for filename and in matrix coordinate (lat/lon/values always outer loop)

# check size are uniform
# with grib.get("md5GridSection")


if __name__ == "__main__":
    # print("- TEST 1 -")
    # test1()

    # print("- TEST 2 -")
    # test2()

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
    # ETA with Refactored with queues: ETA~30min. Real: 1h30 (threads_write=8,nthreads_read=2,n_gridpoints=512,n_features=1024)
    # test5_read("large")

    # print("- TEST 5 - per year")
    # for i in range(2000, 2019):
    #    print("year ", i)
    #    data = cml.load_dataset("ecpoint-test",i)
    #    print(len(data), "fields")
    #    t = WritterClass(data)
    #    t.run()

    print("- TEST 5 - step")
    steps = cml.load_dataset("ecpoint-test", "full").coords["step"]
    step = steps[int(sys.argv[1])]
    print(f"Running step {step} ({sys.argv[1]}/{len(steps)})")
    data = cml.load_dataset("ecpoint-test", f"step_{step}")
    print(len(data), "fields")
    t = WritterClass(data)
    t.run()

    # print("- TEST ECPOINT -")
    # ecpoint_full_write()
    # ETA with TimeSeries: 9k min (450k / 512 * 10min)
    # ETA with TimeSeries2: 12k min (540k/8k * 240min)
    # ETA with Refactored with queues: 24h
    # ecpoint_full_read()

# test2()
# test3()
