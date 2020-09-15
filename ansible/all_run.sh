#!/usr/bin/env bash
#Petit script pour lancer le post traitement des logs pour une batterie de tests

echo -e "
all_run.sh  zf200915.2252

Utilisation:

./all_run.sh > toto.txt
"

./parse-ansible-out4.py awx_logs_100_sites_5_forks_1_pods.txt
./parse-ansible-out4.py awx_logs_100_sites_30_forks_1_pods.txt
./parse-ansible-out4.py awx_logs_100_sites_50_forks_1_pods.txt
./parse-ansible-out4.py awx_logs_100_sites_5_forks_10_pods.txt



