#!/bin/bash
set -x

if [[ ! -f /usr/bin/pip3 ]]; then
   apt-get update
   apt-get install -y python3-pip
fi

pip3 freeze | grep climetlab
if [[ $? -ne 0 ]]; then
   pip3 install "dask[distributed]"
   pip3 install git+https://github.com/ecmwf/climetlab.git@develop
fi

grep scheduler /etc/hosts
if [[ $? -ne 0 ]]; then
   # 10.0.2.2 is the IP of the host machine
   echo "10.0.2.2 node0 scheduler dashboard" >>/etc/hosts
fi
