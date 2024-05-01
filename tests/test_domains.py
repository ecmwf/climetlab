#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#


from climetlab.utils.domains import domain_to_area
from climetlab.utils.domains import domain_to_area_long_name


def test_domains():
    assert domain_to_area("italy") == (50.5, 5.0, 35.0, 20.5)
    assert domain_to_area_long_name("italy") is None

    assert domain_to_area("verification.germany") == (55.5, 5.5, 47.0, 15.5)
    assert domain_to_area_long_name("verification.germany") == "Germany"

    assert domain_to_area("uk") == (63.5, -10.0, 48.0, 5.5)
    assert domain_to_area("verification.uk") == (59.5, -10.5, 49.5, 2.0)
    assert domain_to_area_long_name("verification.uk") == "United Kingdom"

    assert domain_to_area("france") == (54.5, -6.0, 39.0, 9.5)
    assert domain_to_area("verification.france") == (51.5, -5.0, 42.0, 8.5)


if __name__ == "__main__":
    from climetlab.testing import main

    main(__file__)
