"""
Main script for controller.
Usage: python3 <controller.py> <action> <value_type> <value> <target>
Where: <action>         -- create / terminate / delete / attach / unattach
        <value_type>      -- instance / volume / snapshot
        <target>    -- default / streamer-1 (instance-value)
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
        logging.error(
            'invalid number of arguments: <controller.py> <action> <value_type> <value> <target>'
        )
        sys.exit(ERROR)
    action = sys.argv[1]
    value_type = sys.argv[2]
    value = sys.argv[3]
    target = sys.argv[4]
    return action, value_type, value, target


class Controller():
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.region = RegionInfo(value='melbourne', endpoint='nova.rc.nectar.org.au')
        self.ec2_conn = boto.connect_ec2(aws_access_key_id=aws_access_key_id,
                                         aws_secret_access_key=aws_secret_access_key,
                                is_secure=True, region=self.region, port=8773, path='/services/Cloud', validate_certs=False)
        self.jinstances_info = {}

    def add_tag(self, instance, key, value):
        """
        add tag for the instance
        :param instance:
        :param key:
        :param value:
        :return:
        """
        status = instance.update()
        while status != 'running':
            time.sleep(SLEEP_TIME)
            status = instance.update()
        instance.add_tag(key, value)

    def create_instance(self, instance_value):
        reservation = self.ec2_conn.run_instances(image_id='ami-190a1773',
                               placement='melbourne-qh2',
                               key_value='group25',
                               instance_type='m2.small',
                               security_groups=['ssh', 'default'])
        instance = reservation.instances[0]
        self.add_tag(instance, 'value', instance_value)
        while (instance.update() != "running"):
            time.sleep(SLEEP_TIME)
        logging.info('Create an instance:' + instance_value)


    def terminate_instance(self, instance_value):
        id = self.jinstances_info[instance_value]['instance_id']
        self.ec2_conn.terminate_instances(id)
        logging.info('Terminate the instance ' + instance_value)


    def get_instances_info(self):
        reservations = self.ec2_conn.get_all_reservations()
        for idx, res in enumerate(reservations):
            instance = res.instances[0]
            # print(idx, res.id, res.instances, res.instances[0].tags['Type'], res.instances[0].tags['value'])
            self.jinstances_info[instance.tags['value']] = {"res_id": res.id, "instance_id":instance.id}
        logging.info('3. Getting all info of the instances')
        return self.jinstances_info

    def show_volumes(self):
        curr_volumes = self.ec2_conn.get_all_volumes()
        for v in curr_volumes:
            print(v.id)
            print(v.status)
            print(v.zone)

    def attach_volume(self):
        pass


    def create_volume(self, size):
        logging.info('Create a volume with size(G):' + str(size))
        return self.ec2_conn.create_volume(size, "melbourne-qh2")

    def create_snapshot(self, vol_id):
        suffix = datetime.datetime.now().strftime("%m%d%H%M")
        snapshot_value = self.vol_id + suffix
        return self.ec2_conn.create_snapshot(vol_id, snapshot_value)


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
        if action == "create":
            controller.create_volume(int(value))
        elif action == "delete":
            pass
        else:
            logging.error("Unknown action: please select create/terminate")
            sys.exit(ERROR)

    elif value_type == "snapshot":
        if action == "create":
            pass
        elif action == "terminate":
            pass
        else:
            logging.error("Unknown action: please select create/terminate")
            sys.exit(ERROR)
    else:
        logging.error("Unknown value_type: please select instance/volume/snapshot")
        sys.exit(ERROR)



if __value__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s-[line:%(lineno)d]-%(levelvalue)s: %(message)s')

    action, value_type, value, target = check_arguments()
    logging.info("1. Check arguments sucess")

    controller = Controller(aws_access_key_id='238656dab65d438390d91f689a08cb55',aws_secret_access_key='e5734f0116ab4104b1b24c3f8dd651b0')
    logging.info("2. Connection to Nectar sucess")
    # 必须有
    controller.get_instances_info()

    logging.info("4. Take actions")
    run(controller, action, value_type, value, target)
    logging.info("Finish!")

    # print(controller.jinstances_info)
    # for jinstance_info in controller.jinstances_info:
    #     print(jinstance_info)

    # controller.terminate_instance('streamer-1')
    # controller.create_instance('streamer-1')
    # print(datetime.datetime.now().strftime("%m%d%H%M"))

    # controller.create_volume(70)
    # controller.show_volumes()