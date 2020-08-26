# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

import os
import sys

from climetlab.data import load as load_data
from climetlab.core.caching import temp_file

# Examples
# https://github.com/ecmwf/notebook-examples/tree/master/visualisation

from Magics import macro

try:
    from IPython.display import Image, SVG
except Exception:

    def Image(x):
        return x

    def SVG(x):
        return x


class Driver:
    def __init__(self, width=680, grid=False, **kwargs):
        self._projection = None
        self._data = None
        self._format = "png"
        self._width_cm = 10
        self._height_cm = 10
        self._width = width
        self._page_ratio = 1.0
        self._contour = macro.mcont(contour_automatic_setting="ecmwf", legend="off",)

        self._grid = grid
        self._background = macro.mcoast(
            map_grid=self._grid,
            map_grid_colour="tan",
            map_label="off",
            map_boundaries="on",
            map_coastline_land_shade="on",
            map_coastline_land_shade_colour="cream",
            map_coastline_colour="tan",
            map_grid_frame=True,
            map_grid_frame_thickness=5,
        )

        self._foreground = macro.mcoast(
            map_grid=self._grid,
            map_label="off",
            map_grid_frame=True,
            map_grid_frame_thickness=5,
        )

        self._legend = None
        self._title = None

        self.kwargs = dict(**kwargs)

        self.bounding_box(90, -180, -90, 180)
        self._tmp = []

    def temp_file(self, extension=".tmp"):
        self._tmp.append(temp_file(extension))
        return self._tmp[-1].path

    def bounding_box(self, north, west, south, east):
        assert north > south, "North (%s) must be greater than south (%s)" % (
            north,
            south,
        )
        assert west != east

        self._projection = macro.mmap(
            subpage_upper_right_longitude=float(east),
            subpage_upper_right_latitude=float(north),
            subpage_lower_left_latitude=float(south),
            subpage_lower_left_longitude=float(west),
            subpage_map_projection="cylindrical",
        )
        self._page_ratio = (north - south) / (east - west)

    def plot_grib(self, path, offset):
        self._data = macro.mgrib(
            grib_input_file_name=path,
            grib_file_address_mode="byte_offset",
            grib_field_position=int(offset),
        )

    def plot_netcdf(self, params):
        self._data = macro.mnetcdf(**params)

    def plot_numpy(
        self, data, north, west, south_north_increment, west_east_increment, metadata
    ):
        self._data = macro.minput(
            input_field=data,
            input_field_initial_latitude=float(north),
            input_field_latitude_step=-float(south_north_increment),
            input_field_initial_longitude=float(west),
            input_field_longitude_step=float(west_east_increment),
            input_metadata=metadata,
        )

    def plot_xarray(self, ds, variable, dimension_settings={}):
        tmp = self.temp_file(".nc")
        ds.to_netcdf(tmp)

        dimensions = []
        for k, v in dimension_settings.items():
            dimensions.append("%s:%s" % (k, v))

        if dimensions:
            self.plot_netcdf(
                dict(
                    netcdf_filename=tmp,
                    netcdf_value_variable=variable,
                    netcdf_dimension_setting=dimensions,
                    netcdf_dimension_setting_method="index",
                )
            )
        else:
            self.plot_netcdf(
                dict(
                    netcdf_filename=tmp,
                    netcdf_value_variable=variable,
                    # netcdf_dimension_setting=dimensions,
                    # netcdf_dimension_setting_method="index",
                )
            )
        # self._data = macro.mxarray(
        #     xarray_dataset=ds,
        #     xarray_variable_name=variable,
        #     xarray_dimension_settings=dimension_settings,
        # )

    def plot_csv(self, path, variable):
        self._data = macro.mtable(
            table_filename=path,
            table_latitude_variable="1",
            table_longitude_variable="2",
            table_value_variable="3",
            table_header_row=0,
            table_variable_identifier_type="index",
        )
        self.style("red-markers")

    def plot_pandas(self, frame, lat, lon, variable):
        tmp = self.temp_file(".csv")
        frame[[lat, lon, variable]].to_csv(tmp, header=False, index=False)
        self.plot_csv(tmp, variable)

    def apply_kwargs(self, kwargs):

        if "style" in kwargs:
            self.style(kwargs.pop("style"))

        if "projection" in kwargs:
            self.projection(kwargs.pop("projection"))

        for n in ("width", "grid", "title"):
            kwargs.pop(n, None)

        if kwargs:
            print("magics.apply_kwargs ignoring", kwargs, file=sys.stderr)

    def _apply(self, collection, value, action, default_attribute=None):

        if value is None:
            return None

        if isinstance(value, dict):
            return action(value)

        if isinstance(value, str):

            data = load_data(collection, value, fail=default_attribute is None)
            if data is None:
                return action({default_attribute: value})

            magics = data["magics"]
            actions = list(magics.keys())
            assert len(actions) == 1, actions

            action = getattr(macro, actions[0])
            return action(magics[actions[0]])

        assert False, (collection, value)

    def projection(self, projection):
        self._projection = self._apply(
            "projections", projection, macro.mmap, "subpage_map_projection"
        )

    def style(self, style):
        self._contour = self._apply("styles", style, macro.mcont)

    def plot_values(self, latitudes, longitudes, values, metadata={}):
        self._data = macro.minput(
            input_type="geographical",
            input_values=list(values),
            input_latitudes_list=list(latitudes),
            input_longitudes_list=list(longitudes),
            input_metadata=metadata,
        )

    def show(
        self, path=None, width=None, title=None, format=None, frame=False, **kwargs
    ):

        if format:
            self._format = format

        if "projection" in self.kwargs:
            self.projection(self.kwargs["projection"])

        if "style" in self.kwargs:
            self.style(self.kwargs["style"])

        if path is None:
            path = self.temp_file("." + self._format)

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
        output = macro.output(
            output_formats=[fmt[1:]],
            output_name_first_page_number="off",
            page_x_length=float(self._width_cm),
            page_y_length=float(self._height_cm) * self._page_ratio,
            super_page_x_length=float(self._width_cm),
            super_page_y_length=float(self._height_cm) * self._page_ratio
            + _title_height_cm,
            subpage_x_length=float(self._width_cm),
            subpage_y_length=float(self._height_cm) * self._page_ratio,
            subpage_x_position=0.0,
            subpage_y_position=0.0,
            output_width=self._width if width is None else width,
            page_frame=frame,
            page_id_line="off",
            output_name=base,
        )

        args = [
            x
            for x in (
                output,
                self._projection,
                self._background,
                self._data,
                self._contour,
                self._foreground,
                self._legend,
                self._title,
            )
            if x is not None
        ]

        try:
            macro.plot(*args)
        except Exception:
            print(args)
            raise

        if self._format == "svg":
            Display = SVG
        else:
            Display = Image

        return Display(path, metadata=dict(width=width))
