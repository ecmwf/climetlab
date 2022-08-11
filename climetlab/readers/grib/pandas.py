# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import logging

LOG = logging.getLogger(__name__)


class PandasMixIn:
    def to_pandas(self, latitude=None, longitude=None, **kwargs):
        import pandas as pd

        def ident(x):
            return x

        filter = ident

        def select_point(d):
            return [x for x in d if x["lat"] == latitude and x["lon"] == longitude]

        if latitude is not None or longitude is not None:
            filter = select_point

        frames = []
        for s in self:
            df = pd.DataFrame(filter(s.data))
            df["datetime"] = s.valid_datetime()
            for k, v in s.as_mars().items():
                df[k] = v
            frames.append(df)
        return pd.concat(frames)
