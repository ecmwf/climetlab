# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import os
from collections import defaultdict
from functools import partial

from climetlab.core.data import data_entries, get_data_entry
from climetlab.core.ipython import Image, display
from climetlab.core.settings import SETTINGS
from climetlab.core.temporary import temp_file
from climetlab.wrappers import get_wrapper

from .options import Options

LOG = logging.getLogger(__name__)

OPTIONS = {}


def magics(*args, **kwargs):
    from .backends.magics.backend import Backend as MagicsBackend

    return MagicsBackend(*args, **kwargs)


def options(**kwargs):
    global OPTIONS
    OPTIONS = kwargs


def projection(name):
    return get_data_entry("projections", name)


def layer(name):
    return get_data_entry("layers", name)


def style(name):
    return get_data_entry("styles", name)


def projections():
    return sorted(e.name for e in data_entries("projections"))


def layers():
    return sorted(e.name for e in data_entries("layers"))


def styles():
    return sorted(e.name for e in data_entries("styles"))


class Plot:
    """[summary]"""

    def __init__(self, kwargs):
        if "backend" in kwargs:
            backend = kwargs.pop("backend")
            LOG.warning(f"Ignoring argument backend='{backend}'")
        backend = magics

        options = {}
        options.update(SETTINGS.get("plotting-options", {}))
        options.update(OPTIONS)
        options.update(kwargs)
        self.backend = backend(Options(options))

    def plot_map(self, data=None, metadata=None, **kwargs):
        if not isinstance(data, (list, tuple)):
            data = [data]

        if metadata:
            self.backend._options.push("metadata", metadata)

        for d in data:
            d = get_wrapper(d)
            d.plot_map(self.backend)

        options = Options(kwargs)
        self.backend.apply_options(options)
        options.check_unused()

        return self

    def wms_layers(self):
        return self.backend.wms_layers()

    def render(self):
        return self.backend.render()

    def show(self):
        self.backend.show(display=display)

    def macro(self) -> list:
        return self.backend.macro()

    def save(self, path):
        return self.backend.save(path)


def files_to_apng(files, path, fps):
    import imageio

    try:
        from numpngw import write_apng
    except ImportError:
        raise RuntimeError(
            "Package numpngw is required to save animated PNGs (pip install numpngw)"
        )

    frames = [imageio.imread(f) for f in files]

    write_apng(path, frames, delay=int(1000.0 / fps + 0.5))

    return path


def files_to_gif(files, path, fps):
    import imageio

    with imageio.get_writer(path, mode="I", duration=1.0 / fps) as writer:
        for filename in files:
            image = imageio.imread(filename)
            writer.append_data(image)

    return path


def files_to_opencv(files, path, fps, cccc):
    try:
        import cv2
    except ImportError:
        raise RuntimeError(
            "Package OpenCV is required to save movies (pip install opencv-python)"
        )

    frame = cv2.imread(files[0])
    height, width, _ = frame.shape

    video = cv2.VideoWriter(
        path,
        cv2.VideoWriter_fourcc(*cccc),
        fps,
        (width, height),
    )

    for image in files:
        video.write(cv2.imread(image))

    cv2.destroyAllWindows()
    video.release()


CODECS = {
    ".gif": files_to_gif,
    ".png": files_to_apng,
    ".avi": partial(files_to_opencv, cccc="XVID"),
    ".mp4": partial(files_to_opencv, cccc="mp4v"),
    ".wmv": partial(files_to_opencv, cccc="WMV2"),
    ".mov": partial(files_to_opencv, cccc="mp4v"),
}


def unsupported(files, path, fps):
    raise NotImplementedError(
        f"Unsupported format for '{path}'."
        f" Supported formats are {list(CODECS.keys())}"
    )


def files_to_movie(files, path, fps):
    _, ext = os.path.splitext(path)

    return CODECS.get(ext, unsupported)(files, path, fps)


class MapPlot(Plot):
    pass


class AnimationPlot:
    def __init__(self, fps=5, **kwargs):
        self.fps = fps
        self.kwargs = kwargs
        self.files = []

    def plot_map(self, data, **kwargs):
        self.files.append(temp_file(".png"))

        forward_kwargs = {}
        for forward in ("row", "column"):
            if forward in kwargs:
                forward_kwargs[forward] = kwargs.pop(forward)

        options = {}
        options.update(self.kwargs)
        options.update(kwargs)

        p = new_plot(**options)
        p.plot_map(data, **forward_kwargs)
        p.save(self.files[-1].path)

    def show(self):
        tmp = temp_file(".png")
        self.save(tmp.path)
        return display(Image(tmp.path))

    def save(self, path):
        return files_to_movie([f.path for f in self.files], path, self.fps)


class LayoutPlot:
    def __init__(self, rows, columns, animate=False, fps=5, **kwargs):
        self.rows = rows
        self.columns = columns
        self.padding = kwargs.pop("padding", 0)
        self.kwargs = kwargs
        self.files = defaultdict(dict)
        self.animate = animate
        self.fps = fps

    def plot_map(self, data, row, column, step=None, **kwargs):
        tmp = temp_file(".png")

        assert row >= 0 and row < self.rows, (row, self.rows)
        assert column >= 0 and column < self.columns, (column, self.columns)

        self.files[step][(row, column)] = tmp

        options = {}
        options.update(self.kwargs)
        options.update(kwargs)

        p = new_plot(**options)
        p.plot_map(data)
        p.save(tmp.path)

    def show(self):
        tmp = temp_file(".png")
        self.save(tmp.path)
        return display(Image(tmp.path))

    def save(self, path):
        if self.animate:
            files = []
            for step in sorted(self.files.keys()):
                files.append(temp_file(".png"))
                self.render(step, files[-1].path)

            files_to_movie([f.path for f in files], path, self.fps)

        else:
            self.render(None, path)

        return path

    def render(self, step, path):
        try:
            import imageio
        except ImportError:
            raise RuntimeError(
                "Package imageio is required to create animations (pip install imageio)"
            )
        import numpy as np

        WHITE = {1: 255}

        cells = {k: imageio.imread(v.path) for k, v in self.files[step].items()}
        first = cells[list(cells.keys())[0]]
        heigth, width, depth = first.shape

        image = (
            np.ones(
                (
                    heigth * self.rows + self.padding * (self.rows - 1),
                    width * self.columns + self.padding * (self.columns - 1),
                    depth,
                ),
                dtype=first.dtype,
            )
            * WHITE[first.dtype.itemsize]
        )

        for row in range(self.rows):
            for col in range(self.columns):
                cell = (row, col)
                if cell in cells:
                    row_padding = self.padding * row
                    col_padding = self.padding * col
                    image[
                        heigth * row + row_padding : heigth * (row + 1) + row_padding,
                        width * col + col_padding : width * (col + 1) + col_padding,
                        :,
                    ] = cells[cell]

        imageio.imwrite(path, image)

        return path


def new_plot(**kwargs) -> Plot:
    """[summary]

    :return: [description]
    :rtype: Plot
    """

    if "rows" in kwargs and "columns" in kwargs:
        return LayoutPlot(**kwargs)

    if kwargs.pop("animate", False):
        return AnimationPlot(**kwargs)

    return MapPlot(kwargs)


def plot_map(data=None, **kwargs):
    """Plot any data on a map.

    Args:
        data ([any]): [description]
    """

    p = new_plot(**kwargs)
    p.plot_map(data)
    p.show()


Plot.plot_map.__doc__ = plot_map.__doc__


def interactive_map(data=None, **kwargs):
    from climetlab.plotting.wms import interactive_map as wms_map

    return wms_map(data, **kwargs)


def new_table(*args, **kwargs):
    from climetlab.notebook.table import Table

    return Table(*args, **kwargs)
