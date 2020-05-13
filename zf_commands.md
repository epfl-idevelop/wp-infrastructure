#zf200513.1723

Mon mais c'est si simple pour AWX:
https://drive.google.com/open?id=1NyrVYI0ub9yKV8dxzvWOnYJQWrrw6oD5gn117xehhQU


A faire au début du travail
démarrer les VPN

cd ansible
pwd
oc login
oc project wwp-test
oc projects

./wpsible -t awx --test

https://awx-poc-vpsi.epfl.ch/#/login
https://pub-os-exopge.epfl.ch/console/project/wwp-test/overview



Dans un runner

bash
sudo yum -y install git nano
git clone https://github.com/zuzu59/deploy-proxmox.git
source ./deploy-proxmox/alias
./deploy-proxmox/env_a_zuzu.sh
git clone https://github.com/zuzu59/telegraf.git
cd telegraf




