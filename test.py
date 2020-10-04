from climetlab import load_source, plot_map

s = load_source("file", "docs/examples/test.grib")
plot_map(s[0], path="x.png")
plot_map(s[1], path="y.png")
# plot_map(s)
