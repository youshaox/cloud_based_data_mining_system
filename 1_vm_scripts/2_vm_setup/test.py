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


def addTag(instance, key, name):  # create tag for an instance
    status = instance.update()
    while status != 'running':
        time.sleep(1)
        status = instance.update()
    instance.add_tag(key, name)


def attachVolume(ec2_conn, volume_id, instance_id):
    # return ec2_conn.attach_volume(volume_id, instance_id)
    return ec2_conn.attach_volume(volume_id, instance_id, "/dev/vdc")




sys_type_list = ['streamer', 'searcher', 'tweetdb', 'webserver']
jconfig = {'region': {'name': 'melbourne', 'endpoint': 'nova.rc.nectar.org.au'}, 'credentials': {'access_key': '4fe68d160f60423bb0ff819f28f162f8', 'secret_key': '3e153f93268043b3b1717825921ff706'}, 'key': {'name': 'team25'}, 'security_groups': [{'name': 'ssh'}, {'name': 'default'}, {'name': 'http'}], 'system_types': [{'name': 'streamer', 'instance_type': 'm2.small', 'image_id': 'ami-86f4a44c', 'placement': 'melbourne-qh2', 'security_groups': ['ssh', 'default']}, {'name': 'searcher', 'instance_type': 'm2.small', 'image_id': 'ami-86f4a44c', 'placement': 'melbourne-qh2', 'security_groups': ['ssh', 'default']}, {'name': 'tweetdb', 'instance_type': 'm2.small', 'image_id': 'ami-86f4a44c', 'placement': 'melbourne-qh2', 'security_groups': ['ssh', 'default']}, {'name': 'webserver', 'instance_type': 'm2.small', 'image_id': 'ami-86f4a44c', 'placement': 'melbourne-qh2', 'security_groups': ['ssh', 'default', 'http']}]}

region = RegionInfo(name=jconfig['region']['name'], endpoint=jconfig['region']['endpoint'])

"""2.1 connect to nectar"""
print('Connecting to Nectar')
logging.info('Connecting to Nectar')
ec2_conn = boto.connect_ec2(aws_access_key_id=jconfig['credentials']['access_key'],
                            aws_secret_access_key=jconfig['credentials']['secret_key'],
                            is_secure=True, region=region, port=PORT, path=PATH, validate_certs=False)

# attachVolume(ec2_conn, volume_id="vol-bf2e12d5", instance_id="i-8e287e3a")
attachVolume(ec2_conn, volume_id="vol-7d655e90", instance_id="i-8e287e3a")
# print('Connecting to Nectar finshed')
# images = ec2_conn.get_all_images()
#
resultset = ec2_conn.get_all_instances()
#
# print(type(resultset))

for reservation in resultset:
    print(type(reservation))
    instance = reservation.instances[0]
    print(instance.id)
    # typename = instance.tags['Type']
    # instance_nickname = instance.tags['Name']
    # print("instance_nickname:" + instance_nickname)
    # print(typename)

    # i - 551b982c


# for img in images:
#     print('Image id: {}, image name: {}'.format(img.id, img.name))

# reservation = ec2_conn.run_instances(max_count=1,
#                                      image_id='ami-190a1773',
#                                      placement='melbourne-qh2',
#                                      key_name='group25',
#                                      instance_type='m2.small',
#                                      security_groups=["ssh","default"])
# instance = reservation.instances[0]
# print(instance)
# addTag(instance, 'Name','Database-1')
# addTag(instance, 'Type','database')