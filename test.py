from climetlab.core.caching import cache_entries, cache_size, housekeeping

for n in cache_entries():
    print(n)


print(cache_size())
housekeeping()
