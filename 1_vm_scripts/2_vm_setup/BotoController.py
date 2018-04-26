import boto
import os
import time
import boto.exception
from boto.ec2.regioninfo import RegionInfo

# 如何展示，只是提供相关的函数？还是要配置一个config，展示这个。
# 命令行的方式来 删除一个实例

class Ec2Controller():
    def __init__(self, aws_access_key_id='238656dab65d438390d91f689a08cb55',aws_secret_access_key='e5734f0116ab4104b1b24c3f8dd651b0'):
        self.region = RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')
        self.ec2_conn = boto.connect_ec2(aws_access_key_id='238656dab65d438390d91f689a08cb55',
                                    aws_secret_access_key='e5734f0116ab4104b1b24c3f8dd651b0',
                                is_secure=True, region=self.region, port=8773, path='/services/Cloud', validate_certs=False)
        self.jinstances_name = {}

    # todo 需要得到一个instance id和的对应关系

    def terminate_instance(self, id):
        self.ec2_conn.terminate_instances(id)


    def show_reservations(self):
        reservations = self.ec2_conn.get_all_reservations()
        for idx, res in enumerate(reservations):
            print(idx, res.id, res.instances)

    def show_volumes(self):
        curr_volumes = self.ec2_conn.get_all_volumes()
        for v in curr_volumes:
            print(v.id)
            print(v.status)
            print(v.zone)

    def create_volume(self, size=70):
        return self.ec2_conn.create_volume(size, "melbourne-qh2")

ec2controller = Ec2Controller(aws_access_key_id='238656dab65d438390d91f689a08cb55',aws_secret_access_key='e5734f0116ab4104b1b24c3f8dd651b0')
ec2controller.show_reservations()

# ec2controller.create_volume()
# ec2controller.show_volumes()