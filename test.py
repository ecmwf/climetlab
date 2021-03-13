#!/usr/bin/env python
# coding: utf-8

# In[73]:


import cfgrib
import xarray as xr

from climetlab import load_source
from climetlab.sources.readers.grib import FieldSetIndex

source = load_source("file", "docs/examples/test.grib")

store = xr.backends.CfGribDataStore(FieldSetIndex(source))

d = xr.open_dataset(store, engine="cfgrib")
