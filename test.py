# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import climetlab as cml

# %%
ds = cml.load_source(
    "url",
    (
        "https://nextcloud.lsasvcs.ipma.pt/s/saXJ9faXEBec25b/download?"
        "path=%2F&files=NETCDF4_LSASAF_CLIMA-01-2004-2019_MSG_LST_MSG-Disk_200401010000.nc"
    ),
)

# %% [markdown]
#

# %%
ds.path


# %%
ds.to_xarray()


# %%
cml.plot_map(ds)

# %%
