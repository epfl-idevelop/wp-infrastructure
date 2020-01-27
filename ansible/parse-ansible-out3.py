#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible dans ce project
# version conventionnelle plus simple que la version parse-ansible-out.py
# nouvelle version par rapport à parse-ansible-out2.py où ici je ne tiens compte que des *Task* !
# sources: https://janakiev.com/blog/python-shell-commands/

version = "parse-ansible-out3.py  zf200127.1456 "

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
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=DROP MEASUREMENT \"ansible_logs2\""
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"



"""


import datetime, os

def zget_time(zdate):
    #print("xxxxxxxxxxx" + zdate + "yyyyyyyyyy")
    date_time_obj = datetime.datetime.strptime(zdate, '%Y-%m-%d %H:%M:%S.%f')
    date_time_obj_1970 = datetime.datetime.strptime("1970-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
    date_time_nano_sec = ((date_time_obj - date_time_obj_1970).total_seconds())*1000000000
    #print("%18.0f\n" % (date_time_nano_sec))
    return date_time_nano_sec


if (__name__ == "__main__"):
    print("\n" + version + "\n")
    zdebug = True
    zprint_curl = False

    zfile = open("ansible_xfois3.log", "r")
    #zfile = open("ansible_first.191220.0847.log", "r")
    #zfile = open("ansible_about_first.191217.1652.log", "r")
    #zfile = open("ansible_about_second.191217.1703.log", "r")
    i = 0
    time_start = 0
    while True:
        zline = zfile.readline()
        i = i + 1


        a = 'TASK ['
        if zline[0:len(a)] == a :
            #print(i, zline)
            if zline.find(" : ") != -1 :
                ztask = zline[zline.find(" : ")+3:zline.find("] *")]
            else:
                ztask = zline[len(a):zline.find("]")]
            task_num_line = i
            if zdebug : print(str(i) + " task: [" + ztask + "]")

            zline = zfile.readline()
            i = i + 1

            ztask_path = zline[zline.find(": ")+2:zline.find(":",12)]
            if zdebug : print(str(i) + " task_path: [" + ztask_path + "]")

            zline = zfile.readline()
            i = i + 1

            ztask_time = zline[zline.find(" ")+1:zline.find(" +")]
            if zdebug : print(str(i) + " task_time: [" + ztask_time + "]")

            ztask_time_t2t1 = zline[zline.find(" (")+2:zline.find(") ")]
            if zdebug : print(str(i) + " task_time_t2t1: [" + ztask_time_t2t1 + "]")






        a = '}zz donc ne le trouve JAMAIS !'
        if zline[0:len(a)] == a :
            if time_start > 0 :
                #print(i, zline)
                #print(".......................end task...")
                time_delta = (time_end - time_start)/1000000000
                print(str(start_num_line) + " la tâche: //" +ztask + "// avec l'action: //" + zaction + "// sur l'instance //" + zinstance + "// démarre à " + date_start + " (%0.0f" % (time_start) + "), durée: " + str(time_delta))
#                zerr = os.system('echo "' + str(i) + '" >> t1')

                ztable = "ansible_logs2"
                zaction = zaction.replace(" ","_")
                zinstance = zinstance.replace(" ","_")
                ztask = ztask.replace(" ","_")

                zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable + ',instance=' + zinstance + ',action=' + zaction + ',task=' + ztask + ' time_duration=' + str(time_delta) + ' ' + '%0.0f' % (time_start) + '"'
                if zprint_curl :print(zcmd)

                if zdebug == False  :
                    zerr = os.system(zcmd)
                    if zerr != 0 :
                        print(zerr)

                time_start = 0
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

export ztable="ansible_logs"
export zinstance="bobo_bubu"
export ztask="titi_tata"
export ztask="zozo_zuzu"
export t1=$(date +%s%N)
echo $t1
export t2=$(date +%s%N)
echo $t2
export t21=$(echo "($t2 - $t1)/1000000000" | bc -l)
echo $t21

curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "$ztable,instance=$zinstance,task=$ztask time_duration=$t21 $t1"



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
