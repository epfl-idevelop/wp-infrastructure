#
# Petit script pour parser les logs de Ansible dans ce project
# zf191010.1625

import re, json

def tasks(infile):
    next_task = ""
    while True:
        next_line = infile.readline()
        if next_line == "":
            break
        if is_task_header(next_line):
            yield next_task
            next_task = next_line
        else:
            next_task += next_line


def is_task_header(line):
    return -1 != line.find("TASK")

def reports_from_json(task):
    #import ipdb; ipdb.set_trace()
    matched = re.search(r'=> ({\n.*\n})', task, flags=re.DOTALL)
    if matched:
        #import ipdb; ipdb.set_trace()
        return [json.loads(matched.groups()[0])]
    else:
        return []



################################################################################

if (__name__ == "__main__"):
    for task in tasks(open("ansible.log")):
        for report in reports_from_json(task):
            print "$$$$$$$$$$$$$$$$$\n"
            #print report
            if "start" in report:
                print("Start at: "+report["start"])
                print("End at: "+report["end"])
                #import ipdb; ipdb.set_trace()
            print "$$$$$$$$$$$$$$$$$\n"
