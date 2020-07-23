# Mes petits trucs à moi pour bien travailler ;-)
#zf200723.1630

<!-- TOC titleSize:2 tabSpaces:2 depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 skip:2 title:1 charForUnorderedList:* -->
## Table of Contents
* [Mon ..., mais c'est si simple pour AWX](#mon--mais-cest-si-simple-pour-awx)
* [Shortcuts pour Atom](#shortcuts-pour-atom)
* [Go go go !](#go-go-go-)
  * [Sur sa machine](#sur-sa-machine)
  * [Sur sa machine dans une console](#sur-sa-machine-dans-une-console)
    * [A faire au début du travail](#a-faire-au-début-du-travail)
    * [Accélération des tests du code Ansible](#accélération-des-tests-du-code-ansible)
      * [1ère solution](#1ère-solution)
      * [2ème solution](#2ème-solution)
    * [En travail lancer la petite fusée d'un template dans le GUI de AWX](#en-travail-lancer-la-petite-fusée-dun-template-dans-le-gui-de-awx)
      * [Puis récupérer les logs de la tâche (numéro) du template](#puis-récupérer-les-logs-de-la-tâche-numéro-du-template)
      * [Et enfin parser les logs avec le parser en python](#et-enfin-parser-les-logs-avec-le-parser-en-python)
    * [En travail, si on veut refaire l'image du Ansible runner ET du container utilisé par AWX](#en-travail-si-on-veut-refaire-limage-du-ansible-runner-et-du-container-utilisé-par-awx)
      * [ATTENTION:](#attention)
  * [Se connecter en ssh dans un runner (pod)](#se-connecter-en-ssh-dans-un-runner-pod)
  * [Sur Grafana](#sur-grafana)
* [Problèmes actuels](#problèmes-actuels)
  * [Erreur du DistutilsFileError: cannot copy tree '/var/lib/awx/projects/XXX_Project': not a directory](#erreur-du-distutilsfileerror-cannot-copy-tree-varlibawxprojectsxxxproject-not-a-directory)
* [Où en suis-je juste avant de partir en vacances zf200723.1641 ?](#où-en-suis-je-juste-avant-de-partir-en-vacances-zf2007231641-)
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
allumer le VPN !

source /keybase/team/epfl_wwp_blue/influxdb_secrets.sh
source /keybase/private/zuzu59/tequila_zf_secrets.sh
cd /Users/zuzu/dev-vpsi/wp-ops/ansible
oc login -u czufferey
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


### En travail lancer la petite fusée d'un template dans le GUI de AWX
https://awx-poc-vpsi.epfl.ch/#/login

#### Puis récupérer les logs de la tâche (numéro) du template

* Dans un browser en mode *humain*

  https://awx-poc-vpsi.epfl.ch/api/v2/jobs/1219/stdout/

* Dans un curl en mode *machine*

  https://awx-poc-vpsi.epfl.ch/api/v2/jobs/1219/stdout/?format=txt

```
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1222/stdout/?format=txt > awx_logs_2_sites_1_pods.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1241/stdout/?format=txt > awx_logs_10_sites_1_pods.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1225/stdout/?format=txt_download > awx_logs_347_sites_1_pods.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1229/stdout/?format=txt_download > awx_logs_347_sites_10_pods_1.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1230/stdout/?format=txt_download > awx_logs_347_sites_10_pods_2.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1231/stdout/?format=txt_download > awx_logs_347_sites_10_pods_3.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1232/stdout/?format=txt_download > awx_logs_347_sites_10_pods_4.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1233/stdout/?format=txt_download > awx_logs_347_sites_10_pods_5.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1234/stdout/?format=txt_download > awx_logs_347_sites_10_pods_6.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1235/stdout/?format=txt_download > awx_logs_347_sites_10_pods_7.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1236/stdout/?format=txt_download > awx_logs_347_sites_10_pods_8.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1237/stdout/?format=txt_download > awx_logs_347_sites_10_pods_9.txt
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1238/stdout/?format=txt_download > awx_logs_347_sites_10_pods_10.txt

less awx_logs.txt

./parse-ansible-out2.py awx_logs_2_sites_1_pods.txt
./parse-ansible-out2.py awx_logs_10_sites_1_pods.txt
./parse-ansible-out2.py awx_logs_347_sites_1_pods.txt

```
     
#### Et enfin parser les logs avec le parser en python




### En travail, si on veut refaire l'image du Ansible runner ET du container utilisé par AWX
Dans sa console de sa machine
```
./wpsible -t awx
```

#### ATTENTION:
Si on a rebuildé AWX (donc le serveur AWX), après le *rebuild*, il faut *delete* à la main le *pod* **awx-0** sur OC afin qu'il utilise le dernier build !



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



# Où en suis-je juste avant de partir en vacances zf200723.1641 ?
Ici un petit carnet de laboratoire afin de me souvenir, quand je vais revenir de vacances, qu'elles étaient les dernières actions que j'ai faites ;-)

- enlevé ma sonde Telegraf dans le container ansible-runner car je n'en n'ai plus besoin maintenant vu qu'elle se trouve dans le container awx-0

- ajouté le monitoring du réseau dans la configuration de Telegraf, maintenant on arrive à voir les échanges réseau lors des déploiement Ansible

- tout à coup, l'inventaire utilisé sur AWX me retourne 1'034 sites au lieu des 340 sites que j'avais pour les tests. Je précise, je n'ai absolument rien touché depuis vendredi passé, dernière fois où j'avais fait tourner des *templates* de tests sur AWX avec différentes configuration multi-pods et multi-forks pour l'optimisation

- pour voir si c'est à cause que ma branche est trop vieille par rapport à wpveritas, synchronisé ma branche de test profiling/awx2 avec la master:
```
git pull https://github.com/epfl-si/wp-ops master
```

- rebuildé le container awx-web afin de pouvoir hériter du nouveau script d'inventaire:
```
./wpsible -t awx
```

- du coup, au lieu qu'Ansible ne tourne que sur le playbook AWX il tourne aussi sur les 340 sites de test, bien entendu avec un *skiped* comme erreur sur les 340 sites !

- je décide donc d'arrêter les frais pour l'instant et de me préparer à partir en vacances. Je reprendrai tout cela à tête reposée à partir de la 2e semaine d'août ;-)


