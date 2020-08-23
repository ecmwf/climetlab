from climetlab.utils.datetime import datetimes_to_dates_and_times
import datetime

x = datetime.datetime.fromisoformat("1990-01-01")

print(datetimes_to_dates_and_times([x], as_request=True))
