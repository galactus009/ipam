Mini IPAM

Consul is used as KV/Nosql Solution


Usage:
( Only Once)
```bash
$ ./ipam_register_supernet.py --cidr_block="192.168.0.0/16" --resize_bits="/24"
Registered 256 Subnets  in IPAM
```

(For new Customer registration)
```bash
(ipam) $./ipam_subnet_alloc.py --environment="prod"   --cidr_block="192.168.0.0/16"  --customer_id="test5"
192.168.0.0/24
```

(To Find allocation status)
```bash
(ipam) $./ipam_status.py --cidr_block="192.168.0.0/16"
Reserved customer_id: test5 with  192.168.0.0/24
Reserved customer_id: test51 with  192.168.1.0/24
Reserved customer_id: test41 with  192.168.10.0/24
Reserved customer_id: test9 with  192.168.100.0/24
Reserved customer_id: test78 with  192.168.101.0/24
```
