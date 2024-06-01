import os
import sys
import time

from tqdm import tqdm

from climetlab.utils.humanize import bytes


def unbytes(x):
    if x[-1].lower() == "k":
        return int(x[:-1]) * 1024
    if x[-1].lower() == "m":
        return int(x[:-1]) * 1024 * 1024
    if x[-1].lower() == "g":
        return int(x[:-1]) * 1024 * 1024 * 1024
    return int(x)


# for datavalue in ['a' , 'b', 'c']:
#    print()
class Timer:
    def __init__(self):
        self.start = time.time()
        self.current = self.start

    def __call__(self, msg, mult):
        new = time.time()
        delta = new - self.current
        print(msg, delta, "seconds", f"(Total will be {mult*delta} sec)")
        self.current = new

    @property
    def total(self):
        return time.time() - self.start


class BenchmarkIO:
    LOGDIR = "iologs"

    def __init__(self, filename, seek, chunksize, SIZE):
        self.tic = Timer()
        self.filename = filename
        self.seek = seek
        self.chunksize = chunksize
        self.SIZE = SIZE

    def chunksize_str_hook(self):
        return ""

    def go(self):
        msg = f"{bytes(self.SIZE)} by chunks of {bytes(self.chunksize)} with seeks of {bytes(self.seek)} (i.e. {self.seek/self.chunksize} passes)"  # noqa

        with open(self.filename, self.MODE) as f:
            for i, offset in enumerate(
                tqdm(
                    range(0, self.seek, self.chunksize),
                    desc=f"Offset (chunksize={bytes(self.chunksize)+self.chunksize_str_hook()})",
                    leave=False,
                )
            ):
                for cursor in tqdm(
                    list(range(0, self.SIZE, self.seek)),
                    desc=f"Seek (by {bytes(self.seek)})",
                    leave=False,
                ):
                    f.seek(cursor + offset)
                    assert f.tell() == (cursor + offset)
                    self.process(f)
                    if self.tic.total > 15 * 60:
                        print(f"Too long to write {msg}")
                        return
        print(f"{self.VERB} {msg} in {self.tic.total/60} min.")
        bk.write_log()

    def process(self, f):
        raise NotImplementedError()

    def write_log(self):
        logdir = self.LOGDIR
        os.makedirs(logdir, exist_ok=True)
        with open(f"{logdir}/{self.prefix}io.{self.seek}.{self.chunksize}.csv", "a") as f:
            print(f"{self.seek}, {self.chunksize}, {self.tic.total}", file=f)


class BenchmarkWrite(BenchmarkIO):
    MODE = "wb"
    prefix = ""
    VERB = "Wrote"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        import numpy as np

        self.data = np.random.randn(self.chunksize // 4).astype(np.float32).tobytes()

    def process(self, f):
        assert len(self.data) == self.chunksize
        f.write(self.data)


class BenchmarkRead(BenchmarkIO):
    prefix = "read"
    MODE = "rb"
    VERB = "Read"

    def process(self, f):
        f.read(self.chunksize)


class BenchmarkReadanddrop(BenchmarkIO):
    prefix = "readanddrop"
    MODE = "rb"
    VERB = "Readanddrop"

    def process(self, f):
        data = f.read(self.seek)  # noqa
        # Read the whole see and drop what is useless
        # data = data[self.offset:(self.offset+self.chunksize)]


class BenchmarkReadnTimes(BenchmarkIO):
    MODE = "rb"
    VERB = "Readntimes"

    def __init__(self, *args, times, **kwargs):
        self.times = times
        super().__init__(*args, **kwargs)

    @property
    def prefix(self):
        return f"read{self.times}times"

    def chunksize_str_hook(self):
        return "*" + str(self.times)

    def process(self, f):
        data = f.read(self.chunksize * self.times)  # noqa
        # Read "self.times" more than what is usefull drop what is useless
        # data = data[:self.chunksize]


cls = BenchmarkWrite
options = {}
if len(sys.argv) > 3:
    task = sys.argv[1]
    cls = dict(
        read=BenchmarkRead,
        readn=BenchmarkReadnTimes,
        readanddrop=BenchmarkReadanddrop,
        write=BenchmarkWrite,
    )[task]
if len(sys.argv) > 4:
    options["times"] = int(sys.argv[4])

seek = unbytes(sys.argv[2])
chunksize = unbytes(sys.argv[3])
if seek < chunksize:
    exit()

filename = "binfile"
SIZE = 100 * 1024 * 1024 * 1024
bk = cls(filename, seek, chunksize, SIZE, **options)
bk.go()
