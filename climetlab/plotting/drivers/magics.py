# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import logging


# This is needed when running Sphinx on ReadTheDoc

try:
    from Magics import macro
except Exception:
    macro = None


from climetlab.core.caching import temp_file
from climetlab.core.ipython import SVG, Image
from climetlab.core.data import get_data_entry

LOG = logging.getLogger(__name__)


# Examples of Magics macros:
# https://github.com/ecmwf/notebook-examples/tree/master/visualisation

NONE = object()


class Action:

    default_style = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        x = ["macro.%s(" % (self.action,)]
        for k, v in sorted(self.kwargs.items()):
            x.append("\n   %s=%r," % (k, v))
        x.append("\n    )")
        return "".join(x)

    @property
    def action(self):
        return self.__class__.__name__

    def execute(self):
        return getattr(macro, self.action)(**self.kwargs).execute()


class mcont(Action):
    pass


class mcoast(Action):
    pass


class mmap(Action):
    pass


class FieldAction(Action):
    default_style = mcont(contour_automatic_setting="ecmwf", legend=False)


class mgrib(FieldAction):
    pass


class mnetcdf(FieldAction):
    pass


class minput(FieldAction):
    pass


class mtable(Action):
    pass


class mtext(Action):
    pass


class msymb(Action):
    pass


class output(Action):
    pass


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


class Driver:
    """TODO: Docscting
    """

    def __init__(self, options: dict = {}):

        self._options = options
        self._used_options = set()

        self._projection = None
        self._layers = []
        self._width_cm = 10.0
        self._height_cm = 10.0

        self._page_ratio = 1.0

        self._background = mcoast(
            map_grid=False,
            map_grid_colour="tan",
            map_label=False,
            map_boundaries=True,
            map_coastline_land_shade=True,
            map_coastline_land_shade_colour="cream",
            map_coastline_colour="tan",
            map_grid_frame=True,
            map_grid_frame_thickness=5,
        )

        self._foreground = mcoast(
            map_grid=True,
            map_label=False,
            map_grid_frame=True,
            map_grid_frame_thickness=5,
        )

        self._grid = None
        self._rivers = None
        self._cities = None
        self._borders = None

        self._legend = None
        self._title = None

        self.bounding_box(90, -180, -90, 180)
        self._tmp = []

    def temporary_file(self, extension: str = ".tmp") -> str:
        """Return a temporary file name that will be deleted once the plot is produced.abspath

        :param extension: File name extension, defaults to ".tmp"
        :type extension: str, optional
        :return: Temporary file name.
        :rtype: str
        """
        self._tmp.append(temp_file(extension))
        return self._tmp[-1].path

    def bounding_box(self, north: float, west: float, south: float, east: float):

        # Convert to float as these values may come from Numpy
        north = float(north)
        west = float(west)
        south = float(south)
        east = float(east)

        assert north > south, "North (%s) must be greater than south (%s)" % (
            north,
            south,
        )
        assert west != east

        self._projection = mmap(
            subpage_upper_right_longitude=east,
            subpage_upper_right_latitude=north,
            subpage_lower_left_latitude=south,
            subpage_lower_left_longitude=west,
            subpage_map_projection="cylindrical",
        )
        self._page_ratio = (north - south) / (east - west)

    def _push_layer(self, data):
        self._layers.append(Layer(data))

    def plot_grib(self, path: str, offset: int):
        """[summary]

        :param path: [description]
        :type path: [type]
        :param offset: [description]
        :type offset: [type]
        """
        self._push_layer(
            mgrib(
                grib_input_file_name=path,
                grib_file_address_mode="byte_offset",
                grib_field_position=int(offset),
            )
        )

    def plot_netcdf(self, path: str, variable: str, dimensions: dict = {}):
        """[summary]

        :param path: [description]
        :type path: [type]
        :param variable: [description]
        :type variable: [type]
        :param dimensions: [description], defaults to {}
        :type dimensions: dict, optional
        """
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
        north: float,
        west: float,
        south_north_increment: float,
        west_east_increment: float,
        metadata: dict = {},
    ):
        """[summary]

        :param data: [description]
        :type data: [type]
        :param north: [description]
        :type north: [type]
        :param west: [description]
        :type west: [type]
        :param south_north_increment: [description]
        :type south_north_increment: [type]
        :param west_east_increment: [description]
        :type west_east_increment: [type]
        :param metadata: [description]
        :type metadata: [type]
        """
        self._push_layer(
            minput(
                input_field=data,
                input_field_initial_latitude=float(north),
                input_field_latitude_step=-float(south_north_increment),
                input_field_initial_longitude=float(west),
                input_field_longitude_step=float(west_east_increment),
                input_metadata=metadata,
            )
        )

    def plot_xarray(self, ds, variable: str, dimensions: dict = {}):
        """[summary]

        :param ds: [description]
        :type ds: [type]
        :param variable: [description]
        :type variable: [type]
        :param dimensions: [description], defaults to {}
        :type dimensions: dict, optional
        """
        tmp = self.temporary_file(".nc")
        ds.to_netcdf(tmp)
        self.plot_netcdf(tmp, variable, dimensions)

    def plot_csv(self, path: str, variable: str):
        """[summary]

        :param path: [description]
        :type path: [type]
        :param variable: [description]
        :type variable: [type]
        """
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
        """[summary]

        :param frame: [description]
        :type frame: [type]
        :param latitude: [description]
        :type latitude: [type]
        :param longitude: [description]
        :type longitude: [type]
        :param variable: [description]
        :type variable: [type]
        """
        tmp = self.temporary_file(".csv")
        frame[[latitude, longitude, variable]].to_csv(tmp, header=False, index=False)
        self.plot_csv(tmp, variable)

    def _apply(self, collection, value, action):

        if value is None:
            return None

        if isinstance(value, dict):
            return action(**value)

        if isinstance(value, str):

            data = get_data_entry(collection, value).data

            magics = data["magics"]
            actions = list(magics.keys())
            assert len(actions) == 1, actions

            action = globals()[actions[0]]
            return action(**magics[actions[0]])

        assert False, (collection, value)

    def projection(self, projection):
        self._projection = self._apply("projections", projection, mmap)

    def style(self, style):
        if len(self._layers):
            self._layers[-1].style(self._apply("styles", style, mcont))
        else:
            LOG.warning("No current data layer: ignoring style '%r'", style)

    def option(self, name: str, default=NONE):
        self._used_options.add(name)
        if default is NONE:
            return self._options[name]
        else:
            return self._options.get(name, default)

    def apply_options(self, options):
        pass

    def show(self):

        if not self.option("background", True):
            self._background = None

        if not self.option("foreground", True):
            self._foreground = None

        if self.option("style", None):
            self.style(self.option("style"))

        if self.option("projection", None):
            self.projection(self.option("projection"))

        title = self.option("title", None)
        width = self.option("width", 680)
        frame = self.option("frame", False)

        if self.option("grid", False):
            self._grid = mmap(map_grid=True, map_coastline=False)

        if self.option("borders", False):
            self._borders = mmap(
                map_boundaries=True, map_grid=False, map_coastline=False
            )

        if self.option("rivers", False):
            self._rivers = mmap(map_rivers=True, map_grid=False, map_coastline=False)

        if self.option("cities", False):
            self._cities = mmap(map_cities=True, map_grid=False, map_coastline=False)

        path = self.option(
            "path", self.temporary_file("." + self.option("format", "png"))
        )

        _title_height_cm = 0
        if title:
            _title_height_cm = 0.7
            if title is True:
                # Automatic title
                self._title = macro.mtext()
            else:
                self._title = macro.mtext(
                    text_lines=[str(title)],
                    # text_justification='center',
                    # text_font_size=0.6,
                    # text_mode="positional",
                    # text_box_x_position=5.00,
                    # text_box_y_position=18.50,
                    # text_colour='charcoal'
                )

        base, fmt = os.path.splitext(path)
        page = output(
            output_formats=[fmt[1:]],
            output_name_first_page_number=False,
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
            page_id_line=False,
            output_name=base,
        )

        unused = set(self._options.keys()) - self._used_options
        if unused:
            LOG.warning(
                "".join(
                    [
                        "Unused argument%s:" % ("s" if len(unused) > 1 else "",),
                        ", ".join("%s=%s" % (x, self._options[x]) for x in unused),
                    ]
                )
            )

        args = [page] + self.macro()

        # for a in args:
        #     print(a)

        try:
            macro.plot(*args)
        except Exception:
            LOG.error("Error executing: %r", args, exc_info=True)
            raise

        if fmt == ".svg":
            Display = SVG
        else:
            Display = Image

        return Display(path, metadata=dict(width=width))

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
