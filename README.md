# ip-aggregator
Gather, filter, sort, and aggregate IPs from arguments, stdin, or both. Useful for making route and filter tables smaller.

Does the opposite of [ip-deaggregator](https://github.com/andrewtwin/ip-deaggregator)

## Usage
```
usage: ip-aggregator [-h] [-s] [-f INCLUDE_FILTER] [-F EXCLUDE_FILTER] [-q] [-d OUTPUT_DELIMITER]
                     [-m {prefix,net,wildcard}] [-S] [-R] [-A] [-u] [-c] [-V] [-l]
                     [subnet ...]

Extract, filter, sort, and aggregate subnets.
Copyright (C) 2021 Andrew Twin - GNU GPLv3 - see version for more information.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         Print version and licence information and exit
  -l, --list-aliases    List IP aliases and exit. Alises can be used in place of regular addresses. Supports -m/--mask-
                        type flag.

input options:
  How to provide input.

  subnet                Subnets or ip ranges to aggregate.
  -s, --stdin           Extract addresses from stdin (only IPv4 addresses supported, aliases not supported).

filter options:
  Filering of input networks, includes are processed before excludes.

  -f INCLUDE_FILTER, --include-filter INCLUDE_FILTER
                        Filter results to include subnets of a network. Multiple filters can be specified.
  -F EXCLUDE_FILTER, --exclude-filter EXCLUDE_FILTER
                        Filter results to exclude subnets of a network. Multiple filters can be specified.

output options:
  How to display output.

  -q, --quiet           Only produce output, no other information.
  -d OUTPUT_DELIMITER, --output-delimiter OUTPUT_DELIMITER
                        Sets the output delimeter, default is a new line.
  -m {prefix,net,wildcard}, --mask-type {prefix,net,wildcard}
                        Use prefix length (default), net mask, or wildcard mask.
  -S, --sort            Sort the output, ascending order.
  -R, --reverse-sort    Sort the output, decending order.
  -A, --no-aggregate    Don't aggregate subnets. Just output valid networks and addresses.
  -u, --unique          Remove duplicates from the output, redundant without -A/--no-aggregate.
  -c, --count           Only output the count of the networks/IPs.

v0.6.3
```
## Installation
Download the python zipapp from the [releases](https://github.com/andrewtwin/ip-aggregator/releases) page.

## Examples

Combine addresses from both stdin and as arguments.
```
echo '192.168.0.0/24,192.168.2.0/24' | ip-aggregator -s 192.168.1.0/24 192.168.3.0/24
Input 4 addresses:
192.168.0.0/24
192.168.2.0/24
192.168.1.0/24
192.168.3.0/24
------------------
Output 1 addresses:
192.168.0.0/22
```

With alternate masks:
```
echo '192.168.0.0/24,192.168.2.0/24' | ip-aggregator -s 192.168.1.0/24 192.168.3.0/24 -m net
Input 4 addresses:
192.168.0.0/255.255.255.0
192.168.2.0/255.255.255.0
192.168.1.0/255.255.255.0
192.168.3.0/255.255.255.0
------------------
Output 1 addresses:
192.168.0.0/255.255.252.0
```

```
echo '192.168.0.0/24,192.168.2.0/24' | ip-aggregator -s 192.168.1.0/24 192.168.3.0/24 -m wildcard
Input 4 addresses:
192.168.0.0/0.0.0.255
192.168.2.0/0.0.0.255
192.168.1.0/0.0.0.255
192.168.3.0/0.0.0.255
------------------
Output 1 addresses:
192.168.0.0/0.0.3.255
```

With ranges of IP addresses:
```
ip-aggregator 10.0.0.0-10.0.7.255 192.168.0.0-192.168.3.255
Input 2 addresses:
10.0.0.0/21
192.168.0.0/22
------------------
Output 2 addresses:
10.0.0.0/21
192.168.0.0/22
```

Just the output:
```
echo '192.168.0.0/24,192.168.2.0/24' | ip-aggregator -s 192.168.1.0/24 192.168.3.0/24 -q
192.168.0.0/22
```

Extract subnets and addresses from text:
```
echo "These are IPs 10.0.0.1 10.0.0.2, 10.0.0.3 and a network 10.0.0.0/24" | ip-aggregator -s
Input 4 addresses:
10.0.0.1/32
10.0.0.2/32
10.0.0.3/32
10.0.0.0/24
------------------
Output 1 addresses:
10.0.0.0/24
```

Don't aggrerate output, just extract and validate:
```
echo "These are IPs 10.0.0.1 10.0.0.2, 10.0.0.3 and a network 10.0.0.0/24" | ip-aggregator -s -A
Input 4 addresses:
10.0.0.1/32
10.0.0.2/32
10.0.0.3/32
10.0.0.0/24
------------------
Not aggregating subnets as requested.
------------------
Output 4 addresses:
10.0.0.1/32
10.0.0.2/32
10.0.0.3/32
10.0.0.0/24
```

Apply filters to include subnets of a network:
```
echo "10.0.0.1, 172.16.0.1, 192.168.0.1" | ip-aggregator -s -f 10.0.0.0/8
Input 3 addresses:
10.0.0.1/32
172.16.0.1/32
192.168.0.1/32
------------------
Including only addresses in: 10.0.0.0/8
------------------
Output 1 addresses:
10.0.0.1/32
```

Or apply filters to exlcude subnets:
```
echo "10.0.0.1, 172.16.0.1, 192.168.0.1" | ip-aggregator -s -F 10.0.0.0/8
Input 3 addresses:
10.0.0.1/32
172.16.0.1/32
192.168.0.1/32
------------------
Excluding addresses in: 10.0.0.0/8
------------------
Output 2 addresses:
172.16.0.1/32
192.168.0.1/32
```

Sort output:
```
echo "10.0.0.1, 192.168.0.2, 172.16.0.1, 10.0.0.2, 192.168.0.1" | ip-aggregator -s -S
Input 5 addresses:
10.0.0.1/32
192.168.0.2/32
172.16.0.1/32
10.0.0.2/32
192.168.0.1/32
------------------
Output 5 addresses:
10.0.0.1/32
10.0.0.2/32
172.16.0.1/32
192.168.0.1/32
192.168.0.2/32
```

Extract IPs in different formats from stdin, filter for class A addresses and a class C network, exclude a class A network, skip aggregating subnets but remove duplicats, and sort the output.
```
echo "10.0.0.1/255.255.255.255, 10.0.0.1 192.168.0.2, 172.16.0.1, ip=10.0.0.2 ip=10.0.0.2/0.0.0.0, 192.168.0.1,127.0.0.1;10.100.20.0/255.255.255.0 10.100.30.0/0.0.0.255 (10.100.40.0/24)[192.168.20.128/25,10.0.0.5];10.0.0.3;10.0.0.20;10.50.1.1;10.90.0.0/16;10.23.20.1;10.32.6.2"\
| ip-aggregator -s -A -u -f A -f 192.168.0.0/255.255.255.0 -F 10.100.0.0/16 -S
WARNING: Address 10.0.0.2/0.0.0.0 from stdin is not a valid IPv4 address or network, ignoring
Input 18 addresses:
10.0.0.1/32
10.0.0.1/32
192.168.0.2/32
172.16.0.1/32
10.0.0.2/32
192.168.0.1/32
127.0.0.1/32
10.100.20.0/24
10.100.30.0/24
10.100.40.0/24
192.168.20.128/25
10.0.0.5/32
10.0.0.3/32
10.0.0.20/32
10.50.1.1/32
10.90.0.0/16
10.23.20.1/32
10.32.6.2/32
------------------
Including only addresses in: 10.0.0.0/8, 192.168.0.0/24
Excluding addresses in: 10.100.0.0/16
Not aggregating subnets as requested.
------------------
Output 11 addresses:
10.0.0.1/32
10.0.0.2/32
10.0.0.3/32
10.0.0.5/32
10.0.0.20/32
10.23.20.1/32
10.32.6.2/32
10.50.1.1/32
10.90.0.0/16
192.168.0.1/32
192.168.0.2/32
```

And more!
