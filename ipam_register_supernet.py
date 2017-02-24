#!/usr/bin/env python

import logging
import sys
import consulate
import json
import netaddr
import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-p", "--port", help="The TCP port for the rest server.",
                    default=8500, type=int)
PARSER.add_argument("-s", "--consul_server", help="The consul server hostname.",
                    default='127.0.0.1')
PARSER.add_argument("-c", "--consul_dc", help="The consul data center name.",
                    default='dc1')
PARSER.add_argument("-n","--cidr_block",help="Cidr block to register")

PARSER.add_argument("-r","--resize_bits",help="Resize bits")
PARSER.add_argument("-e","--environment",help="Environment",default='localhost')

ARGS = PARSER.parse_args()

def _error_and_exit(msg):
   logging.error(msg)
   sys.exit(-1)

if ( ARGS.cidr_block is None ):
    _error_and_exit("Error: cidr_block is mandatory field")
if ( ARGS.resize_bits is None ):
    _error_and_exit("Error: resize_bits should be integer between 16 to 32")


cidr_block=ARGS.cidr_block
#Hack to play nice with Consul 
c_block=cidr_block.replace("/","_")
environment=ARGS.environment

#Trim / as need only number
resize_bits=int(ARGS.resize_bits.replace("/",""))

if resize_bits < 16 or resize_bits >32:
  _error_and_exit("Error: Invalid resize_bits")


cserver=consulate.Session(host=ARGS.consul_server, datacenter=ARGS.consul_dc)
if cserver is None:
  _error_and_exit("Error Not able to get Consul Connection")
else:
  logging.debug("Got Connection for Consul")

k="ipam/data/supernets/{0}".format(c_block)
data=None
try:
   data=cserver.kv.get(k)
except Exception as err:
   _error_and_exit("Error Occured : {0} ".format(err))

if data == None or data == "":
   #Looks like we dont have subnets registered in consul"
   #Register the cidr in supernet section"
    try: 
      cserver.kv.set("ipam/data/supernets/{0}".format(c_block),"a=,b=,c=")
      print("Registered Superblock".format(cidr_block))
    except Exception as err:
      _error_and_exit("Failed to register supernet {0} ".format(err))
else:
   print("Looks like we have supernets already registered {0} ".format(k))
   _error_and_exit("Exiting as its dangerous....")

#Now Split into bits
network=netaddr.IPNetwork(cidr_block) 
count=0
for subnet in network.subnet(resize_bits):
   #Hack for consul
   s_cidr=str(subnet).replace("/","_")
   skey=("ipam/networkspace/{0}/subnets/{1}".format(c_block,s_cidr))
   logging.debug("Registering subnet {0} ".format(subnet))
   #status,customer
   cserver.kv.set(skey,"UNKNOWN,UNKNOWN")
   count=count+1


print("Registered {0} Subnets  in IPAM".format(count))
