import climetlab as cml

data = cml.load_dataset("hurricane-database", "atlantic")
print(data.home_page)


df = data.to_pandas()
irma = df[(df.name == "irma") & (df.year == 2017)]
cml.plot_map(irma)
