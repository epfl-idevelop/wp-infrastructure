#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible dans ce project
# version conventionnelle plus simple que la version parse-ansible-out.py
#
# sources: https://janakiev.com/blog/python-shell-commands/

version = "parse-ansible-out2.py  zf191212.1145 "

"""
génération du fichier logs
./wpsible -vvv -l about_00 2>&1 |tee ansible.log

usage:
cd ./wp-ops/ansible
. parser/bin/activate
./parse-ansible-out2.py
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
    #zfile = open("ansible.log.191010", "r")
    zfile = open("ansible.log", "r")
    i = 0
    time_start = 0
    while True:
        zline = zfile.readline()
        i = i + 1

        a = '"start": "'
        if zline.find(a) != -1 :
            #print(i, zline)
            zdate = zline[zline.find('": "')+4:zline.find('",')]
            date_start = zdate
            time_start = zget_time(zdate)
            start_num_line = i
            #print("%18.0f\n" % (time_start))

        a = '"end": "'
        if zline.find(a) != -1 :
            #print(i, zline)
            zdate = zline[zline.find('": "')+4:zline.find('",')]
            time_end = zget_time(zdate)
            #print("%18.0f\n" % (time_end))



        a = 'TASK ['
        if zline[0:len(a)] == a :
            #print(i, zline)
            if zline.find(" : ") != -1 :
                ztask = zline[zline.find(" : ")+3:zline.find("] *")]
            else:
                ztask = zline[len(a):zline.find("]")]
            task_num_line = i
            print(str(i) + " task: [" + ztask + "]")

        a = 'ok: ['
        if zline[0:len(a)] == a :
            #print(i, zline)
            zaction = zline[0:len(a)-3]
            zinstance = zline[len(a):zline.find("]")]
            print(str(i) + " action: " + zaction + ", instance" + zinstance)

        a = 'changed: ['
        if zline[0:len(a)] == a :
            #print(i, zline)
            zaction = zline[0:len(a)-3]
            zinstance = zline[len(a):zline.find("]")]
            print(str(i) + " action: " + zaction + ", instance" + zinstance)


        a = 'fatal: ['
        if zline[0:len(a)] == a :
            #print(i, zline[0:len(a)])
            zaction = zline[0:len(a)-3]
            zinstance = zline[len(a):zline.find("]")]
            print(str(i) + " action: " + zaction + ", instance" + zinstance)




        a = '}'
        if zline[0:len(a)] == a :
            if time_start > 0 :
                #print(i, zline)
                #print(".......................end task...")
                time_delta = (time_end - time_start)/1000000000
                print(str(start_num_line) + " la tâche: [" +ztask + "] avec l'action: [" + zaction + "] sur l'instance [" + zinstance + "] démarre à " + date_start + " (%0.0f" % (time_start) + "), durée: " + str(time_delta))
#                zerr = os.system('echo "' + str(i) + '" >> t1')

                ztable = "ansible_logs"
                zaction = zaction.replace(" ","_")
                zinstance = zinstance.replace(" ","_")
                ztask = ztask.replace(" ","_")

                zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable + ',instance=' + zinstance + ',action=' + zaction + ',task=' + ztask + ' time_duration=' + str(time_delta) + ' ' + '%0.0f' % (time_start) + '"'
                print(zcmd)

                zerr = os.system(zcmd)
                if zerr != 0 :
                    print(zerr)

                time_start = 0
        if zline == "":
            break

    zfile.close()



"""
ATOM IDE terminal debug zone

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
"""
