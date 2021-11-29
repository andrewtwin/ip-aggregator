# ip-aggregator
Aggregate IPs from arguments, stdin, or both.

## Usage
```
usage: ip-aggregator [-h] [-s] [-q] [-d OUTPUT_DELIMITER] [-m {prefix,net,wildcard}] [subnet ...]

Aggregate subnets.

positional arguments:
  subnet                Subnets to aggregate.

optional arguments:
  -h, --help            show this help message and exit
  -s, --stdin           Read addresses from stdin (only IPv4 Addresses Supported).
  -q, --quiet           Only produce output, no other information.
  -d OUTPUT_DELIMITER, --output-delimiter OUTPUT_DELIMITER
                        Sets the output delimeter, default is new line.
  -m {prefix,net,wildcard}, --mask-type {prefix,net,wildcard}
                        Use prefix length (default), net mask, or wildcard mask.

ip-aggregator v0.2.0
```

## Examples

Combine an address from both stdin and as arguments.
```
echo '192.168.0.0/24,192.168.2.0/24' | ip-aggregator -s 192.168.1.0/24 192.168.3.0/24
Input 4 addresses: 192.168.0.0/24
192.168.2.0/24
192.168.1.0/24
192.168.3.0/24
==================
192.168.0.0/22
==================
1 subnets total
```

