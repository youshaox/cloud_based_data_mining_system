
"""
Main script for dynamic deployment.
Usage: python3 <deploy.py> <config> <system_type> <number_of_instances>
Where: <config>              -- configuration file
       <system_type>         -- streamer / searcher / tweetdb / webserver / site
       <number_of_instances> -- number of instances to create. This must be 4 for system type 'site'.
"""
import re
import sys
import logging
import json
import boto
import os
import time
from boto.ec2.regioninfo import RegionInfo


NUM_ARGS = 4
ERROR = 2
PORT = 8773
PATH = "/services/Cloud"
INVENTORY_FILE_PATH = "inventory"

def create_ip_list(reservation):
    """Create a list containing IP addresses of created instances.

        Args:
            reservation:

    """
    ip_list = list()
    for instance in reservation.instances:
        while (instance.update() != "running"):
            time.sleep(5)
        ip_list.append(instance.private_ip_address)
    return ip_list


def check_cli_argument():
    """Check command line arguments and return configuration parameters in a json object and a list containing all system types.
        Args:
            reservation:
        Returns:
            jconfig:
            sys_type_list:
    """
    if len(sys.argv) != NUM_ARGS:
        logging.error(
            'invalid number of arguments: <deploy.py> <config.json> <system_type> <number_of_instances>'
        )
        sys.exit(ERROR)
    config = sys.argv[1]
    sys_type = sys.argv[2]
    num_instances = int(sys.argv[3])

    with open(config) as fp:
        jconfig = json.load(fp)

    sys_type_list = list()

    # 只是把我们总共要的system列了出来
    for jsys_type in jconfig['system_types']:
        sys_type_list.append(jsys_type['name'])

    if sys_type not in sys_type_list:
        if sys_type != "site":
            logging.error(
                'invalid <system_type>. Please choose one of the system types listed in config.json file.'
            )
            sys.exit(ERROR)
        elif num_instances != 4:
            logging.error(
                'when <system_type> is \'site\'. <number_of_instances> must be 4.'
            )
            sys.exit(ERROR)

    return jconfig, sys_type_list

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    """1. 读取配置文件中所有的配置信息"""
    # jconfig: 配置信息
    # sys_type_list: 所有的系统类型
    jconfig, sys_type_list = check_cli_argument()
    sys_type = sys.argv[2]
    num_instances = int(sys.argv[3])

    region = RegionInfo(name=jconfig['region']['name'], endpoint=jconfig['region']['endpoint'])

    """2.1 connect to nectar"""
    logging.info('Connecting to Nectar')
    ec2_conn = boto.connect_ec2(aws_access_key_id=jconfig['credentials']['access_key'],
                                aws_secret_access_key=jconfig['credentials']['secret_key'],
                                is_secure=True, region=region, port=PORT, path=PATH, validate_certs=False)
    ip_list = list()

    """2.2 Create instance/s"""
    logging.info("Creating instance")
    # 固定的四个
    if (sys_type == 'site'):
        for type in sys_type_list:
            print(type)
            reservation = ec2_conn.run_instances(max_count=1,
                                                 image_id=jconfig['system_types'][sys_type_list.index(type)][
                                                     'image_id'],
                                                 placement=jconfig['system_types'][sys_type_list.index(type)][
                                                     'placement'],
                                                 key_name=jconfig['key']['name'],
                                                 instance_type=jconfig['system_types'][sys_type_list.index(type)][
                                                     'instance_type'],
                                                 security_groups=jconfig['system_types'][sys_type_list.index(type)][
                                                     'security_groups'])
            # 直到跑起来
            while (reservation.instances[0].update() != "running"):
                time.sleep(5)
            ip_list.append(reservation.instances[0].private_ip_address)
            break  # t/p
        ip_list.extend(['0.0.0.0', '1.1.1.1', '2.2.2.2'])  # t/p
    else:
        logging.info('建立一个节点')
        reservation = ec2_conn.run_instances(max_count=num_instances,
                                             image_id=jconfig['system_types'][sys_type_list.index(sys_type)][
                                                 'image_id'],
                                             placement=jconfig['system_types'][sys_type_list.index(sys_type)][
                                                 'placement'],
                                             key_name=jconfig['key']['name'],
                                             instance_type=jconfig['system_types'][sys_type_list.index(sys_type)][
                                                 'instance_type'],
                                             security_groups=jconfig['system_types'][sys_type_list.index(sys_type)][
                                                 'security_groups'])
        """Get a list of running instances we've created"""
        ip_list = create_ip_list(reservation)
        # ip_list = create_ip_list(reservation)
    print('IP addresses of created instances: ' + ', '.join(ip_list))