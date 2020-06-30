# Mes petits trucs à moi pour bien travailler ;-)
#zf200630.1111

<!-- TOC titleSize:2 tabSpaces:2 depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 skip:2 title:1 charForUnorderedList:* -->
## Table of Contents
* [Problèmes actuels](#problèmes-actuels)
  * [Erreur du DistutilsFileError: cannot copy tree '/var/lib/awx/projects/XXX_Project': not a directory](#erreur-du-distutilsfileerror-cannot-copy-tree-varlibawxprojectsxxxproject-not-a-directory)
* [Mon ..., mais c'est si simple pour AWX](#mon--mais-cest-si-simple-pour-awx)
* [Shortcuts pour Atom](#shortcuts-pour-atom)
* [Go go go !](#go-go-go-)
  * [Sur sa machine](#sur-sa-machine)
  * [Sur sa machine dans une console](#sur-sa-machine-dans-une-console)
    * [A faire au début du travail](#a-faire-au-début-du-travail)
    * [Accélération des tests du code Ansible](#accélération-des-tests-du-code-ansible)
      * [1ère solution](#1ère-solution)
      * [2ème solution](#2ème-solution)
    * [En travail, refaire l'image du ansible runner](#en-travail-refaire-limage-du-ansible-runner)
  * [Se connecter en ssh dans un runner (pod)](#se-connecter-en-ssh-dans-un-runner-pod)
  * [Sur Grafana](#sur-grafana)
<!-- /TOC -->

# Problèmes actuels
## Erreur du DistutilsFileError: cannot copy tree '/var/lib/awx/projects/XXX_Project': not a directory
zf200629.1812
En voulant utiliser les playbooks sur le disque du container AWX au lieu de Github, j'ai cette erreur:

```
Traceback (most recent call last): File "/var/lib/awx/venv/awx/lib/python3.6/site-packages/awx/main/tasks.py", line 1345, in run self.pre_run_hook(self.instance, private_data_dir) File "/var/lib/awx/venv/awx/lib/python3.6/site-packages/awx/main/tasks.py", line 1949, in pre_run_hook job.project.scm_type, job_revision File "/var/lib/awx/venv/awx/lib/python3.6/site-packages/awx/main/tasks.py", line 2342, in make_local_copy copy_tree(project_path, destination_folder, preserve_symlinks=1) File "/usr/lib64/python3.6/distutils/dir_util.py", line 124, in copy_tree "cannot copy tree '%s': not a directory" % src) distutils.errors.DistutilsFileError: cannot copy tree '/var/lib/awx/projects/wp-ops': not a directory
```

J'ai trouvé des infos sur:

https://github.com/ansible/awx/issues/6213

Mais je n'arrive pas à les interpréter :-(
  
https://www.google.com/search?q=awx+copy_tree+%22cannot+copy+tree+%27%25s%27%3A+not+a+directory%22+%25+src)&rlz=1C5CHFA_enCH890CH890&oq=awx+copy_tree+%22cannot+copy+tree+%27%25s%27%3A+not+a+directory%22+%25+src)&aqs=chrome..69i57.1395j1j4&sourceid=chrome&ie=UTF-8



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
allumer le VPN !

source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
cd ansible
pwd
oc login
oc project wwp-test
oc projects
```


### Accélération des tests du code Ansible
Quand on *lance* un template sur AWX (icône petite *fusée*), il va normalement *chercher* ses données Ansible sur https://github.com/epfl-si/wp-ops dans la branche *profiling/awx*, cela demande à chaque changement de code Ansible, de faire un *commit* et un *push* de notre *local* sur Github !<br>

#### 1ère solution
On peut y remédier en *trichant* un peu lors du commit:
```
GIT_EDITOR=true git commit -a --amend && git push -f
```
Du coup on gagne beaucoup de temps pour les tests !

#### 2ème solution
Ou alors, on peut **accélérer grandement le processus** en faisant, une fois sur l'interface WEB AWX, une copie du projet *WWP* et en lui configurant:<br>
**Type de SCM**=manuel, **Chemin de base du projet**=/var/lib/awx/projects, **Répertoire de playbooks**=wp-ops

**ATTENTION: cette configuration n'est pas pérenne, il faut la refaire à chaque redéploiement du POD AWX !**

Après pour synchroniser son *dépôt local* avec celui du *POD AWX*, il suffit de faire à chaque fois:

```
oc rsync --delete /Users/zuzu/dev-vpsi/wp-ops awx-0:/var/lib/awx/projects --exclude .git --exclude ansible-deps-cache
```

On peut le faire de manière automatique (--watch), détecte automatiquement les modifications de fichiers, mais cela déconne encore à cause du **ansible.suitecase** de domq :-(
```
oc rsync --delete /Users/zuzu/dev-vpsi/wp-ops awx-0:/var/lib/awx/projects --exclude .git --exclude ansible-deps-cache --watch
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


### En travail, refaire l'image du ansible runner
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

