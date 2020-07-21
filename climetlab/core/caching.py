# import os
# import tempfile
import hashlib
from .settings import SETTINGS


def update(m, x):
    if isinstance(x, (list, tuple)):
        for y in x:
            update(m, y)
        return

    if isinstance(x, dict):
        for k, v in sorted(x.items()):
            update(m, k)
            update(m, v)
        return

    m.update(str(x).encode('utf-8'))


def temp_file(*args):
    m = hashlib.sha256()
    update(m, args)
    # fd, path = tempfile.mkstemp()
    # os.close(fd)
    return "%s/climetlab.%s" % (SETTINGS['cache_directory'], m.hexdigest(),)
