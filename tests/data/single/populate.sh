#!/usr/bin/env bash
set -e
for param in z t
do
for level in 500 1000
do
for date in 20000101 20000102
do
echo  "
retrieve,date=$date,level=$level,param=$param,target=${param}_${level}_${date}.grib,area=e,grid=5/5
" > r
echo ZZmars r
grib_to_netcdf -k 4 -D NC_SHORT -o ${param}_${level}_${date}.nc ${param}_${level}_${date}.grib
rm -f r
done
done
done
