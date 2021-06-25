#!/usr/bin/env bash
for param in z t
do
for level in 500 1000
do
for format in netcdf grib
do
for date in 20000101 20000102
do
echo  "
retrieve,date=$date,level=$level,param=$param,target=${param}_${level}_${date}.$format,area=e,grid=5/5
" > r
mars r
rm -f r
done
done
done
done
