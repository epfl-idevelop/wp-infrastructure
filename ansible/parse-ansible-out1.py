#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Petit script pour parser les logs de Ansible dans ce project
# sources: https://janakiev.com/blog/python-shell-commands/

version = "parse-ansible-out1.py  zf200708.1204 "

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


import datetime, os, sys

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
    if zdebug2 : print(" zdate_time_obj: [" + str(zdate_time_obj) + "]")
    zdate_time_1970_obj = datetime.datetime.strptime("1970-01-01 01:00:00", '%Y-%m-%d %H:%M:%S')        #Astuce pour faire UTC-1 à cause de Grafana !
    if zdebug2 : print(" zdate_time_1970_obj: [" + str(zdate_time_1970_obj) + "]")
    zdate_time_unix_obj = (zdate_time_obj - zdate_time_1970_obj)
    if zdebug2 : print(" zdate_time_unix_obj: [" + str(zdate_time_unix_obj) + "]")
    return zdate_time_unix_obj


if (__name__ == "__main__"):
    print("\n" + version + "\n")

    if len(sys.argv) == 1 :
        print("Usage: ./parse-ansible-out3.py fichier_log_a_parser\n\n")
        sys.exit()

    zfile = open(sys.argv[1], "r")
    i = 0

    
# ALT+CMD+F bascule du code au terminal


    # On parse le fichier de logs
    while True:
        zline = zfile.readline()
        i = i + 1

        # Est-ce une TASK ?
        a = 'TASK ['
        if zline[0:len(a)] == a :
        
            # Est-ce la Task 'debug' ?
            if zline.find(": debug") != -1 :
                if zdebug2 : print(str(i) + " " + zline)

                # On passe à la ligne suivante
                zline = zfile.readline()
                i = i + 1
                if zdebug2 : print(str(i) + " " + zline)

                # Récupération du path de la Task
                zpath = "/project/ansible/roles/wordpress-instance/tasks/"
                ztask_path_1 = zline[zline.find(zpath)+len(zpath):-1]
                if zdebug2 : print(str(i) + " ztask_path_1: [" + ztask_path_1 + "]")

                while True:
                    if i > 2000000 :
                        quit()

                    # On passe à la ligne suivante
                    zline = zfile.readline()
                    i = i + 1
                    if zdebug2 : print(str(i) + " " + zline)

                    # Est-ce une ligne ok: [site name] ?
                    if zline.find("ok: [") != -1 :

                        # Récupération du nom du site
                        ztask_site_1 = zline[1+zline.find("["):zline.find("]")]
                        if zdebug2 : print(str(i) + " ztask_site_1: [" + ztask_site_1 + "]")
            
                        # On passe à la ligne suivante
                        zline = zfile.readline()
                        i = i + 1
                        if zdebug2 : print(str(i) + " " + zline)
            
                        # Est-ce la ligne 'ztime' ?
                        if zline.find("ztime, ") != -1 :
                            if zdebug2 : print("c'est une ligne ztime............")
                
                            # Récupération de la position dans le logs
                            ztask_line_1 = i
                            
                            # Récupération du nom de la Task
                            ztask_name_1 = zline[1+zline.find("/"):zline.find("/",1+zline.find("/"))]
                            if zdebug2 : print(str(i) + " ztask_name_1: [" + ztask_name_1 + "]")
                
                            # Récupération du time de la Task
                            ztask_time_1 = zline[2+zline.find("/ "):-2]
                            if zdebug2 : print(str(i) + " ztask_time_1: [" + ztask_time_1 + "]")
                            
                            print("..................................................")
                            print("Task name: " + str(ztask_line_1))
                            print("Task name: " + ztask_name_1)
                            print("Path name: " + ztask_path_1)
                            print("Site name: " + ztask_site_1)
                            print("Timestamp: " + ztask_time_1)
                            print("..................................................")

                            # On passe à la ligne suivante
                            zline = zfile.readline()
                            i = i + 1
                            if zdebug2 : print(str(i) + " " + zline)

                                        
                    else:
                        break

        if zline == "" :
            break

    zfile.close()




"""
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

                ztask_unix_time_nano = zget_unix_time(ztask_time_1_obj).total_seconds()*1000000000

                zdate_time_obj_1900 = datetime.datetime.strptime("1900-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
                ztask_duration = (ztask_duration_1_obj - zdate_time_obj_1900).total_seconds()

                zcmd = 'curl -i -XPOST "$dbflux_srv_host:$dbflux_srv_port/write?db=$dbflux_db&u=$dbflux_u_user&p=$dbflux_p_user"  --data-binary "' + ztable + ',action=' + ztask_path + ',task=' + ztask_name + ' duration=' + str(ztask_duration) + ' ' + '%0.0f' % (ztask_unix_time_nano) + '"'
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


"""








"""
ATTENTION vérifier (dans Grafana) AVANT que TELEGRAF tourne bien sur la machine Ansible ET le container mgmt !

################################################################################################
ATOM IDE terminal debug zone
################################################################################################
ssh-add -l
ssh-add
ssh-add -l
source /Keybase/team/epfl_wwp_blue/influxdb_secrets.sh
ssh -A -o SendEnv="GIT*, dbflux*" ubuntu@localhost -p 52222
cd wp-ops/ansible/
oc logout
oc login https://pub-os-exopge.epfl.ch -u czufferey
################### il faut entrer le password dans la fenêtre *terminal*

#sur la console terminal de OKD de mgmt(ATTENTION bien vérifier être dans wwp-int):
bash
cd /srv/le_truc_à_effacer_pour_partir_de_scratch
rm -rf le_truc_à_effacer_pour_partir_de_scratch



##########################################################
zlog="ansible_xfois1_labs_big_1_7.log"
./wpsible -vvv -l labs_big_1 --connector ssh --ssh-port 2222 -f 7 2>&1 |tee $zlog
./parse-ansible-out3.py $zlog
zlog="ansible_xfois2_labs_big_1_7.log"
./wpsible -vvv -l labs_big_1 --connector ssh --ssh-port 2222 -f 7 2>&1 |tee $zlog
./parse-ansible-out3.py $zlog

zlog="ansible_xfois1_labs_big_5_7.log"
./wpsible -vvv -l labs_big_5 --connector ssh --ssh-port 2222 -f 7 2>&1 |tee $zlog
./parse-ansible-out3.py $zlog
zlog="ansible_xfois2_labs_big_5_7.log"
./wpsible -vvv -l labs_big_5 --connector ssh --ssh-port 2222 -f 7 2>&1 |tee $zlog
./parse-ansible-out3.py $zlog

zlog="ansible_xfois1_labs_10_7.log"
./wpsible -vvv -l labs_10 --connector ssh --ssh-port 2222 -f 7 2>&1 |tee $zlog
./parse-ansible-out3.py $zlog


zlog="ansible_xfois1_labs_224_7.log"
./wpsible -vvv -l labs_224 --connector ssh --ssh-port 2222 -f 7 2>&1 |tee $zlog
./parse-ansible-out3.py $zlog

zlog="ansible_xfois2_labs_224_7.log"
./wpsible -vvv -l labs_224 --connector ssh --ssh-port 2222 -f 7 2>&1 |tee $zlog
./parse-ansible-out3.py $zlog





"""