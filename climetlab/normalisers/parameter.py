# (C) Copyright 2021 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

# from climetlab.utils.parameters import yaml_loader_from_cfgrib_TODO


class ParameterNormaliser:
    def __init__(self, format=None):
        self.format = format

    def normalise(self, parameter):
        print(f"Normalising {parameter}")
        if parameter == "2t":
            parameter = "2t"
            # parameter = 't2m'
        elif parameter == "tp":
            pass
        else:
            raise NotImplementedError
        return parameter
