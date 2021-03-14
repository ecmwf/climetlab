#!/usr/bin/env python
# coding: utf-8

# In[73]:
import climetlab as cml

ds = cml.load_dataset("era5-temperature", period=(1979, 1982), domain="France", time=12)
