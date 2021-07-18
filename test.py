import mimetypes

from climetlab.sources.url import canonical_extension

print(mimetypes.guess_all_extensions("application/x-netcdf"))
# print(mimetypes.guess_type("x.cdf"))
# print(canonical_extension("z.nc"))
# print(canonical_extension("z.grib1"))
# print(canonical_extension("z.grib2"))
print(canonical_extension("z.tb2"))
