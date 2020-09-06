import climetlab as cml

dataset = cml.load_dataset("sample-grib-data")
data = dataset[0]

cml.plot_map(data, foreground=False)

cml.plot_map(data, foreground=True)


cml.plot_map(data, foreground="default-foreground")

cml.plot_map(
    data,
    foreground=dict(
        map_grid=False, map_label=False, map_grid_frame=True, map_grid_frame_thickness=5
    ),
)
