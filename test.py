import pandas as pd

from climetlab.normalize import normalize_args

dates = "2020-01-02/2020-12-31/P7D"
# r = pd.date_range(start="2020-01-02", end="2020-12-31", freq="w-thu")


# @normalize_args(date="date-list")
# def foo(date):
#     print(date)


# print(foo(r))


bits = dates.split('/')
import isodate
print(isodate.parse_duration(bits[2]))
