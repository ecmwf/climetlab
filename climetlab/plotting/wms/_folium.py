import folium
import folium.plugins
from branca.element import MacroElement
from jinja2 import Template
import os
from climetlab.core.ipython import HTML
from folium.map import Layer
import base64
from climetlab.utils.bbox import BoundingBox


class SVGOverlay(Layer):
    _name = "SVGOverlay"
    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var svgElement = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svgElement.setAttribute('xmlns', "http://www.w3.org/2000/svg");
            svgElement.setAttribute('viewBox', {{ this.viewBox|tojson }});
            svgElement.innerHTML = {{ this.innerHTML|tojson }}
            var {{ this.get_name() }} = L.svgOverlay(
                svgElement,
                {{ this.bounds|tojson }},
                {{ this.options|tojson }}
            ).addTo({{ this._parent.get_name() }});
        {% endmacro %}"""
    )

    def __init__(self, path, bounds, options={}):
        super().__init__()
        self.path = path
        self.bounds = bounds
        self.options = options

        lines = []
        ok = False
        with open(self.path) as f:
            for line in f:
                if line.startswith("viewBox="):
                    self.viewBox = line.split('"')[1]

                if line.startswith('<metadata id="MAGICSmetadata">'):
                    ok = True
                    continue

                if line.startswith("</svg>"):
                    ok = False
                    continue

                if ok:
                    lines.append(line)

        self.innerHTML = "".join(lines)

    def _get_self_bounds(self):
        return self.bounds


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


def make_map(path, bbox, **kwargs):
    # Prefer `folium` to `ipyleafet` as it does not
    # rely on ipywidgets, that are not always available
    # from ipyleaflet import Map, WMSLayer, projections, FullScreenControl

    # bbox = BoundingBox(north=90, west=-180, south=-90, east=180)
    center = (0, 0)
    zoom = 1

    if bbox is not None:
        center = (bbox.north + bbox.south) / 2, (bbox.east + bbox.west) / 2
        zoom = 1 / max((bbox.north - bbox.south) / 180, (bbox.east - bbox.west) / 360)
        zoom = (2 * zoom + 88) / 27

    m = folium.Map(zoom_start=zoom, location=center)  # , crs="Simple")

    SVGOverlay(
        path=path,
        # bounds=[[85.051129, -180],[-85.051129, 180]],
        bounds=[[90, -180], [-90, 180]],
        options=dict(opacity=0.6, autoZIndex=True),
    ).add_to(m)

    # DirectWMS(
    #     url=url, layers=["climetlab"], transparent=True, fmt="image/png", **kwargs
    # ).add_to(m)

    # https://github.com/python-visualization/folium/blob/master/examples/Plugins.ipynb
    # https://deepnote.com/publish/9ad481b5-5756-4710-a839-2e129e0d9d94

    folium.plugins.Fullscreen(force_separate_button=True).add_to(m)
    NoScrollZoom().add_to(m)

    if bbox is not None:
        m.fit_bounds([[bbox.south, bbox.east], [bbox.north, bbox.west]])

    return m
    # with open(os.path.join(os.path.dirname(__file__), "wms.js")) as f:
    #     wms_js = f.read()

    # return HTML("<script>{}</script>{}".format(wms_js, m._repr_html_()))
