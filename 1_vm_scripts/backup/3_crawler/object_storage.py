from boto.ec2.regioninfo import RegionInfo
import boto

s3_conn = boto.connect_s3(aws_access_key_id='4fe68d160f60423bb0ff819f28f162f8',
                          aws_secret_access_key='3e153f93268043b3b1717825921ff706',
                          is_secure=True,
                          host='swift.rc.nectar.org.au',
                          port=8888,
                          path='/')

buckets = s3_conn.get_all_buckets()
for bucket in buckets:
    print('Bucket name {} '.format(bucket.name))