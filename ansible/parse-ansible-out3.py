#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible dans ce project
# version conventionnelle plus simple que la version parse-ansible-out.py
# nouvelle version par rapport à parse-ansible-out2.py où ici je ne tiens compte que des *Task* !
# sources: https://janakiev.com/blog/python-shell-commands/

version = "parse-ansible-out3.py  zf200130.1112 "

"""
ATTENTION: il faut installer les plugins pour le profilage de Ansible AVANT:
https://janikvonrotz.ch/2018/03/07/profiling-ansible-roles-and-tasks/
https://docs.ansible.com/ansible/latest/plugins/callback/profile_tasks.html

génération du fichier logs
oc login https://xxx.yyy.zzz (à prendre dans l'interface WEB d'OKD)
# le test cours
./wpsible -vvv -l about_00 2>&1 |tee ansible.log
# le test long
./wpsible -vvv -l about_03 2>&1 |tee ansible.log
# le test plus court
./wpsible -vvv -l about_001 2>&1 |tee ansible_first.191220.0847.log
./wpsible -vvv -l about_001 2>&1 |tee ansible_second.191220.0847.log

usage:
cd ./wp-ops/ansible
. parser/bin/activate
reset
./parse-ansible-out3.py

Dans un browser
http://noc-tst.idev-fsd.ml:9092/

Pour mettre à zéro la 'table' dans InfluxDB
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=DROP MEASUREMENT \"ansible_logs3\""
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
"""


import datetime, os

def zget_unix_time(zdate):
#    date_time_obj = datetime.datetime.strptime(zdate, '%Y-%m-%d %H:%M:%S.%f')
    zdate_time_obj = zdate
    zdate_time_obj_1970 = datetime.datetime.strptime("1970-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
    zdate_time_nano_sec = ((zdate_time_obj - zdate_time_obj_1970).total_seconds())*1000000000
    return zdate_time_nano_sec


if (__name__ == "__main__"):
    print("\n" + version + "\n")
    zdebug = False
    zdebug2 = False
    zprint_curl = False
    zsend_grafana = True

    zfile = open("ansible_xfois3.log", "r")
    i = 0

    ztask_time = ""
    ztask_time_obj = 0
    ztask_time_0_obj = 0
    zclock = ""
    zclock_obj = 0
    zclock_0_obj = 0
    zduration = ""

    ztask_line_1 = 0
    ztask_name_1 = ""
    ztask_path_1 = ""
    ztask_time_1_obj = 0
    ztask_duration_1_obj = 0

    ztask_line_2 = 0
    ztask_name_2 = ""
    ztask_path_2 = ""
    ztask_time_2_obj = 0
#    ztask_duration_2_obj = 0      pas besoin !

    while True:
        zline = zfile.readline()
        i = i + 1

        a = 'TASK ['
        if zline[0:len(a)] == a :

# Récupération du nom de la Task
            if zline.find(" : ") != -1 :
                ztask_name_2 = zline[zline.find(" : ")+3:zline.find("] *")]
            else:
                ztask_name_2 = zline[len(a):zline.find("]")]
            ztask_line_2 = i
            if zdebug2 : print(str(i) + " ztask_name_2: [" + ztask_name_2 + "]")

# On passe à la ligne suivante
            zline = zfile.readline()
            i = i + 1

# Récupération du path de la Task
            zpath = "/home/ubuntu/wp-ops/ansible/roles/wordpress-instance/tasks/"
            ztask_path_2 = zline[zline.find(zpath)+len(zpath):-1]
            if zdebug2 : print(str(i) + " ztask_path_2: [" + ztask_path_2 + "]")

# On passe à la ligne suivante
            zline = zfile.readline()
            i = i + 1

# récupération de la base de temps (clock, durée totale)
            p1 = zline.find("   ")
            while zline[p1:p1+1] == " "    :
                p1 = p1 + 1
            zclock = zline[p1:zline.find(" **")]
            if zdebug2 : print(str(i) + " zclock: [" + zclock + "]")
            zclock_obj = datetime.datetime.strptime(zclock, '%H:%M:%S.%f')
            if zdebug2 : print(str(i) + " zclock_obj: [" + str(zclock_obj) + "]")

            if zclock_0_obj == 0 :
                zclock_0_obj = zclock_obj
            if zdebug2 : print(str(i) + " zclock_0_obj: [" + str(zclock_0_obj) + "]")

# récupération de l'heure précise de la Task
            ztask_time = zline[zline.find(" ")+1:zline.find(" +")]
            if zdebug2 : print(str(i) + " ztask_time: [" + ztask_time + "]")
            ztask_time_obj = datetime.datetime.strptime(ztask_time, '%d %B %Y %H:%M:%S')
            if zdebug2 : print(str(i) + " ztask_time_obj: [" + str(ztask_time_obj) + "]")

            if ztask_time_0_obj == 0 :
                ztask_time_0_obj = ztask_time_obj
            if zdebug2 : print(str(i) + " ztask_time_0_obj: [" + str(ztask_time_0_obj) + "]")

            ztask_time_2_obj = ztask_time_0_obj + (zclock_obj - zclock_0_obj)
            if zdebug2 : print(str(i) + " ztask_time_2_obj: [" + str(ztask_time_2_obj) + "]")

# récupération de la durée de la Task
            zduration = zline[zline.find(" (")+2:zline.find(") ")]
            if zdebug2 : print(str(i) + " zduration: [" + zduration + "]")
            ztask_duration_1_obj = datetime.datetime.strptime(zduration, '%H:%M:%S.%f')
            if zdebug2 : print(str(i) + " ztask_duration_1_obj: [" + str(ztask_duration_1_obj) + "]")

# On affiche le résultat de la Task
            if zdebug : print(str(ztask_line_1) + " ztask_name_1: [" + ztask_name_1 + "]")
            if zdebug : print(str(ztask_line_1) + " ztask_path_1: [" + ztask_path_1 + "]")
            if zdebug : print(str(ztask_line_1) + " ztask_time_1_obj: [" + str(ztask_time_1_obj) + "]")
            if zdebug : print(str(ztask_line_1) + " ztask_duration_1_obj: [" + str(ztask_duration_1_obj) + "]")

            if ztask_name_1 != "" :
                print(str(ztask_line_1) + " la tâche: //" + ztask_name_1 + "// avec l'action: //" + ztask_path_1 + "// démarre à " + str(ztask_time_1_obj) + ", durée: " + str(ztask_duration_1_obj))

                ztable = "ansible_logs3"
                ztask_name = ztask_name_1.replace(" ","_") + "_" +str(ztask_line_1)
                ztask_path = ztask_path_1.replace(" ","_")
                ztask_path = ztask_path.replace(":","_")
                ztask_path = ztask_path.replace(".","_")

                ztask_unxi_time = zget_unix_time(ztask_time_1_obj)

                zdate_time_obj_1900 = datetime.datetime.strptime("1900-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
                ztask_duration = (ztask_duration_1_obj - zdate_time_obj_1900).total_seconds()

                zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable + ',action=' + ztask_path + ',task=' + ztask_name + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unxi_time) + '"'
                if zprint_curl :print(zcmd)

                if zsend_grafana == True  :
                    zerr = os.system(zcmd)
                    if zerr != 0 :
                        print(zerr)




# On tourne le 'barillet' de la Task !
            ztask_name_1 = ztask_name_2
            ztask_path_1 = ztask_path_2
            ztask_time_1_obj = ztask_time_2_obj
            ztask_line_1 = ztask_line_2






        if zline == "" :
            break

    zfile.close()



"""
ATOM IDE terminal debug zone
ssh-add -l
ssh-add
ssh-add -l
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
ssh -A -o SendEnv="GIT*, dbflux*" ubuntu@localhost -p 52222
cd wp-ops/ansible/

sur la console terminal de OKD de mgmt(ATTENTION bien vérifier être dans wwp-int):
cd /srv/www/www-wwp-int.128.178.222.83.nip.io/htdocs/
rm -rf about

rm ansible_xfois1.log ansible_xfois2.log ansible_xfois3.log
./wpsible -vvv -l about_000 2>&1 |tee ansible_xfois1.log
./wpsible -vvv -l about_000 2>&1 |tee ansible_xfois2.log
./wpsible -vvvv -l about_000 2>&1 |tee ansible_xfois3.log
ls -alrt

rm ansible_xfois1.log ansible_xfois2.log ansible_xfois3.log
./wpsible -vvv -l about_001 2>&1 |tee ansible_xfois1.log
./wpsible -vvv -l about_001 2>&1 |tee ansible_xfois2.log
./wpsible -vvvv -l about_001 2>&1 |tee ansible_xfois3.log
ls -alrt

rm ansible_xfois1.log ansible_xfois2.log ansible_xfois3.log
./wpsible -vvv -l about_03 2>&1 |tee ansible_xfois1.log
./wpsible -vvv -l about_03 2>&1 |tee ansible_xfois2.log
./wpsible -vvvv -l about_03 2>&1 |tee ansible_xfois3.log
ls -alrt

rm t1
./parse-ansible-out2.py
ls -alrt
cat t1

reset
export ztable="ansible_logs3"
export zaction="bobo_bubu"
export ztask="titi_tata"
export t1=$(date +%s%N)
echo $t1
export t2=$(date +%s%N)
echo $t2
export t21=$(echo "($t2 - $t1)/1000000000" | bc -l)
echo $t21

echo "curl -i -XPOST \"$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user\"  --data-binary \"$ztable,action=$zaction,task=$ztask duration=$t21 $t1\""

curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "$ztable,action=$zaction,task=$ztask duration=$t21 $t1"



python
import os
i=12
zcmd = 'echo "' + str(i) + '" >> toto.txt'
print(zcmd)
os.system(zcmd)



python
import datetime, os
zdate="22 January 2020  17:07:58"
date_time_obj = datetime.datetime.strptime(zdate, '%d %B %Y %H:%M:%S')
print(date_time_obj)
date_time_obj = datetime.datetime.strptime(zdate, '%Y-%m-%d %H:%M:%S.%f')

"""
