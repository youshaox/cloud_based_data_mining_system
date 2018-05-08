#!/usr/bin/env bash
sudo mkdir /data
sudo touch /data/test

#todo 需要get相应的disk名字
sudo mkfs.ext4 /dev/vdc

## 不可用
#sudo su;echo "/dev/vdc /data ext4 0 0" >> /etc/fstab
#
sudo mount /dev/vdc /data

