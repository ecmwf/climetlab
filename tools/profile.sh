set -x
for b in 67108864 2097152 524288 16384
do
    for c in  67108864 2097152 524288 16384
    do
        for t in $(seq 1 20)
        do
            ./profile.py -b $b -c $c -t $t -u https://storage.ecmwf.europeanweather.cloud/s2s-ai-challenge/data/forecast-input/ecmwf-forecast/0.2.5/netcdf/ecmwf-forecast-ttr-20200102.nc -o /dev/null
        done
    done
done
