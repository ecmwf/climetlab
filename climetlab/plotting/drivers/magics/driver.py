# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

import yaml

from climetlab.core.caching import temp_file
from climetlab.core.ipython import SVG, Image
from climetlab.core.metadata import annotation
from climetlab.utils.bbox import BoundingBox

from .actions import mcoast, mgrib, minput, mmap, mnetcdf, mtable, mtext, output, plot
from .apply import apply

LOG = logging.getLogger(__name__)


class Layer:
    def __init__(self, data):
        self._data = data
        self._style = data.default_style

    def add_action(self, actions):
        if self._data:
            actions.append(self._data)
        if self._style:
            actions.append(self._style)

    def style(self, style):
        self._style = style

    def update(self, action, value):
        return self._style.update(action, value)


class WMSLayer:
    def __init__(self, actions, bounding_box, temp_files):
        self.actions = actions
        self.bounding_box = bounding_box
        self.temp_files = temp_files


class Driver:
    """TODO: Docscting"""

    def __init__(self, options):

        self._options = options

        self._projection = None
        self._background = None
        self._foreground = None

        self._layers = []
        self._width_cm = 10.0
        self._height_cm = 10.0
        self._page_ratio = 1.0

        self.background(True)
        self.foreground(True)

        self._grid = None
        self._rivers = None
        self._cities = None
        self._borders = None

        self._legend = None
        self._title = None

        self._bounding_box = None
        self._tmp = []

    def temporary_file(self, extension: str = ".tmp") -> str:
        """Return a temporary file name that will be deleted once the plot is produced.

        :param extension: File name extension, defaults to ".tmp"
        :type extension: str, optional
        :return: Temporary file name.
        :rtype: str
        """

        if self._options("dump_yaml", False):
            return temp_file(extension).path

        self._tmp.append(temp_file(extension))
        return self._tmp[-1].path

    def bounding_box(self, north: float, west: float, south: float, east: float):

        bbox = BoundingBox(north=north, west=west, south=south, east=east)
        if self._bounding_box is None:
            self._bounding_box = bbox
        else:
            self._bounding_box = self._bounding_box.merge(bbox)

    def _push_layer(self, data):
        self._layers.append(Layer(data))

    def plot_grib(self, path: str, offset: int):

        self._push_layer(
            mgrib(
                grib_input_file_name=path,
                grib_file_address_mode="byte_offset",
                grib_field_position=int(offset),
            )
        )

    def plot_netcdf(self, path: str, variable: str, dimensions: dict = None):

        if dimensions is None:
            dimensions = {}

        dimension_setting = ["%s:%s" % (k, v) for k, v in dimensions.items()]

        if dimension_setting:
            params = dict(
                netcdf_filename=path,
                netcdf_value_variable=variable,
                netcdf_dimension_setting=dimension_setting,
                netcdf_dimension_setting_method="index",
            )
        else:
            params = dict(netcdf_filename=path, netcdf_value_variable=variable)

        self._push_layer(mnetcdf(**params))

    def plot_numpy(
        self,
        data,
        metadata: dict = None,
    ):
        if metadata is None:
            metadata = {}

        # TODO: issue warnings
        north = metadata.get("north", 90)
        west = metadata.get("west", 0)
        south_north_increment = metadata.get("south_north_increment")
        west_east_increment = metadata.get("west_east_increment")

        if south_north_increment is None:
            south_north_increment = (north - metadata.get("south", -90)) / (
                data.shape[-2] - 1
            )

        if west_east_increment is None:
            west_east_increment = (metadata.get("east", 360) - west) / (
                data.shape[-1] - 1
            )

        # TODO: remove me when Magics supports full json
        def tidy(x):
            r = {}
            for k, v in x.items():
                if v is None or isinstance(v, (int, float, str, bool)):
                    r[k] = v
            return r

        self._push_layer(
            minput(
                input_field=data,
                input_field_initial_latitude=float(north),
                input_field_latitude_step=-float(south_north_increment),
                input_field_initial_longitude=float(west),
                input_field_longitude_step=float(west_east_increment),
                input_metadata=tidy(metadata),
            )
        )

    def plot_xarray(self, ds, variable: str, dimensions: dict = None):
        tmp = self.temporary_file(".nc")
        field = ds[variable].isel({} if dimensions is None else dimensions)
        field.to_netcdf(tmp)
        self.plot_netcdf(tmp, variable, {} if dimensions is None else dimensions)

    def plot_csv(self, path: str, variable: str):
        self._push_layer(
            mtable(
                table_filename=path,
                table_latitude_variable="1",
                table_longitude_variable="2",
                table_value_variable="3",
                table_header_row=0,
                table_variable_identifier_type="index",
            )
        )
        self.style("default-style-observations")

    def plot_pandas(self, frame, latitude: str, longitude: str, variable: str):
        tmp = self.temporary_file(".csv")
        frame[[latitude, longitude, variable]].to_csv(tmp, header=False, index=False)
        self.plot_csv(tmp, variable)

        style = annotation(frame).get("style")
        if style is not None:
            self.style(style)

    def background(self, background):
        self._background = apply(
            value=background,
            collection="layers",
            target=self._background,
            default="default-background",
            options=self._options,
        )

    def foreground(self, foreground):
        self._foreground = apply(
            value=foreground,
            collection="layers",
            target=self._foreground,
            default="default-foreground",
            options=self._options,
        )

    def projection(self, projection):
        self._projection = apply(
            value=projection,
            collection="projections",
            target=self._projection,
            default=None,
            options=self._options,
        )

    def style(self, style):
        if len(self._layers) > 0:
            last_layer = self._layers[-1]
            last_layer.style(
                apply(
                    value=style,
                    target=last_layer,
                    collection="styles",
                    default=None,
                    options=self._options,
                )
            )
        else:
            raise Exception("No current data layer: cannot set style '%r'" % (style,))

    def apply_options(self, options):
        if options.provided("style"):
            self.style(options["style"])

        if options.provided("bounding_box"):
            bbox = options["bounding_box"]
            if isinstance(bbox, (list, tuple)):
                self.bounding_box(
                    north=bbox[0], west=bbox[1], south=bbox[2], east=bbox[3]
                )
            else:
                self.bounding_box(
                    north=bbox.north, west=bbox.west, south=bbox.south, east=bbox.east
                )

    def option(self, name, default=None):
        return self._options(name, default)

    def finalise(self):
        self.apply_options(self._options)

        if self._options.provided("background"):
            self.background(self._options["background"])

        if self._options.provided("foreground"):
            self.foreground(self._options["foreground"])

        if self._options.provided("projection"):
            self.projection(self._options["projection"])

        if self._options("grid", False):
            self._grid = mcoast(map_grid=True, map_coastline=False)

        if self._options("borders", False):
            self._borders = mcoast(
                map_boundaries=True,
                map_grid=False,
                map_coastline=False,
                map_label=False,
            )

        if self._options("rivers", False):
            self._rivers = mcoast(
                map_rivers=True, map_grid=False, map_coastline=False, map_label=False
            )

        if self._options("cities", False):
            self._cities = mcoast(
                map_cities=True, map_label=False, map_grid=False, map_coastline=False
            )

    def show(self):
        width = self._options("width", 680)

        path = self._options(
            "path", self.temporary_file("." + self._options("format", "png"))
        )

        self.save(path)

        if path.endswith(".svg"):
            Display = SVG  # noqa: N806
        elif path.endswith(".pdf"):
            return path
        else:
            Display = Image  # noqa: N806

        return Display(path, metadata=dict(width=width))

    def save(self, path):  # noqa C901

        self.finalise()

        title = self._options("title", None)
        width = self._options("width", 680)
        frame = self._options("frame", False)

        self._width_cm = self._options("width_cm", 10)
        self._height_cm = self._options("height_cm", 10)

        if self._projection is None:
            # TODO: select best projection based on bbox
            self._projection = mmap(subpage_map_projection="cylindrical")

        if self._bounding_box is not None:
            bbox = self._bounding_box.add_margins(self._options("margins", 0))
            self._projection = apply(
                value={
                    "=subpage_upper_right_longitude": bbox.east,
                    "=subpage_upper_right_latitude": bbox.north,
                    "=subpage_lower_left_latitude": bbox.south,
                    "=subpage_lower_left_longitude": bbox.west,
                },
                target=self._projection,
                action=mmap,
                default=None,
                options=self._options,
            )

        self._page_ratio = self._projection.page_ratio()
        if self._page_ratio <= 0:
            self._page_ratio = 1.0

        _title_height_cm = 0
        if title:
            _title_height_cm = 0.7
            if title is True:
                # Automatic title
                self._title = mtext()
            else:
                self._title = mtext(
                    text_lines=[str(title)],
                    # text_justification='center',
                    # text_font_size=0.6,
                    # text_mode="positional",
                    # text_box_x_position=5.00,
                    # text_box_y_position=18.50,
                    # text_colour='charcoal'
                )

        page = output(
            output_file=path,
            page_x_length=self._width_cm,
            page_y_length=self._height_cm * self._page_ratio,
            super_page_x_length=self._width_cm,
            super_page_y_length=self._height_cm * self._page_ratio + _title_height_cm,
            subpage_x_length=self._width_cm,
            subpage_y_length=self._height_cm * self._page_ratio,
            subpage_x_position=0.0,
            subpage_y_position=0.0,
            output_width=width,
            page_frame=frame,
            super_page_frame=False,
            subpage_frame=False,
            page_id_line=False,
        )

        # TODO
        self._options("update", False)
        self._options("update_foreground", False)

        args = [page] + self.macro()

        dump = self._options("dump_python", False)
        if dump:
            m = "from Magics import macro\nmacro.plot({})".format(args)
            if isinstance(dump, str):
                with open(dump, "w") as f:
                    print(m, file=f)
            else:
                print(m)

        dump = self._options("dump_yaml", False)
        if dump:
            if isinstance(dump, str):
                with open(dump, "w") as f:
                    print(
                        yaml.dump(
                            dict(plot=[a.to_yaml() for a in args]),
                            default_flow_style=False,
                        ),
                        file=f,
                    )
            else:
                print(
                    yaml.dump(
                        dict(plot=[a.to_yaml() for a in args]), default_flow_style=False
                    )
                )

        self._options.check_unused()

        try:
            plot(*args)
        except Exception:
            LOG.error("Error executing: %r", args, exc_info=True)
            raise

        return self._bounding_box

    def macro(self):
        """[summary]

        :return: A list of plotting directives
        :rtype: list
        """
        m = [self._projection, self._background]
        for r in self._layers:
            r.add_action(m)
        m += [
            self._rivers,
            self._borders,
            self._cities,
            self._foreground,
            self._grid,
            self._legend,
            self._title,
        ]
        return [x for x in m if x is not None]

    def wms_layers(self):

        self.finalise()

        m = [self._background]
        for r in self._layers:
            r.add_action(m)
        m += [
            self._rivers,
            self._borders,
            self._cities,
            self._foreground,
            self._grid,
        ]

        actions = [x for x in m if x is not None]
        return WMSLayer(actions, self._bounding_box, self._tmp)
