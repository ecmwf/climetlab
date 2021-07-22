#!/bin/bash

if ! command -v download-cli &> /dev/null
then
    echo "download-cli could not be found"
    echo "The download-cli utility documentation is here:"
    echo "https://sites.ecmwf.int/docs/nexus-toolkit/shell.html"
    echo "To install it, you may try the following (or read the doc):"
    echo "pip3 install nexus-toolkit -U -i https://get.ecmwf.int/repository/pypi-all/simple"
    exit 1
fi

if [[ -z "${ECMWF_PASSWD}" ]]; then
  echo 'Must set the password in ECMWF_PASSWD environment variable'
  echo "And the user name must be in ECMWF_USERNAME if it is different from $USER'"
  exit 1
fi

if [[ -z "${ECMWF_USERNAME}" ]]; then
  ECMWF_USERNAME=$USER
fi

set -eaux

function upload {
   download-cli  --system DOWNLOAD_INSTANCE \
                 --repository test-data \
                 -u $ECMWF_USERNAME -p $ECMWF_PASSWD \
                 upload --local-path $1 --remote-path climetlab/$2/
}

function download {
   download-cli  --system DOWNLOAD_INSTANCE \
                 --repository test-data \
                 -u $ECMWF_USERNAME -p $ECMWF_PASSWD \
                 download --query climetlab/$1 || \
   download-cli  --system DOWNLOAD_INSTANCE \
                 --repository test-data \
                 -u $ECMWF_USERNAME -p $ECMWF_PASSWD \
                 download --query climetlab/$1/'*'
    mv downloads/test-data/climetlab/* .
}

function download_2 {
    # S3 bucket must be mounted with s3fs on /s3/climetlab
    # cat /etc/fstab
    # s3fs#climetlab /s3/climetlab fuse _netdev,allow_other,nodev,nosuid,uid=1000,gid=1000,passwd_file=/root/.passwd-s3fs.climetlab,use_path_request_style,url=https://storage.ecmwf.europeanweather.cloud 0 0
    # Alternatively, use s3cmd

    cp -rp /s3/climetlab/test-data/$1 $2
}

rm -rf tmp-local

mkdir -p tmp-local/input
for i in input/mini-hc-20200102.zarr input/mini-hc-20200109.zarr input/mini-rt-20200102.zarr input/mini-rt-20200109.zarr; do
    # download_1 $i
    download_2 $i tmp-local/$i
    upload tmp-local/$i $i
done

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
upload grib.tar input

gzip grib.tar
upload grib.tar.gz input

tar zcf grib.tgz *.grib
upload grib.tgz input

zip grib.zip *.grib
upload grib.zip input

zip grib-2t.zip 2t-*.grib
upload grib-2t.zip input

zip grib-msl.zip msl-*.grib
upload grib-msl.zip input

dd if=/dev/random of=data.bin bs=1024 count=1024
for n in $(seq 0 9)
do
    ln -sf data.bin 1mb-$n.bin
    upload 1mb-$n.bin input
done

ln -sf $0 test.txt
upload test.txt input
