"""
Main script for controller.
Usage: python3 <controller.py> <action> <value_type> <value> <target>
Where: <action>         -- create / terminate / delete / attach / unattach
        <value_type>      -- instance / volume / snapshot
        <target>    -- default / streamer-1 (instance-name)
        e.g:
        create instance streamer-1 default
        terminate instance streamer-1 default
        attach volume 40 streamer-1
        delete volume vol-f5a3a3f2
        create snapshot vol-f5a3a3f2
        delete snapshot vol-f5a3a3f2
"""

import boto
import os
import time
import datetime
import boto.exception
import logging
import sys
from boto.ec2.regioninfo import RegionInfo

SLEEP_TIME = 5
NUM_ARGS = 5
ERROR = 2

def check_arguments():
    if len(sys.argv) != NUM_ARGS:
        logging.error('invalid number of arguments: <controller.py> <action> <value_type> <value> <target>')
        sys.exit(ERROR)
    action = sys.argv[1]
    value_type = sys.argv[2]
    value = sys.argv[3]
    target = sys.argv[4]
    return action, value_type, value, target


class Controller():
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.region = RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')
        self.ec2_conn = boto.connect_ec2(aws_access_key_id=aws_access_key_id,
                                         aws_secret_access_key=aws_secret_access_key,
                                is_secure=True, region=self.region, port=8773, path='/services/Cloud', validate_certs=False)
        self.jinstances_info = {}

    def add_tag(self, instance, key, name):
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

    def create_instance(self, instance_name):
        reservation = self.ec2_conn.run_instances(image_id='ami-190a1773',
                               placement='melbourne-qh2',
                               key_name='group25',
                               instance_type='m1.medium',
                               security_groups=['ssh', 'default'])
        instance = reservation.instances[0]
        self.add_tag(instance, 'Name', instance_name)
        while (instance.update() != "running"):
            time.sleep(SLEEP_TIME)
        logging.info('Create an instance:' + instance_name)

    def terminate_instance(self, instance_name):
        id = self.jinstances_info[instance_name]['instance_id']
        self.ec2_conn.terminate_instances(id)
        logging.info('Terminate the instance ' + instance_name)

    def get_instances_info(self):
        reservations = self.ec2_conn.get_all_reservations()
        for idx, res in enumerate(reservations):
            instance = res.instances[0]

            # 并不是所有的都有名字
            try:
                self.jinstances_info[instance.tags['Name']] = {"res_id": res.id, "instance_id":instance.id}
            except KeyError:
                continue
        logging.info('3. Getting all info of the instances')
        return self.jinstances_info

    def show_volumes(self):
        curr_volumes = self.ec2_conn.get_all_volumes()
        for v in curr_volumes:
            print(v.id)
            print(v.status)
            print(v.zone)

    def createVolume(self, size):
        logging.info('Create a volume with size(G): ' + str(size))
        return self.ec2_conn.create_volume(size, "melbourne-qh2")

    def detachVolume(self, volume_id):
        return self.ec2_conn.detach_volume(volume_id)

    def deleteVolume(self, volume_id):
        volumes = self.ec2_conn.get_all_volumes()
        if self.detachVolume(volume_id):
            logging.info("Succussfully detach the volume" + volume_id)
            for volume in volumes:
                if volume.id == volume_id:
                    while volume.attachment_state() != None:
                        time.sleep(SLEEP_TIME)
                        volume.update()
            if self.ec2_conn.delete_volume(volume_id):
                # todo 等delete完以后再退出
                logging.info("Succussfully delete the volume" + volume_id)
            else:
                logging.error("Fail to delete the volume " + volume_id)
        else:
            logging.error("Fail to detach the volume" + volume_id)
            sys.exit(ERROR)

    def attachVolume(self, volume_id, instance_id):
        return self.ec2_conn.attach_volume(volume_id, instance_id, "/dev/vdc")

    def createSnapshot(self, volume_id):
        suffix = datetime.datetime.now().strftime("%m%d%H%M")
        snapshot_name = volume_id + suffix
        return self.ec2_conn.create_snapshot(volume_id, snapshot_name)

    def deleteSnapshot(self, snapshot_id):
        return self.ec2_conn.delete_snapshot(snapshot_id)


def run(controller, action, value_type, value, target):
    controller = controller
    if value_type == "instance":
        if action == "create":
            controller.create_instance(value)
        elif action == "terminate":
            controller.terminate_instance(value)
        else:
            logging.error("Unknown action: please select from \"create/terminate\"")
            sys.exit(ERROR)
    elif value_type == "volume":
        if action == "attach":
            volume = controller.createVolume(int(value))
            volume_id = volume.id
            target_instance_id = controller.jinstances_info[target]['instance_id']
            controller.attachVolume(volume_id, target_instance_id)
            logging.info("Attach " + str(volume_id) + " to " + str(target_instance_id))
        elif action == "delete":
            controller.deleteVolume(value)
            logging.info("Delete " + str(value))
        else:
            logging.error("Unknown action: please select from \"attach/unattach/delete\"")
            sys.exit(ERROR)

    elif value_type == "snapshot":
        if action == "create":
            controller.createSnapshot(value)
        elif action == "delete":
            controller.deleteSnapshot(value)
        else:
            logging.error("Unknown action: please select from \"create/delete\"")
            sys.exit(ERROR)
    else:
        logging.error("Unknown value_type: please select \"instance/volume/snapshot\"")
        sys.exit(ERROR)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s-[line:%(lineno)d]-%(levelname)s: %(message)s')

    action, value_type, value, target = check_arguments()
    logging.info('1. Check arguments success')

    # controller = Controller(aws_access_key_id='238656dab65d438390d91f689a08cb55',aws_secret_access_key='e5734f0116ab4104b1b24c3f8dd651b0')
    controller = Controller(aws_access_key_id='4fe68d160f60423bb0ff819f28f162f8',aws_secret_access_key='3e153f93268043b3b1717825921ff706')
    logging.info("2. Connection to Nectar sucess")
    # 必须有
    controller.get_instances_info()

    logging.info("4. Take actions")
    run(controller, action, value_type, value, target)
    logging.info("Finish!")