# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.
#

from climetlab import Dataset


class Meteonet(Dataset):

    URL = "https://github.com/meteofrance/meteonet/raw/master/data_samples"

    home_page = "https://meteofrance.github.io/meteonet/"

    licence = "https://meteonet.umr-cnrm.fr/dataset/LICENCE.md"
