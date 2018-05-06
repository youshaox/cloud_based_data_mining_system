
"""
Main script for dynamic deployment.
Usage: python3 <deploy.py> <configure> <sys_type> <number_of_instances>
Where: <config>              -- configuration file
       <sys_type>         -- streamer / searcher / couchdb / webserver / default
       <number_of_instances> -- number of instances to create. This must be 4 for system type 'default'.
"""
import re
import sys
import logging
import json
import boto
import os
import time
import datetime
from boto.ec2.regioninfo import RegionInfo
import controller

NUM_ARGS = 4
ERROR = 2
PORT = 8773
PATH = "/services/Cloud"
INVENTORY_FILE_PATH = "inventory"
SLEEP_TIME = 5


def orchestrate(inventory_name, sys_type):
    if sys_type == "couchdb":
        playbook_name = "couchdb.yml"
    elif sys_type == "streamer":
        playbook_name = "streamer.yml"
    elif sys_type == "searcher":
        playbook_name = "searcher.yml"
    elif sys_type == "webserver":
        playbook_name = "webserver.yml"
    command = "ansible-playbook -i " + inventory_name + " template/" + playbook_name
    print(command)
    os.system(command)

def get_crendential():
    return "\n[all:vars]\nansible_ssh_user=ubuntu\nansible_ssh_private_key_file=./group25.pem\nansible_ssh_extra_arg"\
           +"s='-o StrictHostKeyChecking=no'"

def generate_inventory(controller, sys_type, num_instances, instance_info_list):
    # reuse
    suffix = datetime.datetime.now().strftime("%m%d%H%M")
    inventory_filename = INVENTORY_FILE_PATH+suffix
    inventory_file = open(inventory_filename, 'w+')
    if sys_type == "default":
        pass
    else:
        if sys_type == "webserver":
            inventory_file.write('[webserver]\n')
            for indx in range(len(instance_info_list)):
                inventory_file.write(instance_info_list[indx][indx]['ip'] +'\n')
            inventory_file.write(get_crendential())
        elif sys_type == "searcher":
            inventory_file.write('[searcher]\n')
            for indx in range(len(instance_info_list)):
                inventory_file.write(instance_info_list[indx][indx]['ip'] +" auth=1" +'\n')
            inventory_file.write(get_crendential())
        elif sys_type == "streamer":
            inventory_file.write('[streamer]\n')
            for indx in range(len(instance_info_list)):
                # todo consider to use dynamic authoriation number
                inventory_file.write(instance_info_list[indx][indx]['ip'] + " auth=0" + '\n')
            inventory_file.write(get_crendential())
        elif sys_type == "couchdb":
            inventory_file.write('[couchdb]\n')
            for indx in range(len(instance_info_list)):
                inventory_file.write(instance_info_list[indx][indx]['ip'] + '\n')
                # print(len(instance_info_list))
                # print(instance_info_list[indx][indx]['ip'])
            inventory_file.write(get_crendential())
    return inventory_filename

def createVolume(ec2_conn, size):
    logging.info('Create a volume with size(G): ' + str(size))
    return ec2_conn.create_volume(size, "melbourne-qh2")

def attachVolume(ec2_conn, volume_size, target_instance_id):
    # todo 需要测试
    volume = createVolume(ec2_conn, volume_size)
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


def create_ip_list(reservation):
    """Create a list containing IP addresses of created instances.

        Args:
            reservation:

    """
    ip_list = list()
    for instance in reservation.instances:
        while (instance.update() != "running"):
            time.sleep(SLEEP_TIME)
        ip_list.append(instance.private_ip_address)
    return ip_list


def check_arguments():
    """Check command line arguments and return configuration parameters in a json object and a list containing all system types.
        Args:
            reservation:
        Returns:
            jconfig:
            sys_type_list:
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

    # instance name list
    for jsys_type in jconfig['sys_types']:
        sys_type_list.append(jsys_type['type'])

    if sys_type not in sys_type_list:
        if sys_type != "default":
            logging.error(
                'invalid <sys_type>. Please choose one of the system types listed in config.json file.'
            )
            sys.exit(ERROR)
        elif num_instances != 2:
            logging.error(
                'when <sys_type> is \'default\'. <number_of_instances> must be 2.'
            )
            sys.exit(ERROR)

    return jconfig, sys_type_list

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s-[line:%(lineno)d]-%(levelname)s: %(message)s')
    #
    # """1. 读取配置文件中所有的配置信息"""
    jconfig, sys_type_list = check_arguments()
    sys_type = sys.argv[2]
    num_instances = int(sys.argv[3])
    #
    region = RegionInfo(name=jconfig['region']['name'], endpoint=jconfig['region']['endpoint'])
    logging.info('1. Finish parsing the ' + sys.argv[1])
    #
    logging.info('2.1 Connecting to Nectar')
    ec2_conn = boto.connect_ec2(aws_access_key_id=jconfig['credentials']['access_key'],
                                aws_secret_access_key=jconfig['credentials']['secret_key'],
                                is_secure=True, region=region, port=PORT, path=PATH, validate_certs=False)
    ip_list = list()

    logging.info("2.2 Creating instances")

    num = 1
    instance_info_list = list()
    # ------
    # ## by default, we creating the instances shown in the configure.json
    # if (sys_type == 'default'):
    #
    #     for type in sys_type_list:
    #         jinfo = {}
    #         reservation = ec2_conn.run_instances(max_count=1,
    #                                              image_id=jconfig['sys_types'][sys_type_list.index(type)][
    #                                                  'image_id'],
    #                                              placement=jconfig['sys_types'][sys_type_list.index(type)][
    #                                                  'placement'],
    #                                              key_name=jconfig['key']['name'],
    #                                              instance_type=jconfig['sys_types'][sys_type_list.index(type)][
    #                                                  'instance_type'],
    #                                              security_groups=jconfig['sys_types'][sys_type_list.index(type)][
    #                                                  'security_groups'])
    #         instance = reservation.instances[0]
    #         add_tag(instance, 'Name', jconfig['sys_types'][sys_type_list.index(type)]['name'])
    #         add_tag(instance, 'Type', jconfig['sys_types'][sys_type_list.index(type)]['type'])
    #
    #         while (instance.update() != "running"):
    #             time.sleep(SLEEP_TIME)
    #
    #         logging.info("Create the instance: " + str(jconfig['sys_types'][sys_type_list.index(type)]['name']) + " with instance id: "
    #                      + str(instance.id))
    #         # attach the volumes:
    #         instance_id = instance.id
    #         try:
    #             volume_size = jconfig['sys_types'][sys_type_list.index(type)]['volume_size']
    #             attachVolume(ec2_conn, volume_size, instance_id)
    #         except KeyError:
    #             pass
    #         ip_list.append(instance.private_ip_address)
    #
    #         ec2_conn.get_all_instances()
    #
    #         # jinfo = {num:{'name':jconfig['sys_types'][sys_type_list.index(type)]['name'],
    #         #          'sys_type':jconfig['sys_types'][sys_type_list.index(type)]['type'],
    #         #               'ip':}}
    #         # instance_info_list.append(jinfo)
    #
    # else:
    #     reservation = ec2_conn.run_instances(max_count=num_instances,
    #                                          image_id=jconfig['sys_types'][sys_type_list.index(sys_type)][
    #                                              'image_id'],
    #                                          placement=jconfig['sys_types'][sys_type_list.index(sys_type)][
    #                                              'placement'],
    #                                          key_name=jconfig['key']['name'],
    #                                          instance_type=jconfig['sys_types'][sys_type_list.index(sys_type)][
    #                                              'instance_type'],
    #                                          security_groups=jconfig['sys_types'][sys_type_list.index(sys_type)][
    #                                              'security_groups'])
    #
    #     for instance in reservation.instances:
    #         while (instance.update() != "running"):
    #             time.sleep(SLEEP_TIME)
    #     for num in range(num_instances):
    #         jinfo = {}
    #         instance = reservation.instances[num]
    #         add_tag(instance, 'Name', jconfig['sys_types'][sys_type_list.index(sys_type)]['name'])
    #         add_tag(instance, 'Type', jconfig['sys_types'][sys_type_list.index(sys_type)]['type'])
    #         jinfo[num] = {"instance-id": instance.id,
    #                             "name": jconfig['sys_types'][sys_type_list.index(sys_type)]['name'],
    #                             'type': jconfig['sys_types'][sys_type_list.index(sys_type)]['type'],
    #                             'ip': instance.private_ip_address}
    #         instance_info_list.append(jinfo)
    #
    # logging.info('IP addresses of created instances: ' + ', '.join(ip_list))
    # logging.info('3. Finish instances setup')
    #
    # logging.info("The info of the instances created:")
    # for instance in instance_info_list:
    #     logging.info(instance)
    #
    # controller = controller.Controller(aws_access_key_id=jconfig['credentials']['access_key'], aws_secret_access_key=jconfig['credentials']['secret_key'])
    # # todo 新的
    # logging.info('4. Generate inventory')
    instance_info_list_fake = [{0: {'instance-id': 'i-bf902ce6', 'name': 'webserver', 'type': 'streamer', 'ip': '115.146.84.167'}},
                    {1: {'instance-id': 'i-c9dbb437', 'name': 'webserver', 'type': 'searcher', 'ip': '115.146.85.170'}}]

    inventory_name = generate_inventory(controller, sys_type, num_instances, instance_info_list_fake)

    # wait for the SSH port open
    # time.sleep(SLEEP_TIME*4)
    # inventory_name ='inventory05061156.txt'
    orchestrate(inventory_name, sys_type)

# Shawn
# "access_key":"238656dab65d438390d91f689a08cb55",
# "secret_key":"e5734f0116ab4104b1b24c3f8dd651b0"

# miaomiao
# d39e2b6c96124c3cbd44749c7aa730b5
# 512ad49874cf4d8eba84ec7c526cb3a5

# mia
# 04908217f41748f28077b2c0f6bffa32
# 4c29e65c91fe4f7c8323e554df848eef