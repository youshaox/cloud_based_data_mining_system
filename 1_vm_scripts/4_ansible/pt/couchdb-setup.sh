#!/bin/sh
cd /data/workspace
wget http://apache.mirror.amaze.com.au/couchdb/source/2.1.1/apache-couchdb-2.1.1.tar.gz
tar -zxvf apache-couchdb-2.1.1.tar.gz
cd apache-couchdb-2.1.1/
sudo rm -rf /usr/lib/erlang/man
./configure && make release

# configure
cd /data/workspace/apache-couchdb-2.1.1/rel/couchdb/etc
sed -i "s/;admin = mysecretpassword/admin = admin/g" local.ini
sed -i 's/127.0.0.1/0.0.0.0/g' default.ini

cd /data/workspace/apache-couchdb-2.1.1/rel/couchdb/releases/2.1.1;rm -rf sys.config
cat > sys.config << EOF
[
    {lager, [
        {error_logger_hwm, 1000},
        {error_logger_redirect, true},
        {handlers, [
            {lager_console_backend, [debug, {
                lager_default_formatter,
                [
                    date, " ", time,
                    " [", severity, "] ",
                    node, " ", pid, " ",
                    message,
                    "\n"
                ]
            }]}
        ]},
        {inet_dist_listen_min, 9100},
        {inet_dist_listen_max, 9200}
    ]}
].
EOF