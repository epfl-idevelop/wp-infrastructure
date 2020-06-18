# Mes petits trucs à moi pour bien travailler ;-)
#zf200618.1453

<!-- TOC titleSize:2 tabSpaces:2 depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 skip:2 title:1 charForUnorderedList:* -->
## Table of Contents
* [Mon ..., mais c'est si simple pour AWX](#mon--mais-cest-si-simple-pour-awx)
* [Shortcuts pour Atom](#shortcuts-pour-atom)
* [Go go go !](#go-go-go-)
  * [Sur sa machine](#sur-sa-machine)
  * [Sur sa machine dans une console](#sur-sa-machine-dans-une-console)
    * [A faire au début du travail](#a-faire-au-début-du-travail)
    * [Copier son dépôt *local* sur le POD AWX](#copier-son-dépôt-local-sur-le-pod-awx)
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


### Copier son dépôt *local* sur le POD AWX
Quand on *lance* un template sur AWX (icône petite *fusée*), il va normalement *chercher* ses données Ansible sur https://github.com/epfl-si/wp-ops dans la branche *profiling/awx*, cela demande à chaque changement de code Ansible, de faire un *commit* et un *push* de notre *local* sur Github !
On peut **accélérer grandement le processus** en faisant, une fois sur l'interface WEB AWX, une copie du projet *WWP* et en lui configurant:<br>
**Type de SCM**=manuel, **Chemin de base du projet**=/var/lib/awx/projects, **Répertoire de playbooks**=wp-ops

**ATTENTION: cette configuration n'est pas pérenne, il faut la refaire à chaque redéploiement du POD AWX !**

Après pour synchroniser son *dépôt local* avec celui du *POD AWX*, il suffit de faire à chaque fois:

```
oc rsync --delete /Users/zuzu/dev-vpsi/wp-ops awx-0:/var/lib/awx/projects --exclude .git --exclude ansible-deps-cache
```

**ATTENTION: on ne peut copier qu'un *dossier*, pas un *fichier*. Si on ne veut copier qu'un seul fichier, il faut tout *exclure* puis *inclure* spécifiquement le fichier désiré:**

```
--exclude=* --include=toto.txt
```

On peut après voir le résultat dans le POD AWX avec:

```
oc rsh awx-0
bash
cd /var/lib/awx/projects/wp-ops/
ls -al
exit
exit
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
oc rsh awx-job-10xx
```
Puis quand on se trouve en ssh dans le pod:
```
bash
git clone https://github.com/zuzu59/deploy-proxmox.git
source ./deploy-proxmox/alias
./deploy-proxmox/env_a_zuzu.sh
sudo -sE

#git clone https://github.com/zuzu59/telegraf.git
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
./telegraf/install_docker_centos.sh
```
Et enfin le lancer en tâche de fond:
```
./telegraf/start_docker.sh
```




## Sur Grafana
http://noc-tst.idev-fsd.ml:9092/

Les credentials pour Grafana sont dans Keybase:
```
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
```





On peut importer le dashboard 928, qui permet déjà de voir une jolie vue
https://grafana.com/grafana/dashboards/928

