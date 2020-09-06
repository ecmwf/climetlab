import climetlab as cml

# Access one of the settings
cache_path = cml.settings.get("cache-directory")
print(cache_path)

# If this is the last line of a Notebook cell, this
# will display a table with all the current settings
cml.settings
