# ATTENTION, ceci est ma documentation provisoire, c'est ce qui se trouve dans ma tête en ce moment !

zf191219.1421

## Buts
*wp-ops* sert à restaurer ou déployer une infra Wordpress de l'EPFL sur Openshift via les commandes oc. Puis en vérifiant l'état via OKD, l'interface WEB de Openshift.

## Problématiques
Si on déploie une *infra* à la main, on ne sera jamais certain de ce que l'on a dû *faire* pour que cela fonctionne et il sera alors impossible de la *restaurer* en cas de problèmes.
Il est préférable de la déployer à partir d'un *code de déploiement*, c'est une *Infrastructure as Code*:

https://fr.wikipedia.org/wiki/Infrastructure_as_Code

### Pourquoi utiliser Ansible plutôt qu'un script en bash ?
Ansible nous permet à tout moment de *vérifier* si ce que l'on a en *prod correspond* à ce que l'on a en *code*. Il *connait* en tout temps l'état et le *maintient* par rapport au code !
Il permet aussi de hautement paralléliser les taches.



## Moyens


### Prérequis
*wpsible* va tourner sur sa machine, il faudra donc installer sur sa machine:

#### Openshift client
Openshift client va nous permettre de communiquer avec l'infra Openshift en lignes de commandes, on peut utiliser ce petit script pour l'installer plus facilement:
```
./utils/install_oc.sh
```

#### Ansible
Ansible va nous permettre d'automatiser l'installation de l'infra de tests.<br>
ATTENTION aux différentes versions de Python et surtout de modes d'installation de Ansible !<br>
On peut utiliser ce petit script pour l'installer plus facilement:
```
./utils/install_ansible.sh
```
Ce script installe aussi différents outils et le plugin Ansible pour Openshift !

#### Keybase
Keybase nous permet de partager les secrets. On l'installe depuis ici:
```
https://keybase.io/download
```
ATTENTION:<br>
Vous devez vous trouver dans le team de Keybase suivant:
```
/keybase/team/epfl_wwp_blue
```



### Utilisation de wpsible

#### Connexion et choix du bon projet sur Openshift
https://pub-os-exopge.epfl.ch/console/project/wwp-int/overview

Il faut en premier se connecter sur OC:

![Image](https://raw.githubusercontent.com/epfl-idevelop/wp-ops/feature/wp-int/img/oc_login.gif)

et surtout bien *choisir* le project **wwp-int** avec:
```
oc project wwp-int
oc projects
```

![Image](https://raw.githubusercontent.com/epfl-idevelop/wp-ops/feature/wp-int/img/oc_project_wwp-int.gif)



#### Récupération du bon dépôt github pour les tests ;-)
Faire:
```
git clone https://github.com/epfl-idevelop/wp-ops.git
cd wp-ops
```
Après il faut récupérer toutes les branches remote en local avec:
```
for b in `git branch -r | grep -v -- "->"`; do git branch --track ${b##origin/} $b; done
```
Enfin se positionner dans la branche *feature/wwp-int* avec:
```
git checkout feature/wp-int
```


#### Déploiement du pod mgmt
Pour pouvoir récupérer les sauvegardes des sites Wordpress de la prod, il nous faut un *pod* de management qui aura une connexion *read only* sur le NAS (NFS) des sauvegarde de la prod.
```
cd wp-ops/ansible
./wpsible -l wp-blue
```



#### Déploiement des pods serveur Wordpress
Après il faut déployer les pods *serveurs* pour Wordpress. Actuellement nous en n'utilisons que deux:<br>

ceci pour *httpd-www*:
```
./wpsible -l httpd-www
```

ceci pour *httpd-labs*:
```
./wpsible -l httpd-labs
```



#### Déploiement d'une instance Wordpress
Après nous pouvons déployer les différentes instances de Wordpress à partir des sauvegardes de la prod:

Juste pour le site *www*:
```
./wpsible -l _srv_www_www.epfl.ch_htdocs
```

et pour le site *www.epfl.ch/labs/emc*:
```
./wpsible -l _srv_labs_www.epfl.ch_htdocs_labs_emc
```

Pour les sites *www* et sous site *about*:
```
./wpsible -l _srv_www_www.epfl.ch_htdocs,_srv_www_www.epfl.ch_htdocs_about
```


#### Déploiement d'un groupe d'instances Wordpress
On peut déployer un *groupe* de tests d'instances Wordpress avec:
```
./wpsible -l gutenberg_02
```

Les groupes de *tests* se trouvent dans ce fichier d'inventaire
```
wp-ops/ansible/inventory/wp-int/tests_instances
```

Temps passé pour *certains* groupes d'instances Wordpress (21x instances)
* **firs time**<br>
./wpsible -l gutenberg_1, **env 33 minutes**

* **second time**<br>
./wpsible -l gutenberg_1, **env 7 minutes**



#### Comment trouver l'url des instances déployées ?
Il faut aller depuis l'interface WEB *OKD* de Openshift pour *rechercher* les URL en fonction des *pods*.<br>
ATTENTION: chaque *pods* a son URL, et pour le pod *labs*, il faut compléter à la main l'url avec le laboratoire souhaité:

![Image](https://raw.githubusercontent.com/epfl-idevelop/wp-ops/feature/wp-int/img/oc_get_url.gif)



#### Comment consulter l'inventaire des instances ?
ATTENTION, il faut que le *pod mgmt* tourne pour que l'inventaire fonctionne !
```
cd wp-ops/ansible
ansible-inventory -i inventory/wp-int/wordpress-instances --graph
ansible-inventory -i inventory/wp-int/wordpress-instances --list
```

On peut aussi faire:
```
./inventory/wp-int/wordpress-instances
```


#### Comment passer de wordpress 4 à 5
ATTENTION, sûrement plus valable au 2 octobre 2019 !
```
./wpsible -l _srv_labs_www.epfl.ch_htdocs_labs_la -t config,symlink,plugins,themes -e '{"wp_destructive": {"_srv_labs_www.epfl.ch_htdocs_labs_la": ["code", "config"]}, "wp_ensure_symlink_version": "5.2"}'
```


#### Comment prendre les dernières images Docker sur le dépôt de l'EPFL
On ne prend qu'une fois les images de Docker de *prod* pour la mettre dans notre infra *wwp-int*. Si on veut la mettre à jour, il faut *tagger* les images de *wwp-int* avec les dernières images de l'infra de *prod* avec:
```
oc tag wwp-test/mgmt:latest wwp-int/mgmt:prod
oc tag wwp-test/httpd:latest wwp-int/httpd:prod
```


#### Comment remettre à zéro totalement l'infra wwp-int ?
**ATTENTION c'est dangereux car cela efface VRAIMENT tout !**
Il faut **VRAIMENT** bien vérifier à chaque fois où on se trouve !

Il faut faire en premier un:
```
oc project wwp-int
```

Et bien vérifier que nous sommes dans wwp-int avec:
```
oc projects
```

Puis se connecter dans le pod *mgmt*
```
oc get pod
oc exec podname -it /bin/bash
```
et effacer **/srv/*** avec
```
rm -rf /srv/*
```

Et enfin sortir du *pod* avec un **ctrl+d** et faire:
```
/keybase/team/epfl_wwp_blue/ec/xfer/delete-wp-int.sh
```


## Avoir des information sur les latences de ansible
Ansible fait beaucoup de choses et prend un certain temps. On aimerait bien savoir *se qu'il fait* pendant tout ce temps !
Quelques pistes à creuser:

Giovanni Cangiani, [19.12.19 11:43]
https://docs.ansible.com/ansible/latest/plugins/callback/profile_tasks.html

Giovanni Cangiani, [19.12.19 11:45]
https://janikvonrotz.ch/2018/03/07/profiling-ansible-roles-and-tasks/

Giovanni Cangiani, [19.12.19 11:46]
https://sketchingdev.co.uk/blog/profiling-ansible-playbooks-to-csv.html




## Trucs à zuzu pour mémoire après les vacances 191010.1633 ;-)

```
virtualenv
sudo apt install virtualenv
virtualenv
virtualenv parser
. parser/bin/activate
pip install ipdb
python --version
python parse-ansible-out.py
python parse-ansible-out.pyc
python parse-ansible-out.py
pip install ipython
ipython
python parse-ansible-out.py



Dans console 1:
ssh-add -l
ssh-add
ssh-add -l
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
mkdir ~/mnt/virtualbox1
sshfs -p 52222 ubuntu@localhost:/home/ubuntu ~/mnt/virtualbox1/
atom ~/mnt/virtualbox1/
ssh -A -o SendEnv="GIT*, dbflux*" ubuntu@localhost -p 52222
cd wp-ops/ansible/


Dans console 2
ssh-add -l
ssh-add
ssh-add -l
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
mkdir ~/mnt/noc-tst.idev-fsd.ml/
sshfs -p 22 czufferey@noc-tst.idev-fsd.ml:/home/czufferey ~/mnt/noc-tst.idev-fsd.ml/
atom  ~/mnt/noc-tst.idev-fsd.ml/
ssh -A -o SendEnv="GIT*, dbflux*" czufferey@noc-tst.idev-fsd.ml
cd docker-influxdb-grafana/
./start.sh
Ne pas oublier après d'arrêter le binz avec:
./stop.sh

Dans un browser
http://noc-tst.idev-fsd.ml:9092/

```


## Trucs à zuzu pour mémoire au retour des vacances de fin d'année 191220.1631 ;-)
Pour avoir plus de détails dans les logs d'Ansible, j'ai installé le plugin https://docs.ansible.com/ansible/latest/plugins/callback/profile_tasks.html selon:
https://janikvonrotz.ch/2018/03/07/profiling-ansible-roles-and-tasks/
mais en fait il tourne le plugin qui se trouve dans:
/usr/local/lib/python3.6/dist-packages/ansible/plugins/callback/profile_tasks.py
au lieu de:
/home/ubuntu/wp-ops/ansible/callback_plugins/profile_tasks.py
et... il a une erreur quand on demande de ne pas trier le résultat final, j'ai donc commenté la ligne 187 de
/usr/local/lib/python3.6/dist-packages/ansible/plugins/callback/profile_tasks.py
pour ne plus avoir l'erreur !
Mais finalement, ce plugin n'ajoute pas plus de détails dans les logs, je suis toujours aveugle entre les tâches
[Delete fact directory] et [wp evaluation 1]
Bien que j'ai ajouté dans le fichier ansible.cfg la ligne
enable_task_debugger = True

Au retour de vacances je dois comprendre pourquoi dans certaines tâches je n'ai pas les timestamps start et end après chaque tâche sur les instances ?




.
