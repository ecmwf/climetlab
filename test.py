# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import climetlab as cml

# %%
ds = cml.load_source(
    "url")

# %% [markdown]
#

# %%
ds.path


# %%
ds.to_xarray()


# %%
cml.plot_map(ds)

# %%
