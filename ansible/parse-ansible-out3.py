#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible (reclog) dans ce project
# version qui calcul la durée de chaque Task !
# sources: https://janakiev.com/blog/python-shell-commands/
# sources: https://github.com/zuzu59/reclog

import signal
import sys
import os
import datetime

version = "parse-ansible-out3.py  zf200901.1830 "

"""
ATTENTION: il ne faut pas oublier, avant de lancer la *petite fusée* d'effacer le fichier de log de reclog !
rm /Users/zuzu/dev-zf/reclog/file.log

génération du fichier logs:
Le faire avec la petite fusée du template dans l'interface WEB de AWX !

usage:
cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_x_sites_y_forks_z_pods.txt

reset
./parse-ansible-out3.py awx_logs_10_sites_5_forks_1_pods.txt


Puis voir le résultat dans un browser
http://noc-tst.idev-fsd.ml:9092/


Pour mettre à zéro la 'table' dans InfluxDB
export ztable="awx_logs1"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=DROP MEASUREMENT $ztable"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
"""


# True False
zverbose_v = True
zverbose_vv = True
zprint_curl = True
zsend_grafana = False

db_logs = {}
ztask_number = 0        # le zéro est important car on l'utilise pour savoir si on est au début du dictionnaire !
ztask_id = 0
ztask_site_number = 0
ztask_site_id = 0
ztask_line = 0
ztask_name = ""
ztask_path = ""
ztask_site = ""
ztask_time = ""
ztask_duration = 0

ztask_time_1 = ""
ztask_time_obj_1 = ""
ztask_unix_time_1 = 0

ztask_time_2 = ""
ztask_time_obj_2 = ""
ztask_unix_time_2 = 0

# ALT+CMD+F bascule du code au terminal

# Structure du dictionnaire
# index: 1
#     task_name: toto1
#     task_path: tutu1
#     index: 1
#         site_name: tata1
#         time_start: 123
#         time_end: 234
#         time_duree: 12
#     index: 2
#         site_name: tata2
#         time_start: 345
#         time_end: 456
#         time_duree: 23
# index: 2
#     task_name: toto2
#     task_path: tutu2
#     index: 1
#         site_name: tata1
#         time_start: 123
#         time_end: 234
#         time_duree: 12
#     index: 2
#         site_name: tata2
#         time_start: 345
#         time_end: 456


def signal_handler(signal, frame):
    print("oups il y a eu un CTRL-C !")
    quit()
    # sys.exit(0)
  
def zget_unix_time(zdate):
    #    date_time_obj = datetime.datetime.strptime(zdate, '%Y-%m-%d %H:%M:%S.%f')
    zdate_time_obj = zdate
    if zverbose_vv: print("zdate_time_obj: [" + str(zdate_time_obj) + "]")
    zdate_time_1970_obj = datetime.datetime.strptime(
        "1970-01-01 01:00:00", '%Y-%m-%d %H:%M:%S')  # Astuce pour faire UTC-1 à cause de Grafana !
    if zverbose_vv: print("zdate_time_1970_obj: [" + str(zdate_time_1970_obj) + "]")
    zdate_time_unix_obj = (zdate_time_obj - zdate_time_1970_obj)
    if zverbose_vv: print("zdate_time_unix_obj: [" + str(zdate_time_unix_obj) + "]")
    return zdate_time_unix_obj


if (__name__ == "__main__"):
    print("\n" + version + "\n")

    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) == 1:
        print("Usage: ./parse-ansible-out3.py fichier_log_a_parser\n\n")
        sys.exit()

    zfile = open(sys.argv[1], "r")
    i = 1

    # On parse le fichier de logs
    while True:
        zline = zfile.readline()
        if zverbose_vv: print("nouvelle ligne: " + str(i) + " " + zline[:-1])

        # Est-ce une ligne de Task ?
        if zline.find(': TASK:') != -1:            
            if zverbose_vv: print("coucou c'est une task")
            
            # Récupération du task_site
            zstr_find1 = 'by zuzu, '
            p1 = zline.find(zstr_find1)
            zstr_find2 = ': TASK:'            
            p2 = zline.find(zstr_find2, p1)
            ztask_site = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_site: [" + ztask_site + "]")
            
            # Récupération du task_path
            zstr_find1 = ': TASK: '
            p1 = zline.find(zstr_find1)
            zstr_find2 = ' : '            
            p2 = zline.find(zstr_find2, p1)
            ztask_path = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_path: [" + ztask_path + "]")

            # Récupération du task_name
            zstr_find1 = ' : '
            p1 = zline.find(zstr_find1)
            zstr_find2 = ' at 2020'            
            p2 = zline.find(zstr_find2, p1)
            ztask_name = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_name: [" + ztask_name + "]")
            
            # Récupération du ztask_time start ou end
            zstr_find1 = ' at '
            p1 = zline.find(zstr_find1)
            # zstr_find2 = ''            
            # p2 = zline.find(zstr_find2, p1)
            p2 = -1
            ztask_time = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_time: [" + ztask_time + "]")
            
            
            
            # Est-ce un start ?
            if zline.find('log start') != -1:
                if zverbose_vv: print("c'est un start")
                if zverbose_vv: print("ztask_number :" + str(ztask_number))

                # Test si le dictionnaire est vide ?
                if ztask_number == 0:
                    if zverbose_vv: print("le dictionnaire est vide, on crée la première tâche")
                    ztask_number = 1
                    db_logs[ztask_number] = {}
                    db_logs[ztask_number]["ztask_name"] = ztask_name
                    db_logs[ztask_number]["ztask_path"] = ztask_path
                    print(db_logs)
                    
                # On cherche où se trouve la tâche dans le dictionnaire
                ztask_id = 0
                for j in range(1, ztask_number+1):
                    print("j: " + str(i))
                    if db_logs[j]["ztask_path"] == ztask_path and db_logs[j]["ztask_name"] == ztask_name:
                        ztask_id = j
                        if zverbose_vv: print("ztask_id 1740:" + str(ztask_id))
                        break
                # Avons-nous trouvé la tâche dans le dictionnaire ?
                if ztask_id == 0:
                    if zverbose_vv: print("la tâche n'existe pas encore, on la crée")
                    ztask_number = ztask_number + 1
                    ztask_id = ztask_number
                    if zverbose_vv: print("ztask_id 1739:" + str(ztask_id))

                    db_logs[ztask_id] = {}
                    db_logs[ztask_id]["ztask_name"] = ztask_name
                    db_logs[ztask_id]["ztask_path"] = ztask_path
                
                # chercher l'index du site dans le dictionnaire
                ztask_site_number = len(db_logs[1]) - 2
                ztask_site_number = ztask_site_number + 1
                if zverbose_vv: print("ztask_site_number:" + str(ztask_site_number))

                # On crée un nouveau site et écrit le task_time_start
                db_logs[ztask_number][ztask_site_number] = {}
                db_logs[ztask_number][ztask_site_number]["ztask_site_name"] = ztask_site
                db_logs[ztask_number][ztask_site_number]["ztask_time_start"] = ztask_time

                
            # Récupération du ztask_time_end
            if zline.find('log end') != -1:
                
                print(db_logs)            
                exit()
                
                if zverbose_vv: print("c'est un end")
                if zverbose_vv: print("ztask_number :" + str(ztask_number))

                if zverbose_vv: print("on cherche elle se trouve")
                ztask_id = 0
                for j in range(1, ztask_number):
                    if db_logs[j]["ztask_path"] == ztask_path and db_logs[j]["ztask_name"] == ztask_name:
                        ztask_id = j
                        if zverbose_vv: print("ztask_id :" + str(ztask_id))
                        break
                db_logs[ztask_id]["zsite_name"][ztask_site].update({"ztask_time_end": ztask_time})
            
                
            
            

        print("")
        i = i + 1
        # On évite la boucle infinie ;-)
        if i > 20:
            quit()

    zfile.close()


    # Calcul les durations pour chaque sites
    for i in range(1, ztask_number):
        if zverbose_vv: print(str(i))

        for j in db_logs[i]["zsite_name"]:
            if zverbose_vv: print(j + ": " + db_logs[i]["zsite_name"][j]["ztask_time"])

            ztask_time_1 = db_logs[i]["zsite_name"][j]["ztask_time"][0:-3]
            ztask_time_obj_1 = datetime.datetime.strptime(ztask_time_1, '%Y-%m-%d %H:%M:%S.%f')
            ztask_unix_time_1 = zget_unix_time(ztask_time_obj_1).total_seconds()
            if zverbose_vv: print("ztask_unix_time_1: " + str(ztask_unix_time_1))

            ztask_time_2 = db_logs[i + 1]["zsite_name"][j]["ztask_time"][0:-3]
            ztask_time_obj_2 = datetime.datetime.strptime(ztask_time_2, '%Y-%m-%d %H:%M:%S.%f')
            ztask_unix_time_2 = zget_unix_time(ztask_time_obj_2).total_seconds()
            if zverbose_vv: print("ztask_unix_time_2: " + str(ztask_unix_time_2))

            ztask_duration = ztask_unix_time_2 - ztask_unix_time_1
            if zverbose_vv: print("Durée: " + str(ztask_duration))
            
            db_logs[i]["zsite_name"][j].update({"ztask_duration": ztask_duration})

            if zverbose_v: print("..................................................")
            # print(str(db_logs[ztask_number]))
            if zverbose_v: print("Task number: " + str(i))
            if zverbose_v: print("Task line: " + str(db_logs[i]["zsite_name"][j]["ztask_line"]))
            if zverbose_v: print("Task name: " + db_logs[i]["ztask_name"])
            if zverbose_v: print("Path path: " + db_logs[i]["ztask_path"])
            if zverbose_v: print("Site name: " + j)
            if zverbose_v: print("Timestamp: " + db_logs[i]["zsite_name"][j]["ztask_time"])
            if zverbose_v: print("Duration: " + str(db_logs[i]["zsite_name"][j]["ztask_duration"]))
            if zverbose_v: print("..................................................")

            
            ztable = "awx_logs1"
            ztask_name_1 = db_logs[i]["ztask_name"]
            ztask_line_1 = db_logs[i]["zsite_name"][j]["ztask_line"]
            ztask_path_1 = db_logs[i]["ztask_path"]
            ztask_site_1 = j
            
            ztask_name = ztask_name_1.replace(" ", "_") + "_" + str(ztask_line_1)
            ztask_name = ztask_name_1.replace(" ", "_")
            ztask_path = ztask_path_1.replace(" ", "_")
            ztask_path = ztask_path.replace(":", "_")
            ztask_path = ztask_path.replace(".", "_")
            ztask_site = ztask_site_1
            
            ztask_time_1 = db_logs[i]["zsite_name"][j]["ztask_time"][0:-3]
            ztask_time_obj_1 = datetime.datetime.strptime(ztask_time_1, '%Y-%m-%d %H:%M:%S.%f')
            ztask_unix_time_1 = zget_unix_time(ztask_time_obj_1).total_seconds()
            ztask_unix_time_nano = ztask_unix_time_1 * 1000000000
            
            ztask_duration = db_logs[i]["zsite_name"][j]["ztask_duration"]

            # zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable + ',action=' + ztask_path + ',task=' + ztask_name + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'

            zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable
            # zcmd = zcmd + ',path=' + ztask_path + ',task=' + ztask_name + ',site=' + ztask_site + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'
            zcmd = zcmd + ',task=' + ztask_name + '_/_' + ztask_path + ',site=' + ztask_site + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'



            if zprint_curl: print(zcmd)
            
            if zsend_grafana:
                zerr = os.system(zcmd)
                if zerr != 0:
                    print(zerr)






