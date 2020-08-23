from climetlab.utils.datetime import datetimes_to_dates_and_times
import datetime

x = datetime.datetime.fromisoformat("1990-01-01")

print(datetimes_to_dates_and_times("1/3/99", as_request=True))
