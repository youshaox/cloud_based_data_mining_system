from boto.ec2.regioninfo import RegionInfo
import boto

s3_conn = boto.connect_s3(aws_access_key_id='REMOVED',
                          aws_secret_access_key='REMOVED',
                          is_secure=True,
                          host='swift.rc.nectar.org.au',
                          port=8888,
                          path='/')

buckets = s3_conn.get_all_buckets()
for bucket in buckets:
    print('Bucket name {} '.format(bucket.name))