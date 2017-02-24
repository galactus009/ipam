#!/usr/bin/env python
import logging
import sys
import consulate
import json
import netaddr
import argparse
import operator
from collections import defaultdict

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-p", "--port", help="The TCP port for the rest server.",
                    default=8500, type=int)
PARSER.add_argument("-s", "--consul_server", help="The consul server hostname.",
                    default='127.0.0.1')
PARSER.add_argument("-d", "--consul_dc", help="The consul data center name.",
                    default='dc1')
PARSER.add_argument("-n","--cidr_block",help="Cidr block to register")
PARSER.add_argument("-e","--environment",help="Environment",default='localhost')
PARSER.add_argument("-c","--customer_id",help="Customer ID",default="xyz")

ARGS = PARSER.parse_args()

def _error_and_exit(msg):
   logging.error(msg)
   sys.exit(-1)

if ( ARGS.cidr_block is None ):
    _error_and_exit("Error: cidr_block is mandatory field")


cidr_block=ARGS.cidr_block
#Hack to play nice with Consul 
c_block=cidr_block.replace("/","_")
environment=ARGS.environment
customer_id=ARGS.customer_id
cserver=consulate.Session(host=ARGS.consul_server, datacenter=ARGS.consul_dc)



#{0} --customer=<> --cidr_block=<> 
d={}
KEYSPACE=("ipam/networkspace/{0}/subnets/".format(c_block))
ipmap=defaultdict(int)

#Worst hack to get the bits
bits=""
for k,v in cserver.kv.find(KEYSPACE).items():
  #Do the Dirty Job
  parts=k.split("/")
  subnet_repr=parts[-1]
  subnet=subnet_repr.replace("_","/")
  (ip,bit)=subnet.split("/")
  bits=bit
  ipmap[ip]=v
 
t={}
for ip,val in sorted(ipmap.items(),key=operator.itemgetter(0)):
   parts=val.split(",")     
   t[ip]=dict([("customer_id" ,parts[0]),("status",parts[1])])
   if t[ip]["customer_id"] == customer_id:
      print "{0}/{1}".format(ip,bits)
      sys.exit(0)
   if t[ip]["customer_id"] == "UNKNOWN" or t[ip]["status"] == "UNKNOWN":
      FINAL=("{0},{1}".format(customer_id,"reserved"))
      FINAL_KEY="ipam/networkspace/{0}/subnets/{1}".format(c_block,ip+"_24")
      print "{0}/{1}".format(ip,bits)
      cserver.kv.set(FINAL_KEY,FINAL)
      sys.exit(0)
