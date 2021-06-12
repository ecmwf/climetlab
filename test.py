from climetlab.core.caching import (
    _check_cache_size,
    cache_size,
    decache,
    get_cached_files,
)

for n in get_cached_files():
    print(n)

decache(0)


print(cache_size())
_check_cache_size()
