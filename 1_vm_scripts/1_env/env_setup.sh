#!bin/bash
# ubuntu 环境安装

# 1. 相关环境安装
# 1.1 系统文件夹
mkdir ~/workspace
mkdir ~/workspace/data

# 2. 系统配置
sudo apt-get update

# 3. 相关软件
# 3.1 git代码
sudo apt install git -y
cd ~/workspace/
# todo key-token 使用配置文件
git clone https://youshaox:3b1d9481ab7a7b30a4c5a32549501151b92f0b0f@github.com/youshaox/cluster_and_cloud_2018.git



# 3.2 python3-pip

sudo apt install python3-pip -y
# pip3 install --upgrade pip

# 3.2.1 pip
pip3 install tweepy
pip3 install couchdb


# 3.3 couchdb
# 3.1.1
sudo apt-get install erlang -y

# host1 下 vi /etc/hosts
127.0.0.1 slave1
115.146.86.17 slave2

sudo hostnamectl set-hostname slave1
# host2 下 vi /etc/hosts
127.0.0.1 slave2
115.146.86.117 slave1

sudo hostnamectl set-hostname slave2

# host1下
erl -sname bus -setcookie 'brumbrum' -kernel inet_dist_listen_min 9100 -kernel inet_dist_listen_max 9200
# host2下
erl -sname car -setcookie 'brumbrum' -kernel inet_dist_listen_min 9100 -kernel inet_dist_listen_max 9200

# host1下
net_kernel:connect_node(car@slave2).
# host2下
net_kernel:connect_node(car@server1).



sudo service hostname start


telnet slave2 4369

# 4. 项目逻辑
