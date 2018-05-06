#!/usr/bin/env bash
# form the cluster
curl -X PUT "http://admin:cdurq48YWLWtZtd@115.146.85.177 :5986/_nodes/couchdb@115.146.85.170" -d {}
curl -X PUT "http://admin:cdurq48YWLWtZtd@${couchdb1_name}:5986/_nodes/${couchdb3_name}@${couchdb3_ip}" -d {}
curl -X PUT "http://admin:cdurq48YWLWtZtd@couchdb:5986/_nodes/${couchdb4_name}@${couchdb4_ip}" -d {}



curl -X GET admin:cdurq48YWLWtZtd@localhost:5984/_membership