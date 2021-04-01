import folium
import folium.plugins
from branca.element import MacroElement
from folium.map import Layer
from jinja2 import Template

from climetlab.core.ipython import HTML, guess_which_ipython


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

    center = (0, 0)
    zoom = 1
    # fmt = "image/svg+xml"
    # fmt = "image/png"

    if bbox is not None:
        center = (bbox.north + bbox.south) / 2, (bbox.east + bbox.west) / 2
        zoom = 1 / max((bbox.north - bbox.south) / 180, (bbox.east - bbox.west) / 360)
        zoom = (2 * zoom + 88) / 27

    m = folium.Map(
        zoom_start=zoom,
        location=center,
        # tiles=None,
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    )  # tiles=None

    # folium.raster_layers.WmsTileLayer(
    #     url="https://apps.ecmwf.int/wms/?token=public",
    #     layers="background",
    #     fmt=fmt,
    #     # styles="cream_sky_background",
    #     # transparent=True,
    #     overlay=False,
    # ).add_to(m)
    # folium.raster_layers.WmsTileLayer(
    #     url="https://apps.ecmwf.int/wms/?token=public",
    #     layers="background",
    #     fmt=fmt,
    #     styles="black_admin_boundaries",
    #     transparent=True,
    #     # overlay=False,
    # ).add_to(m)
    SVGOverlay(
        path=path,
        # bounds=[[85.051129, -180],[-85.051129, 180]],
        bounds=[[90, -180], [-90, 180]],
        # options=dict(opacity=0.6, autoZIndex=True),
        options=dict(attribution="CliMetLab"),
    ).add_to(m)

    folium.plugins.Fullscreen(force_separate_button=True).add_to(m)
    NoScrollZoom().add_to(m)

    # folium.raster_layers.WmsTileLayer(
    #     url="https://apps.ecmwf.int/wms/?token=public",
    #     layers="foreground",
    #     fmt=fmt,
    #     transparent=True,
    #     styles="medium_res_foreground",
    #     # overlay=False,
    # ).add_to(m)

    # folium.raster_layers.WmsTileLayer(
    #     url="https://apps.ecmwf.int/wms/?token=public",
    #     layers="grid",
    #     fmt=fmt,
    #     transparent=True,
    #     # overlay=False,
    # ).add_to(m)

    if bbox is not None:
        m.fit_bounds([[bbox.south, bbox.east], [bbox.north, bbox.west]])

    html = m._repr_html_()

    if guess_which_ipython()[0] == "deepnote":

        # For deepnote
        html = html.replace("width: 100%;height: 100%", "width: 100%").replace(
            "height: 100.0%;", "height: 609px;"
        )

    return HTML(html)
