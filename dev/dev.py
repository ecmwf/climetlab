import climetlab as cml

url = "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/monthly.ao.index.b50.current.ascii"
s = cml.load_source("url", url, reader="fix_width_format")
print(s.to_pandas())
