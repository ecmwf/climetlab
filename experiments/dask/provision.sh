
#!/bin/bash
set -x
node=$1
total=$2

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

for n in $(seq 0 $total)
do
   grep node$n /etc/hosts
   if [[ $? -ne 0 ]]; then
      echo "192.168.56.$((n+10)) node$n" >>/etc/hosts
   fi
done

# cat <<EOF > /etc/systemd/system/simpleproxy$n.service
# [Service]
# Type=simple
# ExecStart=/usr/bin/simpleproxy $proxy
# Restart=always

# [Install]
# WantedBy=multi-user.target

# [Unit]
# Description=Simple Proxy
# After=network.target
# EOF


#    systemctl daemon-reload
#    systemctl start simpleproxy$n
#    systemctl enable simpleproxy$n
# done

hostnamectl set-hostname node$node
