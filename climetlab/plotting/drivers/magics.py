# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# Keep linters happy
# N801 = classes should start with uppercase
# N806 = variables should be lower case

import os
import logging
import yaml
from collections import defaultdict

# This is needed when running Sphinx on ReadTheDoc

try:
    from Magics import macro
except Exception:
    macro = None


from climetlab.core.caching import temp_file
from climetlab.core.ipython import SVG, Image
from climetlab.core.data import get_data_entry
from climetlab.core.metadata import annotation

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

    def update(self, action, values):
        if isinstance(self, action):
            for k, v in values.items():
                if k[0] in ("+",):
                    self.kwargs[k[1:]] = v
                if k[0] in ("-",):
                    self.kwargs.pop(k[1:], None)
            return self
        return None


class mcont(Action):  # noqa: N801
    pass


class mcoast(Action):  # noqa: N801
    pass


class mmap(Action):  # noqa: N801
    pass


class FieldAction(Action):
    default_style = mcont(contour_automatic_setting="ecmwf", legend=False)


class mgrib(FieldAction):  # noqa: N801
    pass


class mnetcdf(FieldAction):  # noqa: N801
    pass


class minput(FieldAction):  # noqa: N801
    pass


class mtable(Action):  # noqa: N801
    pass


class mtext(Action):  # noqa: N801
    pass


class msymb(Action):  # noqa: N801
    pass


class output(Action):  # noqa: N801
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

    def update(self, action, value):
        return self._style.update(action, value)


MAGICS_KEYS = None


def _apply(*, value, collection=None, action=None, default=True, target=None):

    if value is None:
        return None

    if value is False:
        return None

    if value is True:
        assert default is not True
        return _apply(
            value=default,
            collection=collection,
            action=action,
            default=None,
            target=target,
        )

    if isinstance(value, dict):

        if "set" in value or "clear" in value:
            newvalue = {}
            for k, v in value.get("set", {}).items():
                newvalue["+{}".format(k)] = v

            for k in value.get("clear", []):
                newvalue["-{}".format(k)] = None

            return _apply(
                value=newvalue,
                collection=collection,
                action=action,
                default=default,
                target=target,
            )

        if "+" in value or "-" in value:
            newvalue = {}
            for k, v in value.get("+", {}).items():
                newvalue["+{}".format(k)] = v

            for k in value.get("-", []):
                newvalue["-{}".format(k)] = None

            return _apply(
                value=newvalue,
                collection=collection,
                action=action,
                default=default,
                target=target,
            )

        global MAGICS_KEYS

        if MAGICS_KEYS is None:
            MAGICS_KEYS = defaultdict(set)
            with open(os.path.join(os.path.dirname(__file__), "magics.yaml")) as f:
                magics = yaml.load(f, Loader=yaml.SafeLoader)
                for name, params in magics.items():
                    for param in params:
                        MAGICS_KEYS[param].add(name)

        # Guess the best action from the keys
        scores = defaultdict(int)
        special = 0
        for param in value.keys():

            if not param[0].isalpha():
                special += 1
                param = param[1:]

            acts = MAGICS_KEYS.get(param, [])
            if len(acts) == 1:
                # Only consider unambiguous parameters
                scores[list(acts)[0]] += 1

        best = sorted((v, k) for k, v in scores.items())

        if len(best) == 0:
            LOG.warning("Cannot establish Magics action from [%r]", list(value.keys()))

        if len(best) >= 2:
            if best[0][0] == best[1][0]:
                LOG.warning(
                    "Cannot establish Magics action from [%r], it could be %s or %s",
                    list(value.keys()),
                    best[0][1],
                    best[1][1],
                )

        if len(best) > 0:
            action = globals()[best[0][1]]

        if special:
            if special != len(value):
                raise Exception(
                    "Cannot set some attributes and override others %r"
                    % list(value.keys())
                )

            result = target.update(action, value)
            if result is not None:
                return result

            raise Exception(
                "Cannot override attributes %r (no matching style)" % list(value.keys())
            )

        return action(**value)

    if isinstance(value, str):

        # TODO: Consider `value` being a URL (yaml or json)

        data = get_data_entry(collection, value).data

        magics = data["magics"]
        actions = list(magics.keys())
        assert len(actions) == 1, actions

        action = globals()[actions[0]]
        return action(**magics[actions[0]])

    assert False, (collection, value)


class Driver:
    """TODO: Docscting
    """

    def __init__(self, options=None):

        self._options = {} if options is None else options
        self._used_options = set()

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

        self.bounding_box(90, -180, -90, 180)
        self._tmp = []

    def temporary_file(self, extension: str = ".tmp") -> str:
        """Return a temporary file name that will be deleted once the plot is produced.

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
        north: float,
        west: float,
        south_north_increment: float,
        west_east_increment: float,
        metadata: dict = None,
    ):
        if metadata is None:
            metadata = {}

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

    def plot_xarray(self, ds, variable: str, dimensions: dict = None):
        tmp = self.temporary_file(".nc")
        ds.to_netcdf(tmp)
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
        self._background = _apply(
            value=background,
            collection="layers",
            target=self._background,
            default="default-background",
        )

    def foreground(self, foreground):
        self._foreground = _apply(
            value=foreground,
            collection="layers",
            target=self._foreground,
            default="default-foreground",
        )

    def projection(self, projection):
        self._projection = _apply(
            value=projection, collection="projections", target=self._projection
        )

    def style(self, style):
        if len(self._layers) > 0:
            last_layer = self._layers[-1]
            last_layer.style(
                _apply(value=style, target=last_layer, collection="styles")
            )
        else:
            raise Exception("No current data layer: cannot set style '%r'" % (style,))

    def option(self, name: str, default=NONE):
        self._used_options.add(name)
        if default is NONE:
            return self._options[name]

        return self._options.get(name, default)

    def option_provided(self, name: str) -> bool:
        return name in self._options

    def apply_options(self, options):
        pass

    def show(self):

        if self.option_provided("background"):
            self.background(self.option("background"))

        if self.option_provided("foreground"):
            self.foreground(self.option("foreground"))

        if self.option_provided("style"):
            self.style(self.option("style"))

        if self.option_provided("projection"):
            self.projection(self.option("projection"))

        title = self.option("title", None)
        width = self.option("width", 680)
        frame = self.option("frame", False)

        if self.option("grid", False):
            self._grid = mcoast(map_grid=True, map_coastline=False)

        if self.option("borders", False):
            self._borders = mcoast(
                map_boundaries=True,
                map_grid=False,
                map_coastline=False,
                map_label=False,
            )

        if self.option("rivers", False):
            self._rivers = mcoast(
                map_rivers=True, map_grid=False, map_coastline=False, map_label=False
            )

        if self.option("cities", False):
            self._cities = mcoast(
                map_cities=True, map_label=False, map_grid=False, map_coastline=False
            )

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

        # TODO
        self.option("update", False)
        self.option("update_foreground", False)

        unused = set(self._options.keys()) - self._used_options
        if unused:
            raise TypeError(
                "".join(
                    [
                        "Unused argument%s:" % ("s" if len(unused) > 1 else "",),
                        ", ".join("%s=%s" % (x, self._options[x]) for x in unused),
                    ]
                )
            )

        args = [page] + self.macro()

        try:
            macro.plot(*args)
        except Exception:
            LOG.error("Error executing: %r", args, exc_info=True)
            raise

        if fmt == ".svg":
            Display = SVG  # noqa: N806
        else:
            Display = Image  # noqa: N806

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
