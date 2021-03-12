import os
import socket
import sys
import time
import traceback
import uuid
from contextlib import closing

import jinja2
import requests
import skinnywms
from flask import Flask, Response, jsonify, render_template, request, send_file
from IPython.lib import backgroundjobs as bg
from skinnywms.datatypes import Availability, DataLayer, Field
from skinnywms.plot.magics import Plotter, Styler
from skinnywms.server import WMSServer

from climetlab import new_plot
from climetlab.core.ipython import display

jobs = bg.BackgroundJobManager()
application = Flask(__name__)

# sys.stdout = open("output.log", "w")

loader = jinja2.ChoiceLoader(
    [
        application.jinja_loader,
        jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(skinnywms.__file__), "templates")
        ),
    ]
)

application.jinja_loader = loader


class CliMetLabPlotter(Plotter):
    pass


class CliMetLabField(Field):
    def __init__(self, obj):
        self.obj = obj
        self._layers = None

    @property
    def name(self):
        try:
            return self.obj.name
        except Exception:
            return "?"

    @property
    def title(self):
        try:
            return self.obj.title
        except Exception:
            return "?"

    @property
    def time(self):
        return None

    @property
    def styles(self):
        return ["default"]

    def render(self, context, driver, style):
        if self._layers is None:
            self.plot = new_plot()
            self.plot.plot_map(self.obj)
            self._layers = self.plot.wms_layers()
        return self._layers


class CliMetLabLayer(DataLayer):
    def __init__(self, obj):
        super().__init__(CliMetLabField(obj))


class CliMetLabAvailability(Availability):
    def __init__(self, obj):
        super().__init__()
        self._layers[""] = CliMetLabLayer(obj)


class CliMetLabStyler(Styler):
    pass


class CliMetLabWMSServer(WMSServer):
    def process(self, *args, **kwargs):
        try:
            return super().process(*args, **kwargs)
        except Exception:
            print(traceback.format_exc())
            raise


@application.route("/wms/<uid>", methods=["GET"])
def wms(uid):

    try:

        svr = CliMetLabWMSServer(
            CliMetLabAvailability(OBJECTS[uid]), CliMetLabPlotter(), CliMetLabStyler()
        )

        reply = svr.process(
            request,
            Response=Response,
            send_file=send_file,
            render_template=render_template,
            reraise=True,
        )

        return reply
    except Exception:
        print(traceback.format_exc())
        return Response(traceback.format_exc(), mimetype="text/plain", status=500)


@application.route("/status", methods=["GET"])
def status():
    return jsonify(
        dict(
            pid=os.getpid(),
        )
    )


def _task(port):
    # print("Start task", port)
    try:
        application.run(host="localhost", port=port, threaded=4)
    except Exception as e:
        print("WMS server crashed:", e)
    # print("End task", port)


class State:
    job = None
    url = None


STATE = State()


def start_wms():

    if STATE.job is not None and STATE.url is not None:
        if STATE.job.status == STATE.job.stat_running:
            return STATE.url
        jobs.flush()
        STATE.job = STATE.url = None

    for _ in range(10):

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(("localhost", 0))
            port = s.getsockname()[1]

        STATE.job = jobs.new(_task, port)
        while STATE.job.status is STATE.job.stat_created:
            time.sleep(0.1)

        n = 0
        while n < 3:
            status = f"http://localhost:{port}/status"
            try:
                r = requests.get(status)
                r.raise_for_status()
                if r.json()["pid"] == os.getpid():
                    STATE.url = f"http://localhost:{port}/wms"
                    return STATE.url
                else:
                    break
            except requests.exceptions.HTTPError as e:
                print("WMS status at", status, e)
                break
            except requests.exceptions.ConnectionError as e:
                print("WMS status at", status, e)
                time.sleep(1)
                n += 1

        time.sleep(1)

    raise Exception("Cannot start WMS server")


OBJECTS = {}


def interactive_map(obj, **kwargs):
    from ipyleaflet import Map, WMSLayer

    uid = str(uuid.uuid1())
    # TODO: use weak ref
    OBJECTS[uid] = obj
    url = "{}/{}".format(start_wms(), uid)

    wms = WMSLayer(url=url, format="image/png", transparent=True, **kwargs)

    m = Map(zoom=2, center=(50, 0))
    m.add_layer(wms)
    return display(m)
