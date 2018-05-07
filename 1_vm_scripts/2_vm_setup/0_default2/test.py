#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 5/5/18
"""
function:

"""
import sys
import datetime

CLUSTER_FILE_PATH = "cluster_setup"

def get_curl_command(master_ip, slave_ip):
    command = "curl -X PUT \"http://admin:cdurq48YWLWtZtd@" + str(master_ip) + ":5986/_nodes/couchdb@" + str(slave_ip) + "\"" + " -d {}\n"
    return command

def genearate_cluster_setup(instance_info_list):
    suffix = datetime.datetime.now().strftime("%m%d%H%M")
    cluster_setup_filename = CLUSTER_FILE_PATH + suffix + ".sh"
    print(cluster_setup_filename)

    with open(cluster_setup_filename, 'w+') as cluster_setup_file:
        master_ip=""
        slave_ip_list=list()
        for indx in range(len(instance_info_list)):
            if instance_info_list[indx][indx]['name'] == "couchdb-master":
                master_ip = instance_info_list[indx][indx]['ip']
            elif instance_info_list[indx][indx]['name'] == "couchdb-slave":
                slave_ip_list.append(instance_info_list[indx][indx]['ip'])
        cluster_setup_file.write('#!/usr/bin/env bash\n')
        if len(slave_ip_list)!=0:
            for slave_ip in slave_ip_list:
                line = get_curl_command(master_ip, slave_ip)
                cluster_setup_file.write(line)

instance_info_list=[{0: {'instance-id': 'i-f4e28fa0', 'name': 'couchdb-slave', 'type': 'combo', 'ip': '115.146.85.177'}},
                    {1: {'instance-id': 'i-80a739bd', 'name': 'couchdb-master', 'type': 'combo', 'ip': '115.146.86.215'}},
                    {2: {'instance-id': 'i-80a739bd', 'name': 'couchdb-slave', 'type': 'combo', 'ip': '115.146.86.213'}},
                    {3: {'instance-id': 'i-80a739bd', 'name': 'couchdb-slave', 'type': 'combo', 'ip': '115.146.86.214'}}]
genearate_cluster_setup(instance_info_list)