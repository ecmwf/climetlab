import climetlab as  cml
s = cml.load_source("demo-source", "sqlite:///test.db", "select * from data;", parse_dates=["time"])
