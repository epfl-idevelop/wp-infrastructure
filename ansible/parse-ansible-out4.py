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

version = "parse-ansible-out4.py  zf200908.0958 "

"""
ATTENTION: il ne faut pas oublier, avant de lancer la *petite fusée* d'effacer le fichier de log de reclog !
rm /Users/zuzu/dev-zf/reclog/file.log

génération du fichier logs:
Le faire avec la petite fusée du template dans l'interface WEB de AWX !

usage:
cp /Users/zuzu/dev-zf/reclog/file.log awx_logs_x_sites_y_forks_z_pods.txt

reset
./parse-ansible-out4.py awx_logs_10_sites_5_forks_1_pods.txt


Puis voir le résultat dans un browser
http://noc-tst.idev-fsd.ml:9092/


Pour mettre à zéro la 'table' dans InfluxDB
export ztable="awx_logs1"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=DROP MEASUREMENT $ztable"
curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/query?u=$dbflux_u_admin&p=$dbflux_p_admin&db=$dbflux_db"  --data-urlencode "q=SHOW MEASUREMENTS"
"""


# True False
zverbose_v = False
zverbose_vv = False
zprint_curl = True
zsend_grafana = True

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


def zprint_db_log():
    for i in range(1, ztask_number+1): 
        print("------------")
        print("ztask_name: " + str(i) + ", " + db_logs[i]["ztask_name"])
        print("ztask_path: " + db_logs[i]["ztask_path"])
        ztask_site_number = len(db_logs[i]) - 2
        for j in range(1, ztask_site_number+1):
            print("----")
            print("ztask_site_name: " + str(j) + ", " + db_logs[i][j]["ztask_site_name"])
            try:
                print("ztask_time_start: " + db_logs[i][j]["ztask_time_start"])
            except:
                print("************************************************************************oups y'a pas de ztask_time_start")

            try:
                print("ztask_line_start: " + str(db_logs[i][j]["ztask_line_start"]))
            except:
                print("************************************************************************oups y'a pas de ztask_line_start")

            try:
                print("ztask_time_end: " + db_logs[i][j]["ztask_time_end"])
            except:
                print("************************************************************************oups y'a pas de ztask_time_end")

            try:
                print("ztask_line_end: " + str(db_logs[i][j]["ztask_line_end"]))
            except:
                print("************************************************************************oups y'a pas de ztask_line_end")


            
        

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
        print("Usage: ./parse-ansible-out4.py fichier_log_a_parser\n\n")
        sys.exit()

    zfile = open(sys.argv[1], "r")
    i = 1

    # On parse le fichier de logs
    while True:
        zline = zfile.readline()
        # est-ce la fin du fichier de logs ?
        if zline == "":
            break

        if zverbose_vv: print("nouvelle ligne: " + str(i) + " " + zline[:-1])

        # Est-ce une ligne de Task ?
        if zline.find(', TASK:') != -1:            
            if zverbose_vv: print("coucou c'est une task")
            
            # Récupération du task_site
            zstr_find1 = ' by zuzu, '
            p1 = zline.find(zstr_find1)
            zstr_find2 = ': PATH: '            
            p2 = zline.find(zstr_find2, p1)
            ztask_site = zline[p1 + len(zstr_find1):p2]
            if zverbose_vv: print(str(i) + " ztask_site: [" + ztask_site + "]")
            
            # Récupération du task_path
            zstr_find1 = ': PATH: '
            p1 = zline.find(zstr_find1)
            zstr_find2 = ', TASK: '            
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
                ztask_site_number = len(db_logs[ztask_number]) - 2
                ztask_site_number = ztask_site_number + 1
                if zverbose_vv: print("ztask_site_number:" + str(ztask_site_number))

                # On crée un nouveau site et écrit le task_time_start
                db_logs[ztask_number][ztask_site_number] = {}
                db_logs[ztask_number][ztask_site_number]["ztask_site_name"] = ztask_site
                db_logs[ztask_number][ztask_site_number]["ztask_time_start"] = ztask_time
                db_logs[ztask_number][ztask_site_number]["ztask_line_start"] = i

                
            # Récupération du ztask_time_end
            if zline.find('log end') != -1:                
                if zverbose_vv: print("c'est un end")
                if zverbose_vv: print("ztask_number :" + str(ztask_number))

                # On cherche la tâche
                ztask_id = 0
                for j in range(1, ztask_number + 1):
                    if db_logs[j]["ztask_path"] == ztask_path and db_logs[j]["ztask_name"] == ztask_name:
                        ztask_id = j
                        if zverbose_vv: print("ztask_id :" + str(ztask_id))
                        break
                if ztask_id == 0:
                    print("oups, y'a pas de tâche ici 133759")
                    exit()
                # On cherche le site
                ztask_site_number = len(db_logs[ztask_id]) - 2
                if zverbose_vv: print("ztask_site_number 1135:" + str(ztask_site_number))

                ztask_site_id = 0
                # print(db_logs)
                #zprint_db_log()
                for j in range(1, ztask_site_number + 1):
                    print("j 1059: " + str(j))
                    # print(db_logs[ztask_id][j]["ztask_site_name"])
                    # print(ztask_site)
                    if zverbose_vv: print("ztask_site_name 1135:" + str(db_logs[ztask_id][j]["ztask_site_name"]))
                    if zverbose_vv: print("ztask_site 1135:" + str(ztask_site))
                    if db_logs[ztask_id][j]["ztask_site_name"] == ztask_site:
                        ztask_site_id = j
                        if zverbose_vv: print("ztask_site_id 1133:" + str(ztask_site_id))
                        break

                if ztask_site_id == 0:
                    print("oups, y'a pas de site ici 133935")
                    
                    # on cherche l'index du site dans le dictionnaire
                    ztask_site_id = len(db_logs[ztask_id]) - 2
                    ztask_site_id = ztask_site_id + 1
                    if zverbose_vv: print("ztask_site_id 1346:" + str(ztask_site_id))

                    # On crée un nouveau site
                    db_logs[ztask_id][ztask_site_id] = {}
                    db_logs[ztask_id][ztask_site_id]["ztask_site_name"] = ztask_site
                
                # On écrit le task_time_end
                db_logs[ztask_id][ztask_site_id]["ztask_time_end"] = ztask_time
                db_logs[ztask_id][ztask_site_id]["ztask_line_end"] = i

                
            
            

        print("")
        i = i + 1
        # On évite la boucle infinie ;-)
        if i > 2000000:
            break

    zfile.close()

    print("coucou 1057")
    #print(db_logs)
    # zprint_db_log()
    # quit()
    
    
    # Calcul les durations pour chaque sites
    for i in range(1, ztask_number+1): 
        if zverbose_vv: print("i: " + str(i))        
        ztask_site_number = len(db_logs[i]) - 2
        for j in range(1, ztask_site_number+1):
            if zverbose_vv: print("ztask_site_name: " + str(j) + ", " + db_logs[i][j]["ztask_site_name"])

            ztask_time_1 = db_logs[i][j]["ztask_time_start"][0:-6]
            if zverbose_vv: print("ztask_time_1: " + str(ztask_time_1))
            ztask_time_obj_1 = datetime.datetime.strptime(ztask_time_1, '%Y-%m-%d %H:%M:%S.%f')
            ztask_unix_time_1 = zget_unix_time(ztask_time_obj_1).total_seconds()
            if zverbose_vv: print("ztask_unix_time_1: " + str(ztask_unix_time_1))

            ztask_time_2 = db_logs[i][j]["ztask_time_end"][0:-6]
            if zverbose_vv: print("ztask_time_2: " + str(ztask_time_2))

            ztask_time_obj_2 = datetime.datetime.strptime(ztask_time_2, '%Y-%m-%d %H:%M:%S.%f')
            ztask_unix_time_2 = zget_unix_time(ztask_time_obj_2).total_seconds()
            if zverbose_vv: print("ztask_unix_time_2: " + str(ztask_unix_time_2))

            ztask_duration = ztask_unix_time_2 - ztask_unix_time_1
            if zverbose_vv: print("Durée: " + str(ztask_duration))
            
            db_logs[i][j]["ztask_duration"] = ztask_duration
            
            if zverbose_v: print("..................................................")                        
            if zverbose_v: print("Task number: " + str(i))
            if zverbose_v: print("ztask_name: " + str(i) + ", " + db_logs[i]["ztask_name"])
            if zverbose_v: print("ztask_path: " + db_logs[i]["ztask_path"])
            if zverbose_v: print("ztask_site_name: " + str(j) + ", " + db_logs[i][j]["ztask_site_name"])
            if zverbose_v: print("ztask_time_start: " + db_logs[i][j]["ztask_time_start"])
            if zverbose_v: print("ztask_line_start: " + str(db_logs[i][j]["ztask_line_start"]))
            if zverbose_v: print("ztask_time_end: " + db_logs[i][j]["ztask_time_end"])
            if zverbose_v: print("ztask_line_end: " + str(db_logs[i][j]["ztask_line_end"]))
            if zverbose_v: print("ztask_duration: " + str(db_logs[i][j]["ztask_duration"]))
            if zverbose_v: print("..................................................")

            
            ztable = "awx_logs1"
            ztask_name_1 = db_logs[i]["ztask_name"]
            ztask_line_1 = db_logs[i][j]["ztask_line_start"]
            ztask_path_1 = db_logs[i]["ztask_path"]
            ztask_site_1 = db_logs[i][j]["ztask_site_name"]
            
            # on raccourci le task_path à cause de l'affichage dans Grafana
            ztask_path_1 = ztask_path_1[ztask_path_1.find("project/ansible")+16:-1]
            
            # on change tous les caractères *system* utilisés par InfluxDB
            ztask_name = ztask_name_1.replace(" ", "_") + "_" + str(ztask_line_1)
            ztask_name = ztask_name_1.replace(" ", "_")
            ztask_path = ztask_path_1.replace(" ", "_")
            ztask_path = ztask_path.replace(":", "_")
            ztask_path = ztask_path.replace(".", "_")
            ztask_site = ztask_site_1
            
            # on transforme en nano secondes pour InfluxDB
            ztask_time_1 = db_logs[i][j]["ztask_time_start"][0:-6]
            ztask_time_obj_1 = datetime.datetime.strptime(ztask_time_1, '%Y-%m-%d %H:%M:%S.%f')
            ztask_unix_time_1 = zget_unix_time(ztask_time_obj_1).total_seconds()
            ztask_unix_time_nano = ztask_unix_time_1 * 1000000000

            ztask_duration = db_logs[i][j]["ztask_duration"]
            
            # zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable + ',action=' + ztask_path + ',task=' + ztask_name + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'
            
            zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable
            # zcmd = zcmd + ',path=' + ztask_path + ',task=' + ztask_name + ',site=' + ztask_site + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'
            zcmd = zcmd + ',task=' + ztask_name + '_/_' + ztask_path + ',site=' + ztask_site + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'
            
            if zprint_curl: print(zcmd)
            
            if zsend_grafana:
                zerr = os.system(zcmd)
                if zerr != 0:
                    print(zerr)

        # On évite la boucle infinie ;-)
        print("toto:" + str(i))
        if i > 1000000:
            break
            

