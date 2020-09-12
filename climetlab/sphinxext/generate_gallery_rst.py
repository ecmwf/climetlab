#!/usr/bin/env python3
# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import os
import sys

import climetlab
import climetlab.plotting

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs")


def plot_projection(name, path):
    print("plot_projection", name, file=sys.stderr)
    climetlab.plot_map(None, projection=name, background="land-sea", path=path)
    print("done", name, file=sys.stderr)

def plot_layer(name, path):
    print("plot_layer", name, file=sys.stderr)
    climetlab.plot_map(None, background=False, foreground=name, path=path)
    print("done", name, file=sys.stderr)

def plot_style(name, path):
    print("plot_style", name, file=sys.stderr)
    yaml = climetlab.plotting.style(name).data

    gallery = yaml.get("gallery", {})

    if "sample" in gallery:
        sample = gallery["sample"]
        if "source" in sample:
            source  = sample["source"]
            print("source", source["name"], source.get("args", {}), file=sys.stderr)
            data = climetlab.load_source(source["name"], **source.get("args", {}))
            data = data[0]
            print("done", source["name"], file=sys.stderr)
        else:
            dataset  = sample["dataset"]
            print("dataset", dataset["name"], dataset.get("args", {}), file=sys.stderr)
            data = climetlab.load_dataset(dataset["name"], **dataset.get("args", {}))
            if "to_pandas" in sample:
                data = data.to_pandas(**sample["to_pandas"])
            print("done", dataset["name"], file=sys.stderr)
    else:
        if "msymb" in yaml["magics"]:
            data = climetlab.load_dataset("sample-bufr-data")
            data = data.to_pandas(
                columns=(
                    "stationNumber",
                    "latitude",
                    "longitude",
                    "data_datetime",
                    "pressure",
                    "airTemperature",
                ),
                filters={},
            )
        if "mcont" in yaml["magics"]:
            data = climetlab.load_dataset("sample-grib-data")[0]


    extra = gallery.get("plot_map", {})

    climetlab.plot_map(data, style=name, path=path, **extra)
    print("done", name, file=sys.stderr)


def output(title, collection, plotter):

    print()
    print(title[0].upper() + title[1:])
    print("-" * len(title))
    print()

    path = os.path

    for p in collection:
        print()
        print(p)
        print("^" * len(p))

        image = "_static/gallery/%s/%s.svg" % (title, p)
        path = os.path.join(DOCS, image)

        if not os.path.exists(path):
            try:
                os.makedirs(os.path.dirname(path))
            except FileExistsError:
                pass
            # try:
            plotter(p, path)
            # except Exception as e:
            #     print(e)

        print()
        print(".. image::", "/" + image)
        print("   :width: 600")
        print()


def execute():

    output("layers", climetlab.plotting.layers(), plot_layer)
    output("styles", climetlab.plotting.styles(), plot_style)
    output("projections", climetlab.plotting.projections(), plot_projection)


if __name__ == "__main__":
    execute()
