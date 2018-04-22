# Readme

This part is for the twitter crawler.



# 挑战

**爬虫策略**

1. 去重
   * 解决方式:
     1. ==将tweets数据中id_str作为couchDB的id，如果存数据出错误了，那么就认为重复了。==
     2. 使用bloomfilter，做一遍hash
     3. 检查下id_str是否在couchDB中（效率太低了）
2. 爬虫，是否使用多代理IP
   1. 考虑项目时间，不使用代理池。每一台机器一个stream，一个search api。两个爬虫，使用不同的token。采取命令行argument的方式。（考虑到twitter对APP的限制，使用6个不同的token，因为有rate limit for search API）.

