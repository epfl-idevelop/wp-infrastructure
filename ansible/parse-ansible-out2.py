#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible dans ce project
# version qui calcul la durée de chaque Task !
# sources: https://janakiev.com/blog/python-shell-commands/

import sys
# import os
import datetime
version = "parse-ansible-out2.py  zf200709.1354 "

"""
génération du fichier logs:
Le faire avec la petite fusée du template dans l'interface WEB de AWX !

usage:
source /keybase/team/epfl_wwp_blue/influxdb_secrets.sh
source /keybase/private/zuzu59/tequila_zf_secrets.sh
cd /Users/zuzu/dev-vpsi/wp-ops/ansible
curl https://$ABC_DEF:$KLM_NOP@awx-poc-vpsi.epfl.ch/api/v2/jobs/1219/stdout/?format=txt > awx_logs.txt

reset
./parse-ansible-out1.py awx_logs.txt


Puis voir le résultat dans un browser
http://noc-tst.idev-fsd.ml:9092/


Pour mettre à zéro la 'table' dans InfluxDB
export ztable="ansible_logs3"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=DROP MEASUREMENT $ztable"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
"""


# True Flase
zdebug = True
zdebug2 = False
zprint_curl = True
zsend_grafana = False

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
ztask_site_1 = ""
ztask_time_1_obj = 0
ztask_duration_1_obj = 0

ztask_line_2 = 0
ztask_name_2 = ""
ztask_path_2 = ""
ztask_site_2 = ""
ztask_time_2_obj = 0


def zget_unix_time(zdate):
    #    date_time_obj = datetime.datetime.strptime(zdate, '%Y-%m-%d %H:%M:%S.%f')
    zdate_time_obj = zdate
    if zdebug2:
        print(" zdate_time_obj: [" + str(zdate_time_obj) + "]")
    zdate_time_1970_obj = datetime.datetime.strptime(
        "1970-01-01 01:00:00", '%Y-%m-%d %H:%M:%S')  # Astuce pour faire UTC-1 à cause de Grafana !
    if zdebug2:
        print(" zdate_time_1970_obj: [" + str(zdate_time_1970_obj) + "]")
    zdate_time_unix_obj = (zdate_time_obj - zdate_time_1970_obj)
    if zdebug2:
        print(" zdate_time_unix_obj: [" + str(zdate_time_unix_obj) + "]")
    return zdate_time_unix_obj


if (__name__ == "__main__"):
    print("\n" + version + "\n")

    if len(sys.argv) == 1:
        print("Usage: ./parse-ansible-out3.py fichier_log_a_parser\n\n")
        sys.exit()

    zfile = open(sys.argv[1], "r")
    i = 0


# ALT+CMD+F bascule du code au terminal

    db_logs = {}

    db_logs[1] = {"ztask_name": "toto1", "ztask_path": "tutu1", "zsite_name": {}}
    print("La db au complet: " + str(db_logs))

    db_logs[1]["zsite_name"].update({"tata1": {"ztime_start": 123}})
    db_logs[1]["zsite_name"].update({"tata2": {"ztime_start": 234}})
    
    print("La db au complet après l'ajout des 2x sites: " + str(db_logs))
    print("La 1ère task: " + str(db_logs[1]))
    print("Tous les sites de la 1ère task: " + str(db_logs[1]["zsite_name"]))
    print("La time du site tata1: " + str(db_logs[1]["zsite_name"]["tata1"]["ztime_start"]))
    print("\n")

    db_logs[2] = {"ztask_name": "toto2", "ztask_path": "tutu2", "zsite_name": {}}
    print("La db au complet: " + str(db_logs))

    db_logs[2]["zsite_name"].update({"tata1": {"ztime_start": 345}})
    db_logs[2]["zsite_name"].update({"tata2": {"ztime_start": 456}})
    
    print("La db au complet après l'ajout des 2x sites: " + str(db_logs))
    print("La 2ème task: " + str(db_logs[2]))
    print("Tous les sites de la 2ème task: " + str(db_logs[2]["zsite_name"]))
    print("La time du site tata1: " + str(db_logs[2]["zsite_name"]["tata1"]["ztime_start"]))
    print("\n")

    db_logs[1]["zsite_name"]["tata1"].update({"ztime_duration": 1})
    print("Tous les sites de la 1ère task: " + str(db_logs[1]["zsite_name"]))
    print("La time du site tata1 de la task 1: " + str(db_logs[1]["zsite_name"]["tata1"]["ztime_duration"]))

    quit()


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


    # On parse le fichier de logs
    while True:
        zline = zfile.readline()
        i = i + 1

        # Est-ce une TASK ?
        a = 'TASK ['
        if zline[0:len(a)] == a:

            # Est-ce la Task 'debug' ?
            if zline.find(": debug") != -1:
                if zdebug2:
                    print(str(i) + " " + zline)

                # On passe à la ligne suivante
                zline = zfile.readline()
                i = i + 1
                if zdebug2:
                    print(str(i) + " " + zline)

                # Récupération du path de la Task
                zpath = "/project/ansible/roles/wordpress-instance/tasks/"
                ztask_path_1 = zline[zline.find(zpath) + len(zpath):-1]
                if zdebug2:
                    print(str(i) + " ztask_path_1: [" + ztask_path_1 + "]")

                while True:
                    if i > 2000000:
                        quit()

                    # On passe à la ligne suivante
                    zline = zfile.readline()
                    i = i + 1
                    if zdebug2:
                        print(str(i) + " " + zline)

                    # Est-ce une ligne ok: [site name] ?
                    if zline.find("ok: [") != -1:

                        # Récupération du nom du site
                        ztask_site_1 = zline[1 + zline.find("["):zline.find("]")]
                        if zdebug2:
                            print(
                                str(i) + " ztask_site_1: [" + ztask_site_1 + "]")

                        # On passe à la ligne suivante
                        zline = zfile.readline()
                        i = i + 1
                        if zdebug2:
                            print(str(i) + " " + zline)

                        # Est-ce la ligne 'ztime' ?
                        if zline.find("ztime, ") != -1:
                            if zdebug2:
                                print("c'est une ligne ztime............")

                            # Récupération de la position dans le logs
                            ztask_line_1 = i

                            # Récupération du nom de la Task
                            ztask_name_1 = zline[1 + zline.find(
                                "/"):zline.find("/", 1 + zline.find("/"))]
                            if zdebug2:
                                print(
                                    str(i) + " ztask_name_1: [" + ztask_name_1 + "]")

                            # Récupération du time de la Task
                            ztask_time_1 = zline[2 + zline.find("/ "):-2]
                            if zdebug2:
                                print(
                                    str(i) + " ztask_time_1: [" + ztask_time_1 + "]")

                            print(
                                "..................................................")
                            print("Task name: " + str(ztask_line_1))
                            print("Task name: " + ztask_name_1)
                            print("Path name: " + ztask_path_1)
                            print("Site name: " + ztask_site_1)
                            print("Timestamp: " + ztask_time_1)
                            print(
                                "..................................................")

                            # On passe à la ligne suivante
                            zline = zfile.readline()
                            i = i + 1
                            if zdebug2:
                                print(str(i) + " " + zline)

                    else:
                        break

        if zline == "":
            break

    zfile.close()
