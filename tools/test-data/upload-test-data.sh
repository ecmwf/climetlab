#!/bin/bash

set -eaux

function upload {
   download-cli  --system DOWNLOAD_INSTANCE \
                 --repository test-data \
                 -u $USER -p $PASSWD \
                 upload --local-path $1 --remote-path climetlab/
}

for param in 2t msl
do
    for date in 20000101 20000102 20000103
    do
        target="${param}-${date}.grib"
        if [[ ! -f $target ]]
        then
            echo retrieve,date=$date,levtype=sfc,param=$param,target=data,grid=10/10 | mars
            mv data $target
        fi
    done
done

tar cf grib.tar *.grib
upload grib.tar

gzip grib.tar
upload grib.tar.gz

tar zcf grib.tgz *.grib
upload grib.tgz

zip grib.zip *.grib
upload grib.zip

zip grib-2t.zip 2t-*.grib
upload grib-2t.zip

zip grib-msl.zip msl-*.grib
upload grib-msl.zip

dd if=/dev/random of=data.bin bs=1024 count=1024
for n in $(seq 0 9)
do
    ln -sf data.bin 1mb-$n.bin
    upload 1mb-$n.bin
done

ln -sf $0 test.txt
upload test.txt
