#!/usr/bin/env python3
from climetlab import load_source, plot_map


s = load_source("file", "docs/examples/test.grib")
plot_map(s[0])
plot_map(s[1])
# plot_map(s)
