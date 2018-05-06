#!/usr/bin/env bash

sudo adduser --system --no-create-home --shell /bin/bash --group --gecos "CouchDB Administrator" couchdb
sudo cp -R /data/workspace/apache-couchdb-2.1.1/rel/couchdb /home/couchdb


sudo chown -R couchdb:couchdb /home/couchdb
sudo find /home/couchdb -type d -exec chmod 0770 {} \;
sudo sh -c 'chmod 0644 /home/couchdb/etc/*'
sudo mkdir /var/log/couchdb
sudo chown couchdb:couchdb /var/log/couchdb
sudo mkdir /etc/sv/couchdb
sudo mkdir /etc/sv/couchdb/log

# 路径
cd /data/workspace
cat > apache-couchdb-2.1.1/run << EOF
#!/bin/sh
export HOME=/home/couchdb
exec 2>&1
exec chpst -u couchdb /home/couchdb/bin/couchdb
EOF
# 路径
cat > apache-couchdb-2.1.1/log_run << EOF
#!/bin/sh
exec svlogd -tt /var/log/couchdb
EOF

sudo mv apache-couchdb-2.1.1/run /etc/sv/couchdb/run
sudo mv apache-couchdb-2.1.1/log_run /etc/sv/couchdb/log/run
sudo chmod u+x /etc/sv/couchdb/run
sudo chmod u+x /etc/sv/couchdb/log/run
sudo ln -s /etc/sv/couchdb/ /etc/service/couchdb
sleep 5
sudo sv status couchdb