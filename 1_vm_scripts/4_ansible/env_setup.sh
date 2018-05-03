#!/usr/bin/env bash
sudo apt update
sudo apt install python3-pip -y
sudo pip3 install ansible



ansible masters -m shell -a "pwd" --private-key=/home/ec2-user/openshift-aws-installer-image/ck_workshop.pem -u ec2-user
