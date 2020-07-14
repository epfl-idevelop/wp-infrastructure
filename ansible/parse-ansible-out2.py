#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible dans ce project
# version qui calcul la durée de chaque Task !
# sources: https://janakiev.com/blog/python-shell-commands/

import signal
import sys
import os
import datetime

version = "parse-ansible-out2.py  zf200714.0957 "

"""
génération du fichier logs:
Le faire avec la petite fusée du template dans l'interface WEB de AWX !

usage:
source /keybase/team/epfl_wwp_blue/influxdb_secrets.sh
source /keybase/private/zuzu59/tequila_zf_secrets.sh
cd /Users/zuzu/dev-vpsi/wp-ops/ansible
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1219/stdout/?format=txt > awx_logs.txt

reset
./parse-ansible-out2.py awx_logs_2_sites_1_pods.txt

Puis voir le résultat dans un browser
http://noc-tst.idev-fsd.ml:9092/


Pour mettre à zéro la 'table' dans InfluxDB
export ztable="ansible_logs3"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=DROP MEASUREMENT $ztable"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
"""


# True False
zverbose_v = True
zverbose_vv = False
zprint_curl = True
zsend_grafana = False

db_logs = {}
ztask_number = 0
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
    i = 0


# ALT+CMD+F bascule du code au terminal

# Structure du dictionnaire
# index: 1
#     task_name: toto1
#     task_path: tutu1
#     site_name: tata1
#             time_start: 123
#             time_duree: 12
#         site_name: tata2
#             time_start: 234
#             time_duree: 23
# index: 2
#     task_name: toto1
#     task_path: tutu1
#         site_name: tata1
#             time_start: 123
#             time_duree: 12
#         site_name: tata2
#             time_start: 234
#             time_duree: 23

    # On parse le fichier de logs
    while True:
        zline = zfile.readline()
        i = i + 1

        # Est-ce une TASK ?
        a = 'TASK ['
        if zline[0:len(a)] == a:

            # Est-ce la Task 'debug' ?
            if zline.find(": debug") != -1:
                if zverbose_vv: print(str(i) + " " + zline)
                ztask_number = ztask_number + 1
                db_logs[ztask_number] = {"zsite_name": {}}

                # On passe à la ligne suivante
                zline = zfile.readline()
                i = i + 1
                if zverbose_vv: print(str(i) + " " + zline)

                # Récupération du path de la Task
                zpath = "/project/ansible/roles/wordpress-instance/tasks/"
                ztask_path = zline[zline.find(zpath) + len(zpath):-1]
                if zverbose_vv: print(str(i) + " ztask_path: [" + ztask_path + "]")
                db_logs[ztask_number].update({"ztask_path": ztask_path})

                while True:
                    # On évite la boucle infinie ;-)
                    if i > 200000000:
                        quit()

                    # On passe à la ligne suivante
                    zline = zfile.readline()
                    i = i + 1
                    if zverbose_vv: print(str(i) + " " + zline)

                    # Est-ce une ligne ok: [site name] ?
                    if zline.find("ok: [") != -1:

                        # Récupération du nom du site
                        ztask_site = zline[1 + zline.find("["):zline.find("]")]
                        if zverbose_vv: print(str(i) + " ztask_site: [" + ztask_site + "]")
                        db_logs[ztask_number]["zsite_name"].update({ztask_site: {}})

                        # On passe à la ligne suivante
                        zline = zfile.readline()
                        i = i + 1
                        if zverbose_vv: print(str(i) + " " + zline)

                        # Est-ce la ligne 'ztime' ?
                        if zline.find("ztime, ") != -1:
                            if zverbose_vv: print("c'est une ligne ztime............")

                            # Récupération de la position dans le logs
                            ztask_line = i
                            db_logs[ztask_number]["zsite_name"][ztask_site].update({"ztask_line": ztask_line})

                            # Récupération du nom de la Task
                            ztask_name = zline[1 + zline.find("/"):zline.find("/", 1 + zline.find("/"))]
                            if zverbose_vv: print(str(i) + " ztask_name: [" + ztask_name + "]")
                            db_logs[ztask_number].update({"ztask_name": ztask_name})

                            # Récupération du time de la Task
                            ztask_time = zline[2 + zline.find("/ "):-2]
                            if zverbose_vv: print(str(i) + " ztask_time: [" + ztask_time + "]")
                            db_logs[ztask_number]["zsite_name"][ztask_site].update({"ztask_time": ztask_time})

                            if zverbose_vv: print("..................................................")
                            # print(str(db_logs[ztask_number]))
                            if zverbose_vv: print("Task number: " + str(ztask_number))
                            if zverbose_vv: print("Task line: " + str(db_logs[ztask_number]["zsite_name"][ztask_site]["ztask_line"]))
                            if zverbose_vv: print("Task name: " + db_logs[ztask_number]["ztask_name"])
                            if zverbose_vv: print("Path path: " + db_logs[ztask_number]["ztask_path"])
                            if zverbose_vv: print("Site name: " + ztask_site)
                            if zverbose_vv: print("Timestamp: " + db_logs[ztask_number]["zsite_name"][ztask_site]["ztask_time"])
                            if zverbose_vv: print("..................................................")

                            # On passe à la ligne suivante
                            zline = zfile.readline()
                            i = i + 1
                            if zverbose_vv: print(str(i) + " " + zline)
                        else:
                            # Ce n'est pas une task debug avec un ztime, on recule donc le pointeur du dictionnaire
                            ztask_number = ztask_number - 1

                    else:
                        break

        if zline == "":
            break

    zfile.close()

    # index: 1
    #     task_name: toto1
    #         task_path: tutu1
    #         site_name: tata1
    #             time_start: 123
    #             time_duree: 12
    #         site_name: tata2
    #             time_start: 234
    #             time_duree: 23
    # index: 2
    #     task_name: toto1
    #         task_path: tutu1
    #         site_name: tata1
    #             time_start: 123
    #             time_duree: 12
    #         site_name: tata2
    #             time_start: 234
    #             time_duree: 23

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
            
            ztask_name = ztask_name_1.replace(" ", "_") + "_" + str(ztask_line_1)
            ztask_path = ztask_path_1.replace(" ", "_")
            ztask_path = ztask_path.replace(":", "_")
            ztask_path = ztask_path.replace(".", "_")
            # 
            ztask_unix_time_nano = db_logs[i]["zsite_name"][j]["ztask_time"]*1000000000

            # zdate_time_obj_1900 = datetime.datetime.strptime("1900-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
            # ztask_duration = db_logs[i]["zsite_name"][j]["ztask_duration"]

            # zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable + ',action=' + ztask_path + ',task=' + ztask_name + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'
            # if zprint_curl: print(zcmd)
            # 
            # if zsend_grafana:
            #     zerr = os.system(zcmd)
            #     if zerr != 0:
            #         print(zerr)






