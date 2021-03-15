import folium
import folium.plugins
from branca.element import MacroElement
from jinja2 import Template
import os
from climetlab.core.ipython import HTML

with open(os.path.join(os.path.dirname(__file__), "wms.j2")) as f:
    direct_wms = f.read()


class DirectWMS(folium.raster_layers.WmsTileLayer):
    _name = "DirectWMS"
    _template = Template(direct_wms)


class NoScrollZoom(MacroElement):
    _name = "NoScrollZoom"
    _template = Template(
        """
        {% macro header(this,kwargs) %}
        {% endmacro %}
        {% macro html(this,kwargs) %}
        {% endmacro %}
        {% macro script(this,kwargs) %}
        {{ this._parent.get_name() }}.scrollWheelZoom.disable();
        {% endmacro %}
    """
    )


def make_map(url, bbox, **kwargs):
    # Prefer `folium` to `ipyleafet` as it does not
    # rely on ipywidgets, that are not always available
    # from ipyleaflet import Map, WMSLayer, projections, FullScreenControl

    center = (0, 0)
    zoom = 1

    if bbox is not None:
        center = (bbox.north + bbox.south) / 2, (bbox.east + bbox.west) / 2
        zoom = 1 / max((bbox.north - bbox.south) / 180, (bbox.east - bbox.west) / 360)
        zoom = (2 * zoom + 88) / 27

    m = folium.Map(zoom_start=zoom, location=center)

    DirectWMS(
        url=url, layers=["climetlab"], transparent=True, fmt="image/png", **kwargs
    ).add_to(m)

    # https://github.com/python-visualization/folium/blob/master/examples/Plugins.ipynb
    # https://deepnote.com/publish/9ad481b5-5756-4710-a839-2e129e0d9d94

    folium.plugins.Fullscreen(force_separate_button=True).add_to(m)
    NoScrollZoom().add_to(m)

    if bbox is not None:
        m.fit_bounds([[bbox.south, bbox.east], [bbox.north, bbox.west]])

    with open(os.path.join(os.path.dirname(__file__), "wms.js")) as f:
        wms_js = f.read()

    return HTML("<script>{}</script>{}".format(wms_js, m._repr_html_()))
