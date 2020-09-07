import climetlab as cml

# Change the location of the cache:
cml.settings.set("cache-directory", "/big-disk")

# Set some default plotting options (e.g. all maps will
# be 400 pixels wide by default):
cml.settings.set("plotting-options", width=400)
