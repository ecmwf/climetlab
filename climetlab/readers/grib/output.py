# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging
import re

from climetlab.decorators import alias_argument, normalize
from climetlab.utils.humanize import list_to_human

LOG = logging.getLogger(__name__)

# Make sure the

ACCUMULATIONS = {("tp", 2): {"productDefinitionTemplateNumber": 8}}


class Combined:
    def __init__(self, handle, metadata):
        self.handle = handle
        self.metadata = metadata

    def __contains__(self, key):
        raise NotImplementedError()

    def __getitem__(self, key):
        if key in self.metadata:
            return self.metadata[key]
        return self.handle.get(key)


class GribOutput:
    def __init__(self, filename, split_output=False, template=None, **kwargs):
        self._files = {}
        self.filename = filename

        if split_output:
            self.split_output = re.findall(r"\{(.*?)\}", self.filename)
        else:
            self.split_output = None

        self.template = template
        self._bbox = {}
        self.kwargs = kwargs

    @alias_argument("levelist", ["level", "levellist"])
    @alias_argument("levtype", ["leveltype"])
    @alias_argument("param", ["variable", "parameter"])
    @alias_argument("number", ["realization", "realisation"])
    @alias_argument("class", ["klass", "class_"])
    @normalize("date", "date")
    def _normalize_kwargs_names(self, **kwargs):
        return kwargs

    def f(self, handle):
        if self.split_output:
            path = self.filename.format(**{k: handle.get(k) for k in self.split_output})
        else:
            path = self.filename

        if path not in self._files:
            self._files[path] = open(path, "wb")
        return self._files[path]

    def write(
        self,
        values,
        check_nans=False,
        missing_value=1e36,
        metadata={},
        template=None,
        **kwarg,
    ):
        # Make a copy as we may modify it
        md = self._normalize_kwargs_names(**self.kwargs)
        md.update(self._normalize_kwargs_names(**metadata))
        md.update(self._normalize_kwargs_names(**kwarg))

        metadata = md

        if template is None:
            template = self.template

        if template is None:
            handle = self.handle_from_metadata(values, metadata)
        else:
            handle = template.handle.clone()

        self.update_metadata(handle, metadata)

        other = {}

        for k, v in list(metadata.items()):
            if not isinstance(v, (int, float, str)):
                other[k] = metadata.pop(k)

        if check_nans:
            import numpy as np

            if np.isnan(values).any():
                missing_value = np.finfo(values.dtype).max
                values = np.nan_to_num(values, nan=missing_value)
                metadata["bitmapPresent"] = 1

        LOG.debug("GribOutput.metadata %s", metadata)
        LOG.debug("GribOutput.metadata %s", other)

        handle.set_multiple(metadata)

        for k, v in other.items():
            handle.set(k, v)

        handle.set_values(values)
        handle.write(self.f(handle))

    def close(self):
        for f in self._files.values():
            f.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self.close()

    def update_metadata(self, handle, metadata):
        # TODO: revisit that logic
        combined = Combined(handle, metadata)
        if "step" in metadata:
            if combined["type"] == "an":
                metadata["type"] = "fc"

    def handle_from_metadata(self, values, metadata):
        from .codes import CodesHandle  # Lazy loading of eccodes

        if len(values.shape) == 1:
            sample = self._gg_field(values, metadata)
        elif len(values.shape) == 2:
            sample = self._ll_field(values, metadata)
        else:
            raise ValueError(
                f"Invalid shape {values.shape} for GRIB, must be 1 or 2 dimension "
            )

        compulsary = ("date", ("param", "paramId", "shortName"))

        metadata.setdefault("bitsPerValue", 16)
        metadata["scanningMode"] = 0

        if "stream" not in metadata:
            if "number" in metadata:
                metadata["stream"] = "enfo"
                metadata.setdefault("type", "pf")

        if "number" in metadata:
            compulsary += ("numberOfForecastsInEnsemble",)

        if "levelist" in metadata:
            metadata.setdefault("levtype", "pl")

        if "param" in metadata:
            param = metadata.pop("param")
            try:
                metadata["paramId"] = int(param)
            except ValueError:
                metadata["shortName"] = param

        metadata.update(
            ACCUMULATIONS.get(
                (
                    metadata.get("paramId"),
                    metadata.get("edition", 2),
                ),
                {},
            )
        )
        metadata.update(
            ACCUMULATIONS.get(
                (
                    metadata.get("shortName"),
                    metadata.get("edition", 2),
                ),
                {},
            )
        )

        if "time" in metadata:  # TODO, use a normalizer
            try:
                time = int(metadata["time"])
                if time < 100:
                    metadata["time"] = time * 100
            except ValueError:
                pass

        if "time" not in metadata and "date" in metadata:
            date = metadata["date"]
            metadata["time"] = date.hour * 100 + date.minute

        if "date" in metadata:
            date = metadata["date"]
            metadata["date"] = date.year * 10000 + date.month * 100 + date.day

        if (
            "class" in metadata
            or "type" in metadata
            or "stream" in metadata
            or "expver" in metadata
        ):
            # MARS labelling
            metadata["setLocalDefinition"] = 1
            # metadata['grib2LocalSectionNumber'] = 1

        for check in compulsary:
            if not isinstance(check, tuple):
                check = [check]

            if not any(c in metadata for c in check):
                choices = list_to_human([f"'{c}'" for c in check], "or")
                raise ValueError(f"Please provide a value for {choices}.")

        LOG.debug("CodesHandle.from_sample(%s)", sample)
        return CodesHandle.from_sample(sample)

    def _ll_field(self, values, metadata):
        Nj, Ni = values.shape
        metadata["Nj"] = Nj
        metadata["Ni"] = Ni

        # We assume the scanning mode north->south, west->east
        west_east = 360 / Ni

        if Nj % 2 == 0:
            north_south = 180 / Nj
            adjust = north_south / 2
        else:
            north_south = 181 / Nj
            adjust = 0

        north = 90 - adjust
        south = -90 + adjust
        west = 0
        east = 360 - west_east

        metadata["iDirectionIncrementInDegrees"] = west_east
        metadata["jDirectionIncrementInDegrees"] = north_south

        metadata["latitudeOfFirstGridPointInDegrees"] = north
        metadata["latitudeOfLastGridPointInDegrees"] = south
        metadata["longitudeOfFirstGridPointInDegrees"] = west
        metadata["longitudeOfLastGridPointInDegrees"] = east

        edition = metadata.get("edition", 2)
        levtype = metadata.get("levtype")
        if levtype is None:
            if "levelist" in metadata:
                levtype = "pl"
            else:
                levtype = "sfc"

        return f"regular_ll_{levtype}_grib{edition}"

    def _gg_field(self, values, metadata):
        GAUSSIAN = {
            6114: (32, False),
            13280: (48, False),
            24572: (64, False),
            35718: (80, False),
            40320: (96, True),
            50662: (96, False),
            88838: (128, False),
            108160: (160, True),
            138346: (160, False),
            213988: (200, False),
            348528: (256, False),
            542080: (320, False),
            843490: (400, False),
            1373624: (512, False),
            2140702: (640, False),
            5447118: (1024, False),
            8505906: (1280, False),
            20696844: (2000, False),
        }

        n = len(values)
        if n not in GAUSSIAN:
            raise ValueError(f"Unsupported GAUSSIAN grid. Number of grid points {n:,}")
        N, octahedral = GAUSSIAN[n]

        if N not in self._bbox:
            import eccodes

            self._bbox[N] = max(eccodes.codes_get_gaussian_latitudes(N))

        metadata["latitudeOfFirstGridPointInDegrees"] = self._bbox[N]
        metadata["latitudeOfLastGridPointInDegrees"] = -self._bbox[N]
        metadata["longitudeOfFirstGridPointInDegrees"] = 0

        metadata["N"] = N
        if octahedral:
            half = list(range(20, 20 + N * 4, 4))
            pl = half + list(reversed(half))
            assert len(pl) == 2 * N, (len(pl), 2 * N)
            metadata["pl"] = pl
            metadata["longitudeOfLastGridPointInDegrees"] = 360 - max(pl) / 360
        else:
            # Assumed to be set properly in the sample
            # metadata["longitudeOfLastGridPointInDegrees"] = east
            pass

        edition = metadata.get("edition", 2)
        levtype = metadata.get("levtype")
        if levtype is None:
            if "levelist" in metadata:
                levtype = "pl"
            else:
                levtype = "sfc"

        if octahedral:
            return f"reduced_gg_{levtype}_grib{edition}"
        else:
            return f"reduced_gg_{levtype}_{N}_grib{edition}"


def new_grib_output(*args, **kwargs):
    return GribOutput(*args, **kwargs)
