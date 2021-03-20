from climetlab import new_plot
from climetlab.core.caching import temp_file

from ._folium import make_map


def interactive_map(obj, **kwargs):

    h = 100 * 3

    tmp = temp_file(".svg")
    p = new_plot(
        projection="web-mercator",
        width=6 * 1024,
        width_cm=h,
        height_cm=h,
        frame=False,
        foreground=False,
        background=False,
    )
    p.plot_map(obj)
    bbox = p.save(tmp.path)

    return make_map(tmp.path, bbox)
