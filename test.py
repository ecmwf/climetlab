import climetlab as clm
import yaml

ds = clm.load_dataset("meteonet-radar")


print(yaml.dump(dict(style=ds.contouring, default_flow_style=False)))
