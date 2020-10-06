# Mes petits trucs à moi pour bien travailler ;-)
#zf201006.0959

<!-- TOC titleSize:2 tabSpaces:2 depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 skip:2 title:1 charForUnorderedList:* -->
## Table of Contents
* [Mon ..., mais c'est si simple pour AWX](#mon--mais-cest-si-simple-pour-awx)
* [Shortcuts pour Atom](#shortcuts-pour-atom)
* [Go go go !](#go-go-go-)
  * [Sur sa machine](#sur-sa-machine)
  * [Sur sa machine dans une console](#sur-sa-machine-dans-une-console)
    * [A faire au début du travail](#a-faire-au-début-du-travail)
    * [ATTENTION, si on a des erreurs de Ansible-Suitcase il faut le régénérer !](#attention-si-on-a-des-erreurs-de-ansible-suitcase-il-faut-le-régénérer-)
    * [Synchronisation de la branche master avec la branche de travail](#synchronisation-de-la-branche-master-avec-la-branche-de-travail)
    * [Accélération des tests du code Ansible](#accélération-des-tests-du-code-ansible)
    * [En travail lancer la petite fusée d'un template dans le GUI de AWX](#en-travail-lancer-la-petite-fusée-dun-template-dans-le-gui-de-awx)
    * [Voir les résultats des logs avec *reclog*](#voir-les-résultats-des-logs-avec-reclog)
    * [En travail, si on veut refaire l'image du Ansible runner ET du container utilisé par AWX](#en-travail-si-on-veut-refaire-limage-du-ansible-runner-et-du-container-utilisé-par-awx)
      * [ATTENTION:](#attention)
  * [Sur Grafana](#sur-grafana)
* [Tests de profilling de wp-cli](#tests-de-profilling-de-wp-cli)
  * [pour les tests en local sur sa machine](#pour-les-tests-en-local-sur-sa-machine)
* [Idées à creuser et astuces](#idées-à-creuser-et-astuces)
  * [Mitogen et pipelining](#mitogen-et-pipelining)
  * [OPcache, cache PHP](#opcache-cache-php)
  * [Manual Ansible Runner (pour ses propres modules, page 22)](#manual-ansible-runner-pour-ses-propres-modules-page-22)
  * [Installer ses propres plugins](#installer-ses-propres-plugins)
  * [ansible.cfg](#ansiblecfg)
  * [debug python pour IntelliJ](#debug-python-pour-intellij)
  * [date & time sous Python](#date--time-sous-python)
  * [savoir qui on est dans un container OC](#savoir-qui-on-est-dans-un-container-oc)
  * [pour voir quels pods tournent sur quels nodes](#pour-voir-quels-pods-tournent-sur-quels-nodes)
  * [voir la PR 324 pour les backups de WWP via awx](#voir-la-pr-324-pour-les-backups-de-wwp-via-awx)
  * [test en python pour obtenir l'heure](#test-en-python-pour-obtenir-lheure)
  * [un mini logger](#un-mini-logger)
  * [comment modifier directement le contenu d'un groupe d'inventaire sur AWX ?](#comment-modifier-directement-le-contenu-dun-groupe-dinventaire-sur-awx-)
  * [essais d'optimisation de AWX avec le pipelining (zf200916.1610)](#essais-doptimisation-de-awx-avec-le-pipelining-zf2009161610)
  * [Calcul de la moyenne, médiane et du 95e percentil en bash ;-)](#calcul-de-la-moyenne-médiane-et-du-95e-percentil-en-bash--)
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
oc login -u czufferey -p $KLM_NOP
oc project wwp-test
oc projects
```


### ATTENTION, si on a des erreurs de Ansible-Suitcase il faut le régénérer !
Simplement en effaçant le fichier:
```
ansible/ansible-deps-cache/.versions
```



### Synchronisation de la branche master avec la branche de travail
Après un certain temps, la branche de travail se *désynchronise* avec la branche master et on peut avoir des effets de bord avec *wp-veritas* par exemple.
On peut très facilement resynchroniser la branche de travail avec la master ainsi:
```
git pull https://github.com/epfl-si/wp-ops master
```

c'est meilleure cette façons à cause des git push -f de certaines personnes
```
git pull --rebase --autostash https://github.com/epfl-si/wp-ops master
```


### Accélération des tests du code Ansible
Quand on *lance* un template sur AWX (icône petite *fusée*), il va normalement *chercher* ses données Ansible sur https://github.com/epfl-si/wp-ops dans la branche *profiling/awx*, cela demande à chaque changement de code Ansible, de faire un *commit* et un *push* de notre *local* sur Github !

On peut y remédier en *trichant* un peu lors du commit:
```
GIT_EDITOR=true git commit -a --amend && git push -f
```
Du coup on gagne beaucoup de temps pour les tests !



### En travail lancer la petite fusée d'un template dans le GUI de AWX
https://awx-poc-vpsi.epfl.ch/#/login



### Voir les résultats des logs avec *reclog*
On peut utiliser *reclog* pour enregistrer les logs de profilage d'Ansible:
https://github.com/zuzu59/reclog

Quand le *reclog* tourne, il ne faut pas oublier, avant de lancer Ansible, d'effacer les anciens logs:
```
rm ../../../dev-zf/reclog/file.log
tail -f ../../../dev-zf/reclog/file.log
```




### En travail, si on veut refaire l'image du Ansible runner ET du container utilisé par AWX
Dans sa console de sa machine
```
./wpsible -t awx
# si c'est juste pour faire un check on peut faire ceci:
./wpsible -t awx --check
```

#### ATTENTION:
**Si on a modifié le code Ansible, il faut *forcer* le rebuild en changeant la date dans le dockerfile du ansible-runner (roles/awx-instance/templates/Dockerfile.wp-ansible-runner) afin que le *patch* puisse s'appliquer !**



## Sur Grafana
http://noc-tst.idev-fsd.ml:9092/

Les credentials pour Grafana sont dans Keybase:
```
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
```


On peut importer le dashboard 928, qui permet déjà de voir une jolie vue
https://grafana.com/grafana/dashboards/928


# Tests de profilling de wp-cli
Le but étant de savoir combien de fois on lance la commande *wp-cli*, commande en PHP très consommateur en ressources, et surtout le temps passé avec.

L'idée est d'installer ma sonde de mesure directement dans le code python du module Ansible qui lance cette commande.

## pour les tests en local sur sa machine
Sur sa machine il faut faire la procédure d'initialisation de l'environnement décrite sous:

[A faire au début du travail](#a-faire-au-début-du-travail)

Puis dans sa console:
```
./wpsible --check -t themes -l test_migration_wp__labs__aqua
./wpsible --check -t plugins -l test_migration_wp__labs__aqua
```












# Idées à creuser et astuces
## Mitogen et pipelining
https://www.toptechskills.com/ansible-tutorials-courses/speed-up-ansible-playbooks-pipelining-mitogen/


## OPcache, cache PHP
https://www.ekino.com/articles/php-comment-configurer-utiliser-et-surveiller-opcache


## Manual Ansible Runner (pour ses propres modules, page 22)
https://ansible-runner.readthedocs.io/_/downloads/en/stable/pdf/
https://ansible-runner.readthedocs.io/en/latest


## Installer ses propres plugins
https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html


## ansible.cfg
https://github.com/ansible/ansible/blob/devel/examples/ansible.cfg


## debug python pour IntelliJ
import sys; sys.path.append("/Users/zuzu/Library/Application Support/JetBrains/IntelliJIdea2020.2/plugins/python/pydevd-pycharm.egg"); import pydevd; pydevd.settrace('localhost', port=12477, stdoutToServer=True, stderrToServer=True)


## date & time sous Python
https://www.programiz.com/python-programming/datetime/current-datetime


## savoir qui on est dans un container OC
oc whoami


## pour voir quels pods tournent sur quels nodes
oc get pods -o wide -n wwp


## voir la PR 324 pour les backups de WWP via awx
https://github.com/epfl-si/wp-ops/pull/324
Je dois faire des tests de sauvegardes de wwp avec awx


## test en python pour obtenir l'heure
from datetime import datetime
print(datetime.now())


## un mini logger
On peut se faire hyper facilement un mini *logger* pour *récupérer* des infos avec:
```
socat TCP4-LISTEN:55514,reuseaddr,fork OPEN:/tmp/toto.log,creat,append
```

Je décide de prendre comme port de logger le 55514, c'est 55'000+514 qui est le port habituel du syslog
https://www.poftut.com/linux-logger-command-usage-tutorial-with-examples/#:~:text=Specify%20Remote%20Syslog%20Server%20Port,by%20providing%20the%20port%20number.


## comment modifier directement le contenu d'un groupe d'inventaire sur AWX ?
https://confluence.epfl.ch:8443/display/SIAC/Ansible+et+Ansible+Tower+-+PRJ0011294


## essais d'optimisation de AWX avec le pipelining (zf200916.1610)
**ATTENTION:** ce n'est PAS persistant aux rebuilds des images awx !
J'ai mis ceci:
```
{
 "HOME": "/var/lib/awx",
 "ANSIBLE_PIPELINING": "True",
 "ANSIBLE_SSH_PIPELINING": "True"
}
```

dans (dans variables d'environnements supplémentaires):
https://awx-poc-vpsi.epfl.ch/#/settings/jobs


## Calcul de la moyenne, médiane et du 95e percentil en bash ;-)
Des fois il est très pratique de pouvoir calculer la moyenne, la médiane et le 95e percentil en bash d'une liste dans un fichier.
(https://stackoverflow.com/questions/47319123/how-to-get-average-median-mean-stats-from-a-file-which-has-numbers-in-first-co)

Moyenne
```
echo 'Moyenne'
cat toto.txt | grep 'zratio_duration_wp_task' | awk '{print $2}' | sort -n | awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }' 
```

Médiane
```
echo 'Médiane'
cat toto.txt | grep 'zratio_duration_wp_task' | awk '{print $2}' | sort -n | awk '{count[NR] = $1;} END {if (NR % 2) {print count[(NR + 1) / 2];} else {print (count[(NR / 2)] + count[(NR / 2) + 1]) / 2.0;}}' 
```


95e percentil
```
echo '95e percentil'
cat toto.txt | grep 'zratio_duration_wp_task' | awk '{print $2}' | sort -n | awk 'BEGIN{c=0} length($0){a[c]=$0;c++}END{p5=(c/100*5); p5=p5%1?int(p5)+1:p5; print a[c-p5-1]}' 
```






