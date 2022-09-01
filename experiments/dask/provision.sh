
#!/bin/bash
set -x
node=$1

if [[ ! -f /usr/bin/pip3 ]]; then
   apt-get update
   apt-get install -y python3-pip
fi

if [[ ! -f /usr/bin/simpleproxy ]]; then
   apt-get install -y simpleproxy
fi

pip3 freeze | grep climetlab
if [[ $? -ne 0 ]]; then
   pip3 install bokeh
   pip3 install "dask[distributed]"
   pip3 install git+https://github.com/ecmwf/climetlab.git@develop
fi

if [[ $node -eq 0 ]]; then

   # 10.0.2.15 is this machine (guest of Vagrant)
   node0=10.0.2.15
   proxy="-Lnode0:8786 -Rlocalhost:8786"

else

   # 10.0.2.2 is the IP of the host machine
   node0=10.0.2.2
   proxy="-Rnode0:8786 -Llocalhost:8786"
fi

grep scheduler /etc/hosts
if [[ $? -ne 0 ]]; then
   # 10.0.2.2 is the IP of the host machine
   echo "$node0 node0 scheduler dashboard" >>/etc/hosts
fi

cat <<EOF > /etc/systemd/system/simpleproxy.service
[Service]
Type=simple
ExecStart=/usr/bin/simpleproxy $proxy
Restart=always

[Install]
WantedBy=multi-user.target

[Unit]
Description=Simple Proxy
After=network.target
EOF
systemctl daemon-reload
systemctl start simpleproxy

hostnamectl set-hostname node$node
