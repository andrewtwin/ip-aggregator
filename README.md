# ip-aggregator
Aggregate IPs from arguments, stdin, or both. Useful for making route and filter tables smaller.

Does the opposite of [ip-deaggregator](https://github.com/andrewtwin/ip-deaggregator)

## Usage
```
usage: ip-aggregator [-h] [-s] [-q] [-d OUTPUT_DELIMITER] [-m {prefix,net,wildcard}] [-A] [subnet ...]

Aggregate subnets.

positional arguments:
  subnet                Subnets to aggregate.

optional arguments:
  -h, --help            show this help message and exit
  -s, --stdin           Read addresses from stdin (only IPv4 addresses supported).
  -q, --quiet           Only produce output, no other information.
  -d OUTPUT_DELIMITER, --output-delimiter OUTPUT_DELIMITER
                        Sets the output delimeter, default is new line.
  -m {prefix,net,wildcard}, --mask-type {prefix,net,wildcard}
                        Use prefix length (default), net mask, or wildcard mask.
  -A, --no-aggregate    Don't aggregate subnets. Just output valid networks and addresses

ip-aggregator v0.3.0
```
## Installation
Download the python zipapp from the [releases](https://github.com/andrewtwin/ip-aggregator/releases) page.

## Examples

Combine addresses from both stdin and as arguments.
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

With alternate masks:
```
echo '192.168.0.0/24,192.168.2.0/24' | ip-aggregator -s 192.168.1.0/24 192.168.3.0/24 -m net
Input 4 addresses: 192.168.0.0/255.255.255.0
192.168.2.0/255.255.255.0
192.168.1.0/255.255.255.0
192.168.3.0/255.255.255.0
==================
192.168.0.0/255.255.252.0
==================
1 subnets total
```

```
echo '192.168.0.0/24,192.168.2.0/24' | ip-aggregator -s 192.168.1.0/24 192.168.3.0/24 -m wildcard
Input 4 addresses: 192.168.0.0/0.0.0.255
192.168.2.0/0.0.0.255
192.168.1.0/0.0.0.255
192.168.3.0/0.0.0.255
==================
192.168.0.0/0.0.3.255
==================
1 subnets total
```

Just the output:
```
echo '192.168.0.0/24,192.168.2.0/24' | ip-aggregator -s 192.168.1.0/24 192.168.3.0/24 -q
192.168.0.0/22
```

