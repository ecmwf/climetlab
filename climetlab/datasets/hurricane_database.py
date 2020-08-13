# See https://www.aoml.noaa.gov/hrd/hurdat/Data_Storm.html


from . import Dataset
from climetlab.utils import download_and_cache


SIGN = {"N": 1, "W": -1, "E": 1, "S": -1}

TYPE = {
    "C": "Closest approach to a coast, not followed by a landfall",
    "G": "Genesis",
    "I": "An intensity peak in terms of both pressure and wind",
    "L": "Landfall (center of system crossing a coastline)",
    "P": "Minimum in central pressure",
    "R": "Provides additional detail on the intensity of the cyclone when rapid changes are underway",
    "S": "Change of status of the system",
    "T": "Provides additional detail on the track (position) of the cyclone",
    "W": "Maximum sustained wind speed",
}

STATUS = {
    "TD": "Tropical cyclone of tropical depression intensity (< 34 knots)",
    "TS": "Tropical cyclone of tropical storm intensity (34-63 knots)",
    "HU": "Tropical cyclone of hurricane intensity (> 64 knots)",
    "EX": "Extratropical cyclone (of any intensity)",
    "SD": "Subtropical cyclone of subtropical depression intensity (< 34 knots)",
    "SS": "Subtropical cyclone of subtropical storm intensity (> 34 knots)",
    "LO": "A low that is neither a tropical cyclone, a subtropical cyclone, nor an extratropical cyclone (of any intensity)",
    "WV": "Tropical Wave (of any intensity)",
    "DB": "Disturbance (of any intensity)",
}


def category(knots):

    if knots < 83:
        return 1

    if knots < 96:
        return 2

    if knots < 113:
        return 3

    if knots < 137:
        return 4

    return 5


# def lookup(filter={'time': '0000', 'category': 5}):
#     cyclones = _load()
#     keys = filter.keys()
#     for n in cyclones:
#         for p in n['positions']:
#             ok = True
#             for k in keys:
#                 if p[k] != filter[k]:
#                     ok = False
#             if ok:
#                 d = dict()
#                 d.update(n)
#                 del d['positions']
#                 d.update(p)
#                 yield d


class HurricaneDatabase(Dataset):

    home_page = "https://www.aoml.noaa.gov/hrd/hurdat/Data_Storm.html"

    def __init__(self, url="https://www.aoml.noaa.gov/hrd/hurdat/hurdat2.txt"):
        path = download_and_cache(url)
        _cyclones = []
        with open(path) as f:
            lines = f
            for line in lines:
                cyclone = {
                    "bassin": line[0:2],
                    "number": line[3:4],
                    "year": line[4:8],
                    "name": line[18:28].strip().lower(),
                    "positions": [],
                }

                p = cyclone["positions"]
                # http://www.aoml.noaa.gov/hrd/hurdat/hurdat2-format-may2015.pdf

                for i in range(0, int(line[33:36])):
                    line = next(lines)
                    # print line
                    knots = float(line[38:41])
                    position = {
                        "date": line[0:8],
                        "time": line[10:14],
                        "type": line[16],
                        "status": line[19:21],
                        "lat": float(line[23:27]) * SIGN[line[27]],
                        "lon": float(line[30:35]) * SIGN[line[35]],
                        "knots": knots,
                        "category": category(knots),
                        "pressure": float(line[43:47]),
                        "m/s": knots * 0.514444,
                    }
                    p.append(position)

                _cyclones.append(cyclone)

        self.cyclones = _cyclones


dataset = HurricaneDatabase
