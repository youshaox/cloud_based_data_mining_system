#!bin/bash
# ubuntu 环境安装

# 1. 相关环境安装
# 1.1 系统文件夹
mkdir ~/workspace
mkdir ~/workspace/data

# 2. 系统配置


# 3. 相关软件
# 3.1 git代码
sudo apt install git -y
cd ~/workspace/
# todo key-token 使用配置文件
git clone https://youshaox:3b1d9481ab7a7b30a4c5a32549501151b92f0b0f@github.com/youshaox/cluster_and_cloud_2018.git



# 3.2 python3-pip
sudo apt-get update
sudo apt install python3-pip -y
# pip3 install --upgrade pip

# 3.2.1 pip
pip3 install tweepy
pip3 install couchdb


# 3.3 couchdb


# 4. 项目逻辑
