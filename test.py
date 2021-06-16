from climetlab.core.caching import (
    cache_size,
    cache_entries,
    housekeeping

)

for n in cache_entries():
    print(n)



print(cache_size())
housekeeping()
