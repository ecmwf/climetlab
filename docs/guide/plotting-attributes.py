import climetlab as cml

# cml.settings.set("plotting-options", {'dump_yaml': True})

dataset = cml.load_dataset("example-dataset")
data = dataset[0]

cml.plot_map(data, foreground=False)

cml.plot_map(data, foreground=True)


cml.plot_map(data, foreground="example-foreground")

cml.plot_map(
    data,
    foreground=dict(
        map_grid=False,
        map_label=False,
        map_grid_frame=True,
        map_grid_frame_thickness=5,
        map_boundaries=True,
    ),
)

# Partial update of the current `foreground`
# How to do is still to be decided

# Option 1
cml.plot_map(
    data,
    foreground={
        "+map_rivers": True,
        "+map_cities": True,
        "+map_label": True,
        "-map_boundaries": None,
    },
)

# Option 2
cml.plot_map(
    data,
    foreground={
        "set": {"map_rivers": True, "map_cities": True, "map_label": True},
        "clear": ["map_boundaries"],
    },
)
# Option 3
cml.plot_map(
    data,
    foreground={
        "+": {"map_rivers": True, "map_cities": True, "map_label": True},
        "-": ["map_boundaries"],
    },
)
# Option 4
cml.plot_map(
    data,
    update_foreground={
        "map_rivers": True,
        "map_cities": True,
        "map_label": True,
        "map_boundaries": None,
    },
)

# Option 5
cml.plot_map(
    data,
    update={
        "foreground": {
            "map_rivers": True,
            "map_cities": True,
            "map_label": True,
            "map_boundaries": None,
        },
    },
)
