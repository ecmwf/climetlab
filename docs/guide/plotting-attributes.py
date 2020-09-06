import climetlab as cml

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


cml.plot_map(
    data,
    foreground={
        "+map_rivers": True,
        "+map_cities": True,
        "+map_label": True,
        "-map_boundaries": None,
    },
)


cml.plot_map(
    data,
    foreground={
        "set": {"map_rivers": True, "map_cities": True, "map_label": True},
        "clear": ["map_boundaries"],
    },
)

cml.plot_map(
    data,
    foreground={
        "+": {"map_rivers": True, "map_cities": True, "map_label": True},
        "-": ["map_boundaries"],
    },
)
