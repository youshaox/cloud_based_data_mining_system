"""
Script for controller of the instances, volumes and snapshots.
Usage: python3 <controller.py> <action> <value_type> <value> <target>
Where: <action>         -- create / terminate / delete / attach / recover
        <value_type>      -- instance / volume / snapshot
        <value>           -- depends on value_type and action
        <target>    -- default / streamer (instance-name)
        e.g:
        get instance info default
        create instance instance-name default
        terminate instance i-d7da2302 default
        get volume info default
        create volume 40 i-d7da2302
        delete volume vol-f5a3a3f2 default
        create snapshot vol-f5a3a3f2 default
        delete snapshot snap-f5a3a3f2 default
        recover snapshot snap-f5a3a3f2 streamer
"""

import boto
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
        logging.error('invalid number of arguments: <controller.py> <action> <value_type> <value> <target>' +
                      "\nhelp: python controller.py help instance/volume/snapshot default default")
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

    def terminate_instance(self, instance_id):
        logging.info('Terminate the instance ' + instance_id)
        return self.ec2_conn.terminate_instances(instance_id)

    def show_instances(self):
        cur_reservations = self.ec2_conn.get_all_reservations()
        for idx, res in enumerate(cur_reservations):
            instance = res.instances[0]
            print({"instance_id": instance.id,
                   "instance_state": instance.state,
                   "instance_placement": instance.placement,
                   "instance_tags": instance.tags
                   })

    def get_instances(self):
        instance_list = list()
        cur_reservations = self.ec2_conn.get_all_reservations()
        for idx, res in enumerate(cur_reservations):
            instance = res.instances[0]
            instance_list.append({"instance_id": instance.id,
                   "instance_state": instance.state,
                   "instance_placement": instance.placement,
                   "instance_tags": instance.tags
                   })
        return instance_list

    def show_volumes(self):
        curr_volumes = self.ec2_conn.get_all_volumes()
        for volume in curr_volumes:
            print({"volume_id":volume.id,
                   "volume_create_time":volume.create_time,
                   "volume_size": volume.size,
                   "volume_status":volume.status,
                   "volume_zone":volume.zone})

    def show_snapshots(self):
        curr_snapshots= self.ec2_conn.get_all_snapshots()
        for snapshot in curr_snapshots:
            print({"snapshot_id":snapshot.id,
                   "volume_id":snapshot.volume_id,
                   "snapshot_size": snapshot.volume_size,
                   "start_time": snapshot.start_time,
                   "snapshot_status":snapshot.status
                   })

    def createVolume(self, size):
        logging.info('Create a volume with size(G): ' + str(size))
        return self.ec2_conn.create_volume(size, "melbourne-qh2")

    def detachVolume(self, volume_id):
        return self.ec2_conn.detach_volume(volume_id)

    def deleteVolume(self, volume_id):
        volumes = self.ec2_conn.get_all_volumes()
        try:
            detach = self.detachVolume(volume_id)
        except boto.exception.EC2ResponseError:
            detach = True
        if detach:
            logging.info("Succussfully detach the volume" + volume_id)
            for volume in volumes:
                if volume.id == volume_id:
                    while volume.attachment_state() != None:
                        time.sleep(SLEEP_TIME)
                        volume.update()
            if self.ec2_conn.delete_volume(volume_id):
                # todo exit wafter the deleteing finish
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
        snapshot = self.ec2_conn.create_snapshot(volume_id, snapshot_name)
        logging.info("Create the snapshot:" + str(snapshot.id) + " of the volume:" + str(volume_id))
        return snapshot

    def deleteSnapshot(self, snapshot_id):
        logging.info("Delete the snapshot:" + str(snapshot_id))
        return self.ec2_conn.delete_snapshot(snapshot_id)

    def recoverSnapshot(self, snapshot_id, instance_id):
        snapshot = self.ec2_conn.get_all_snapshots([snapshot_id])[0]
        new_vol = snapshot.create_volume('melbourne-qh2')
        while new_vol.status != "available":
            time.sleep(SLEEP_TIME)
            new_vol.update()

        if self.attachVolume(new_vol.id, instance_id):
            logging.info("Recover snapshot: " + str(snapshot_id) + " and attach the new volume " + str(new_vol.id) +" to instancde: " + str(instance_id))
        else:
            logging.error("Recover snapshot: fail in attach the new volume:" + str(new_vol.id))

def run(controller, action, value_type, value, target):
    """
    run the actual command
    :param controller:
    :param action:
    :param value_type:
    :param value:
    :param target:
    :return:
    """
    controller = controller
    if value_type == "instance":
        if action == "create":
            controller.create_instance(value)
        elif action == "terminate":
            controller.terminate_instance(value)
        elif action == "get":
            controller.show_instances()
        else:
            logging.error("\nUnknown action: please select from \"create/terminate/get\"\n" +
                          "e.g:\n" +
                          "python controller.py get instance info default\n"+
                          "python controller.py create instance <nickname> default\n" +
                          "python controller.py terminate instance <instance-id> default\n")
            sys.exit(ERROR)
    elif value_type == "volume":
        if action == "create":
            volume = controller.createVolume(int(value))
            volume_id = volume.id
            target_instance_id = target
            controller.attachVolume(volume_id, target_instance_id)
            logging.info("Attach " + str(volume_id) + " to " + str(target_instance_id))
        elif action == "delete":
            controller.deleteVolume(value)
            logging.info("Delete " + str(value))
        elif action == "get":
            controller.show_volumes()
        else:
            logging.error("\nUnknown action: please select from \"create/delete/get\"\n" +
                          "e.g:\n" +
                          "python controller.py get volume info default\n" +
                          "python controller.py create volume <size> <instance-id>\n" +
                          "python controller.py delete volume <vol-id> default\n")
            sys.exit(ERROR)

    elif value_type == "snapshot":
        if action == "create":
            controller.createSnapshot(value)
        elif action == "delete":
            controller.deleteSnapshot(value)
        elif action == "recover":
            controller.recoverSnapshot(value, target)
        elif action == "get":
            controller.show_snapshots()
        else:
            logging.error("Unknown action: please select from \"create/delete\"")
            logging.error("\nUnknown action: please select from \"attach/delete/get\"\n" +
                          "e.g:\n" +
                          "python controller.py recover snapshot <snap-id> <instance-id>\n" +
                          "python controller.py create snapshot <vol-id> default\n" +
                          "python controller.py delete snapshot <snap-id> default\n")
            sys.exit(ERROR)
    else:
        logging.error("help:\npython controller.py help instance/volume/snapshot")
        sys.exit(ERROR)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,format='%(asctime)s-[line:%(lineno)d]-%(levelname)s: %(message)s')

    action, value_type, value, target = check_arguments()
    logging.info('1. Check arguments success')
    # shawn personal
    # controller = Controller(aws_access_key_id='238656dab65d438390d91f689a08cb55',aws_secret_access_key='e5734f0116ab4104b1b24c3f8dd651b0')
    # project
    controller = Controller(aws_access_key_id='4fe68d160f60423bb0ff819f28f162f8',aws_secret_access_key='3e153f93268043b3b1717825921ff706')
    logging.info("2. Connection to Nectar sucess")

    logging.info("3. Trigger the actions")
    run(controller, action, value_type, value, target)
    logging.info("Finish!")