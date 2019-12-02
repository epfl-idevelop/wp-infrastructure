# coding: utf-8
#
# Petit script pour parser les logs de Ansible dans ce project
# version conventionnelle plus simple
# zf191202.1752

"""
 génération du fichier logs
    ./wpsible -vvv -l _srv_www_www.epfl.ch_htdocs_about 2>&1 |tee ansible.log

 usage:
    . parser/bin/activate
    python parse-ansible-out.py
"""


# "start": "2019-10-10 12:51:23.875479"

import datetime
#import time

def zget_time(zstring):
    p1 = zline.find(zstring) + len(zstring)
    p2 = zline.find(" ", p1)
    p3 = zline.find('"', p2)
    zdate = zline[p1:p2]
    ztime = zline[p2:p3]


date_time_str = "2019-10-10 12:51:58.886249"
date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
date_time_1970 = datetime.datetime.strptime("1970-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
date_time_sec = (date_time_obj - date_time_1970).total_seconds()
print "%18.6f\n" % (date_time_sec)




print zdate, ztime, ztimestamp




if (__name__ == "__main__"):
    zfile = open("ansible.log.191010", "r")
    i = 0
    while True:
        zline = zfile.readline()
        i = i + 1
#        if zline.find("TASK ") != -1 :
#            print i, zline
        a = '"start": "'
        if zline.find(a) != -1 :
            print i, zline
            zget_time(a)




        if zline == "":
            break

    zfile.close()

"""
        if zline.find('"end":') != -1 :
            print i, zline
        if zline.find('"delta":') != -1 :
            print i, zline
"""
