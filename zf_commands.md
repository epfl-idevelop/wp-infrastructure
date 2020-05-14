# Mes petits trucs à moi pour bien travailler ;-)
#zf200514.1143

<!-- TOC titleSize:2 tabSpaces:2 depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 skip:2 title:1 charForUnorderedList:* -->
## Table of Contents
* [Mon ..., mais c'est si simple pour AWX](#mon--mais-cest-si-simple-pour-awx)
* [Shortcuts pour Atom](#shortcuts-pour-atom)
* [Go go go !](#go-go-go-)
  * [Sur sa machine](#sur-sa-machine)
  * [Sur sa machine dans une console](#sur-sa-machine-dans-une-console)
    * [A faire au début du travail](#a-faire-au-début-du-travail)
    * [En travail](#en-travail)
  * [Se connecter en ssh dans un runner (pod)](#se-connecter-en-ssh-dans-un-runner-pod)
  * [Sur Grafana](#sur-grafana)
<!-- /TOC -->

# Mon ..., mais c'est si simple pour AWX
https://drive.google.com/open?id=1NyrVYI0ub9yKV8dxzvWOnYJQWrrw6oD5gn117xehhQU


# Shortcuts pour Atom
* push windows line to terminal CTRL+ALT+ENT
* toggle windows to terminal ALT+CMD+F



# Go go go !
## Sur sa machine
démarrer les VPN

Dans un browser:
https://awx-poc-vpsi.epfl.ch/#/login
https://pub-os-exopge.epfl.ch/console/project/wwp-test/overview


## Sur sa machine dans une console
### A faire au début du travail
```
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
cd ansible
pwd
oc login
oc project wwp-test
oc projects
```


### En travail
Dans sa console de sa machine
```
./wpsible -t awx --test
```


## Se connecter en ssh dans un runner (pod)
Trouver le nom du pod
```
oc get pod |grep awx-job
```
Se connecter en ssh dans le pod:
```
oc rsh awx-job-xxx
```
Puis quand on se trouve en ssh dans le pod:
```
bash
sudo yum -y install git nano
git clone https://github.com/zuzu59/deploy-proxmox.git
source ./deploy-proxmox/alias
./deploy-proxmox/env_a_zuzu.sh
git clone https://github.com/zuzu59/telegraf.git
cd telegraf
```
Copier les influxdb_secrets (export dbflux_*) depuis un autre terminal:
```
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
```
Puis les coller dans le terminal runner:
```
export dbflux_*
```
Vérifier dans le pod qu'ils sont bien présents:
```
env |grep dbflux
```
Installer Telegraf:
```
./oc_yum_install_telegraf.sh
```
Et enfin le lancer en tâche de fond:
```
/usr/bin/telegraf --debug -config /etc/telegraf/telegraf.conf -config-directory /etc/telegraf/telegraf.d  > /dev/null 2>&1 &
```






## Sur Grafana
http://noc-tst.idev-fsd.ml:9092/

Les credentials pour Grafana sont dans Keybase:
```
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
```





On peut importer le dashboard 928, qui permet déjà de voir une jolie vue
https://grafana.com/grafana/dashboards/928

