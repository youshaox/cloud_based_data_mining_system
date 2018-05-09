"""
group 25
* Youshao Xiao - 876548
* Jiaheng Zhu - 1211955
* Lina Zhou - 941539
* Haimei Liu - 895804
* Miaomiao Zhang - 895216

Script for dynamic deployment.
Usage: python3 <deploy.py> <configure> <sys_type> <number_of_instances>
Where: <config>              -- configuration file
       <sys_type>         -- streamer / searcher / couchdb / webserver / combo / default
       <number_of_instances> -- number of instances to create. This must be the number of instances specified in the configure file.
"""
import sys
import logging
import json
import boto
import os
import time
import datetime
from boto.ec2.regioninfo import RegionInfo

NUM_ARGS = 4
ERROR = 2
PORT = 8773
PATH = "/services/Cloud"
INVENTORY_FILE_PATH = "inventory"
CLUSTER_FILE_PATH = "cluster_setup.sh"
SLEEP_TIME = 5

# couchdb cluster formation
def prepend_the_master_ip(inventory_filename, master_ip):
    """
    prepend the master ip to the inventory for the couchdb cluster
    :param inventory_filename:
    :param master_ip:
    :return:
    """
    with open(inventory_filename, 'r+') as inventory_file:
        content = inventory_file.read()
        inventory_file.seek(0, 0)
        line = "[master]\n" + str(master_ip) + "\n"
        inventory_file.write(line.rstrip('\r\n') + '\n' + content)

def get_curl_command(master_ip, slave_ip):
    command = "curl -X PUT \"http://admin:cdurq48YWLWtZtd@" + str(master_ip) + ":5986/_nodes/couchdb@" + str(slave_ip) + "\"" + " -d {}\n"
    return command

def genearate_cluster_setup_file(instance_info_list):
    cluster_setup_filename = CLUSTER_FILE_PATH
    with open(cluster_setup_filename, 'w+') as cluster_setup_file:
        master_ip=""
        slave_ip_list=list()
        for indx in range(len(instance_info_list)):
            if instance_info_list[indx][indx]['name'] == "couchdb-master":
                master_ip = instance_info_list[indx][indx]['ip']
            elif instance_info_list[indx][indx]['name'] == "couchdb-slave":
                slave_ip_list.append(instance_info_list[indx][indx]['ip'])
        if len(slave_ip_list) == 0:
            logging.info("0 slave. No need for cluster setup")
        else:
            cluster_setup_file.write('#!/usr/bin/env bash\n')
            for slave_ip in slave_ip_list:
                line = get_curl_command(master_ip, slave_ip)
                cluster_setup_file.write(line)
    return cluster_setup_filename, len(slave_ip_list), master_ip

def run(inventory_name, s_type):
    """
    run the corresponding yaml
    :param inventory_name:
    :param s_type:
    :return:
    """
    playbook_name=""
    if s_type == "couchdb":
        playbook_name = "couchdb.yml"
    elif s_type == "streamer":
        playbook_name = "streamer.yml"
    elif s_type == "searcher":
        playbook_name = "searcher.yml"
    elif s_type == "webserver":
        playbook_name = "webserver.yml"
    elif s_type == "combo":
        playbook_name = "combo.yml"
    command = "ansible-playbook -i " + inventory_name + " template/" + playbook_name
    logging.info(command)
    os.system(command)

def orchestrate(inventory_name, sys_type, inventory_list):
    if sys_type == "default":
        for jinventory in inventory_list:
            s_type = jinventory['s_type']
            run(inventory_name, s_type)
    else:
        s_type = sys_type
        run(inventory_name, s_type)

def get_crendential():
    return "\n[all:vars]\nansible_ssh_user=ubuntu\nansible_ssh_private_key_file=./group25.pem\nansible_ssh_extra_arg"\
           +"s='-o StrictHostKeyChecking=no'\n"

def generate_actual_inventory(inventory_file, sys_list):
    for jsys in sys_list:
        s_type = jsys['s_type']
        # s_num = jsys['s_num']
        if s_type == "webserver":
            inventory_file.write('[webserver]\n')
            for ip in jsys['ip_list']:
                inventory_file.write(ip + "\n")
        elif s_type == "searcher":
            inventory_file.write('[searcher]\n')
            for ip in jsys['ip_list']:
                inventory_file.write(ip + " auth=1" + "\n")
        elif s_type == "streamer":
            inventory_file.write('[streamer]\n')
            for ip in jsys['ip_list']:
                inventory_file.write(ip + " auth=0" + "\n")
        elif s_type == "couchdb":
            inventory_file.write('[couchdb]\n')
            for ip in jsys['ip_list']:
                inventory_file.write(ip + "\n")
        elif s_type == "combo":
            inventory_file.write('[combo]\n')
            for ip in jsys['ip_list']:
                inventory_file.write(ip + "\n")
        else:
            logging.error("Unknown system type when generating the inventory")
            sys.exit(ERROR)

def generate_inventory(instance_info_list):
    """
    generate the inventory file for the usage in the ansibe-playbook
    :param instance_info_list:
    :return:
    """
    inventory_list = list()
    combo_ip_list = list()
    couchdb_ip_list = list()
    streamer_ip_list = list()
    searcher_ip_list = list()
    webserver_ip_list = list()

    suffix = datetime.datetime.now().strftime("%m%d%H%M")
    inventory_filename = INVENTORY_FILE_PATH+suffix
    inventory_file = open(inventory_filename, 'w+')

    for indx in range(len(instance_info_list)):
        if instance_info_list[indx][indx]['type'] == "combo":
            combo_ip_list.append(instance_info_list[indx][indx]['ip'])
        elif instance_info_list[indx][indx]['type'] == "couchdb":
            couchdb_ip_list.append(instance_info_list[indx][indx]['ip'])
        elif instance_info_list[indx][indx]['type'] == "streamer":
            streamer_ip_list.append(instance_info_list[indx][indx]['ip'])
        elif instance_info_list[indx][indx]['type'] == "searcher":
            searcher_ip_list.append(instance_info_list[indx][indx]['ip'])
        elif instance_info_list[indx][indx]['type'] == "webserver":
            webserver_ip_list.append(instance_info_list[indx][indx]['ip'])

    if len(combo_ip_list) != 0:
        inventory_list.append({"s_type":"combo","s_num":len(combo_ip_list), "ip_list":combo_ip_list})

    if len(couchdb_ip_list) != 0:
        inventory_list.append({"s_type": "couchdb", "s_num": len(couchdb_ip_list), "ip_list": couchdb_ip_list})

    if len(streamer_ip_list) != 0:
        inventory_list.append({"s_type": "streamer", "s_num": len(streamer_ip_list), "ip_list": streamer_ip_list})

    if len(searcher_ip_list) != 0:
        inventory_list.append({"s_type": "searcher", "s_num": len(searcher_ip_list), "ip_list": searcher_ip_list})

    if len(webserver_ip_list) != 0:
        inventory_list.append({"s_type": "webserver", "s_num": len(webserver_ip_list), "ip_list": webserver_ip_list})
    generate_actual_inventory(inventory_file, inventory_list)

    inventory_file.write(get_crendential())
    return inventory_filename, inventory_list

def get_volume_size(jconfig):
    """
    return the volume size of the first combo or couchdb in the configure.json
    :param jconfig:
    :return:
    """
    jinstance_info_list = jconfig['sys_types']
    for jinstance_info in jinstance_info_list:
        # print(jinstance_info)
        if jinstance_info['type'] in 'couchdb' or jinstance_info['type'] in 'combo':
            # print("+" + jinstance_info)
            n_volume_size = jinstance_info['volume_size']
            # print(n_volume_size)
            return n_volume_size

def createVolume(ec2_conn, size):
    """
    create volume
    :param ec2_conn:
    :param size:
    :return:
    """
    logging.info('Create a volume with size(G): ' + str(size))
    return ec2_conn.create_volume(size, "melbourne-qh2")

def attachVolume(ec2_conn, volume_size, target_instance_id):
    volume = createVolume(ec2_conn, int(volume_size))
    volume_id = volume.id
    ec2_conn.attach_volume(volume_id, target_instance_id, "/dev/vdc")
    logging.info("Attach " + str(volume_id) + " to " + str(target_instance_id))
    return True

def add_tag(instance, key, name):
    """
    add tag for the instance
    :param instance:
    :param key:
    :param name:
    :return:
    """
    status = instance.update()
    while status != 'running':
        time.sleep(SLEEP_TIME)
        status = instance.update()
    instance.add_tag(key, name)

def check_arguments():
    """
    Check command line arguments and return configuration parameters in a json object and a list containing all system types.
    :return:
    """
    if len(sys.argv) != NUM_ARGS:
        logging.error(
            'invalid number of arguments: <deploy.py> <config.json> <sys_type> <number_of_instances>'
        )
        sys.exit(ERROR)
    config = sys.argv[1]
    sys_type = sys.argv[2]
    num_instances = int(sys.argv[3])

    with open(config) as fp:
        jconfig = json.load(fp)

    sys_type_list = list()
    instance_name_list = list()

    for instance_name in jconfig['sys_types']:
        instance_name_list.append(instance_name['name'])
    # instance name list
    for jsys_type in jconfig['sys_types']:
        sys_type_list.append(jsys_type['type'])

    if sys_type not in sys_type_list:
        if sys_type != "default":
            logging.error(
                'invalid <sys_type>. Please choose one of the system types listed in config.json file.'
            )
            sys.exit(ERROR)
        elif num_instances != len(sys_type_list):
            logging.error(
                'when <sys_type> is \'default\'. <number_of_instances> must be the number of instance in the configuration file.'
            )
            sys.exit(ERROR)
    return jconfig, sys_type_list, instance_name_list

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s-[line:%(lineno)d]-%(levelname)s: %(message)s')
    # 1. check the arguments
    jconfig, sys_type_list, instance_name_list = check_arguments()
    sys_type = sys.argv[2]
    num_instances = int(sys.argv[3])

    region = RegionInfo(name=jconfig['region']['name'], endpoint=jconfig['region']['endpoint'])
    logging.info('1. Finish parsing the ' + sys.argv[1])

    logging.info('2.1 Connecting to Nectar')
    ec2_conn = boto.connect_ec2(aws_access_key_id=jconfig['credentials']['access_key'],
                                aws_secret_access_key=jconfig['credentials']['secret_key'],
                                is_secure=True, region=region, port=PORT, path=PATH, validate_certs=False)
    logging.info("2.2 Creating instances")

    instance_info_list = list()

    if (sys_type == 'default'):

        num = 0
        for instance_name in instance_name_list:
            jinfo = {}
            reservation = ec2_conn.run_instances(max_count=1,
                                                 image_id=jconfig['sys_types'][instance_name_list.index(instance_name)][
                                                     'image_id'],
                                                 placement=jconfig['sys_types'][instance_name_list.index(instance_name)][
                                                     'placement'],
                                                 key_name=jconfig['key']['name'],
                                                 instance_type=jconfig['sys_types'][instance_name_list.index(instance_name)][
                                                     'instance_type'],
                                                 security_groups=jconfig['sys_types'][instance_name_list.index(instance_name)][
                                                     'security_groups'])
            instance = reservation.instances[0]
            add_tag(instance, 'Name', jconfig['sys_types'][instance_name_list.index(instance_name)]['name'])
            add_tag(instance, 'Type', jconfig['sys_types'][instance_name_list.index(instance_name)]['type'])

            while (instance.update() != "running"):
                time.sleep(SLEEP_TIME)

            logging.info("Create the instance: " + str(jconfig['sys_types'][instance_name_list.index(instance_name)]['name']) + " with instance id: "
                         + str(instance.id))
            # attach the volumes if the volume is specified in the configure.json:
            instance_id = instance.id
            try:
                # if there is no volume set, just leave it.
                volume_size = jconfig['sys_types'][instance_name_list.index(instance_name)]['volume_size']
                attachVolume(ec2_conn, volume_size, instance_id)
            except KeyError:
                pass
            jinfo = {}
            jinfo[num] = {"instance-id": instance.id,
                      "name": jconfig['sys_types'][instance_name_list.index(instance_name)]['name'],
                      'type': jconfig['sys_types'][instance_name_list.index(instance_name)]['type'],
                      'ip': instance.private_ip_address}
            instance_info_list.append(jinfo)
            num += 1
    else:
        reservation = ec2_conn.run_instances(max_count=num_instances,
                                             image_id=jconfig['sys_types'][sys_type_list.index(sys_type)][
                                                 'image_id'],
                                             placement=jconfig['sys_types'][sys_type_list.index(sys_type)][
                                                 'placement'],
                                             key_name=jconfig['key']['name'],
                                             instance_type=jconfig['sys_types'][sys_type_list.index(sys_type)][
                                                 'instance_type'],
                                             security_groups=jconfig['sys_types'][sys_type_list.index(sys_type)][
                                                 'security_groups'])

        for instance in reservation.instances:
            while (instance.update() != "running"):
                time.sleep(SLEEP_TIME)
        for num in range(num_instances):
            jinfo = {}
            instance = reservation.instances[num]
            add_tag(instance, 'Name', jconfig['sys_types'][sys_type_list.index(sys_type)]['name'])
            add_tag(instance, 'Type', jconfig['sys_types'][sys_type_list.index(sys_type)]['type'])
            jinfo[num] = {"instance-id": instance.id,
                                "name": jconfig['sys_types'][sys_type_list.index(sys_type)]['name'],
                                'type': jconfig['sys_types'][sys_type_list.index(sys_type)]['type'],
                                'ip': instance.private_ip_address}
            instance_info_list.append(jinfo)
            # attach the volume if there is volume settings
            if sys_type in "couchdb" or sys_type in "combo":
                try:
                    # if there is no volume set, just leave it.
                    instance_id = instance.id
                    volume_size = get_volume_size(jconfig)
                    attachVolume(ec2_conn, volume_size, instance_id)
                except KeyError:
                    pass

    logging.info('3. Finish instances setup')
    logging.info("The info of the instances created:")
    for instance in instance_info_list:
        logging.info(instance)

    logging.info('4. Generate inventory')
    inventory_filename, inventory_list = generate_inventory(instance_info_list)
    logging.info("Waiting for a while for the open of the port 22")

    time.sleep(SLEEP_TIME*14)
    logging.info("5. Orchestrate the servers")
    orchestrate(inventory_filename, sys_type, inventory_list)

    # form cluster function only provided to the default mode if the couchdb instances >= 2
    if sys_type == 'default':
        cluster_setup_shell_filename, slave_num, master_ip = genearate_cluster_setup_file(instance_info_list)
        if slave_num != 0:
            prepend_the_master_ip(inventory_filename, master_ip)
            command = "ansible-playbook -v -i " + inventory_filename + " template/cluster.yml"
            os.system(command)
            logging.info("Form the couchdb cluster with slave number:" + str(slave_num))
    logging.info("6. Finish")
