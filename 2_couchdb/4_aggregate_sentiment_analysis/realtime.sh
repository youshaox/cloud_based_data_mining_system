#!/usr/bin/env bash
mkdir /data/log/view
# add the following line in the crontab: crontab -e
# then the result_data will be runned every one minute
*/1 * * * * cd /data/log/view; python3 /data/workspace/cluster_and_cloud_2018/2_couchdb/4_aggregate_sentiment_analysis/aggregrate_result.py >> /data/log/view/createview.log