# ATTENTION, ceci est ma documentation provisoire, c'est ce qui se trouve dans ma tête en ce moment !

zf191002.1541

## Buts
wp-ops sert à restaurer ou déployer une infra Wordpress de l'EPFL sur Openshift via les commandes oc. Puis en vérifiant l'état via OKD, l'interface WEB de Openshift.

## Problématiques


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
oc rollout latest dc/mgmt
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
Après nous pouvons déployer les différentes instance de Wordpress à partir des sauvegardes de la prod:

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


#### Comment prendre les dernières images docker sur le dépôt de l'EPFL
On ne prend qu'une fois les images de Docker de prod. Si on veut la mettre à jour, il faut *tagger* les images de wwp-int avec les dernières images de l'infra de prod avec:
```
oc tag wwp-test/mgmt:latest wwp-int/mgmt:prod
oc tag wwp-test/httpd:latest wwp-int/httpd:prod
```


#### Comment remettre à zéro totalement l'infra oc wwp-int ?
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

Puis se connecter dans le pod mgmt
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











.
