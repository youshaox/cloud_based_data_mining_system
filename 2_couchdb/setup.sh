#!/bin/sh
# 1. 安装文件
sudo apt-get --no-install-recommends -y install build-essential pkg-config runit erlang libicu-dev libmozjs185-dev libcurl4-openssl-dev

# 2. 目录
sudo mkdir -p /data/workspace
sudo chown -R ubuntu:ubuntu /data
cd /data/workspace
wget http://apache.mirror.amaze.com.au/couchdb/source/2.1.1/apache-couchdb-2.1.1.tar.gz
tar -zxvf apache-couchdb-2.1.1.tar.gz
cd apache-couchdb-2.1.1/
./configure && make release

# 3. 配置
cd /data/workspace/apache-couchdb-2.1.1/rel/couchdb/etc;sed -i "s/;admin = mysecretpassword/admin = admin/g" local.ini
sed -i 's/127.0.0.1/0.0.0.0/g' default.ini

cd /data/workspace/apache-couchdb-2.1.1/rel/couchdb/releases/2.1.1
rm -rf sys.config
echo "[
    {lager, [
        {error_logger_hwm, 1000},
        {error_logger_redirect, true},
        {handlers, [
            {lager_console_backend, [debug, {group25.pem
                lager_default_formatter,
                [
                    date, \" \", time,
                    \" [\", severity, \"] \",
                    node, \" \", pid, \" \",
                    message,
                    \"\\n\"
                ]
            }]}
        ]},
        {inet_dist_listen_min, 9100},
        {inet_dist_listen_max, 9200}
    ]}
]." >> sys.config

# todo 改couchdb1, ip
# my ip: 115.146.85.248
# remote ip: 115.146.85.226
#sed -i "s/-name couchdb@127.0.0.1/-name couchdb1@115.146.85.248/g" /data/workspace/apache-couchdb-2.1.1/rel/couchdb/etc/vm.args
sed -i "s/-name couchdb@127.0.0.1/-name ${couchdb1_name}@${couchdb1_ip}/g" /data/workspace/apache-couchdb-2.1.1/rel/couchdb/etc/vm.args


nohup sh /data/workspace/apache-couchdb-2.1.1/rel/couchdb/bin/couchdb 2>&1 &

########### todo 分开做，因为需要couchdb1, couchdb2建立完成
## 4. 节点
#
#curl -X POST -H "Content-Type: application/json" http://admin:admin@127.0.0.1:5984/_cluster_setup -d '{"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "admin", "password":"admin", "node_count":"3"}'
## todo 改remote ip
#curl -X POST -H "Content-Type: application/json" http://admin:admin@127.0.0.1:5984/_cluster_setup -d '{"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "admin", "password":"admin", "port": 5984, "node_count": "3", "remote_node": "115.146.85.226", "remote_current_user": "admin", "remote_current_password": "admin" }'
## todo 改remote ip
#curl -X POST -H "Content-Type: application/json" http://admin:admin@127.0.0.1:5984/_cluster_setup -d '{"action": "add_node", "host":"115.146.85.226", "port": "5984", "username": "admin", "password":"admin"}'
#curl -X POST -H "Content-Type: application/json" http://admin:admin@127.0.0.1:5984/_cluster_setup -d '{"action": "finish_cluster"}'

## adding nodes 改localhost 和 name和 remote ip
#curl -X PUT "http://admin:admin@115.146.85.248:5986/_nodes/couchdb2@115.146.85.226" -d {}

# 只需要在master上执行
curl -X PUT "http://admin:admin@${couchdb1_name}:5986/_nodes/${couchdb2_name}@${couchdb2_ip}" -d {}

