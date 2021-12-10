# ip-aggregator
Gather, filter, sort, and aggregate IPs from arguments, stdin, or both. Useful for making route and filter tables smaller.

Does the opposite of [ip-deaggregator](https://github.com/andrewtwin/ip-deaggregator)

## Usage
```
usage: ip-aggregator [-h] [-s] [-q] [-d OUTPUT_DELIMITER] [-l] [-f INCLUDE_FILTER] [-F EXCLUDE_FILTER] [-m {prefix,net,wildcard}] [-S | -R] [-A] [-u] [-c] [subnet ...]

Extract, filter, sort, and aggregate subnets.
Copyright (C) 2021 Andrew Twin

positional arguments:
  subnet                Subnets to aggregate.

optional arguments:
  -h, --help            show this help message and exit
  -s, --stdin           Extract addresses from stdin (only IPv4 addresses supported).
  -q, --quiet           Only produce output, no other information.
  -d OUTPUT_DELIMITER, --output-delimiter OUTPUT_DELIMITER
                        Sets the output delimeter, default is new line.
  -l, --list-classes    List IP classes and exit. Classes can be used in filters, supports -m/--mask-type flag.
  -f INCLUDE_FILTER, --include-filter INCLUDE_FILTER
                        Filter results to include subnets of a network. Multiple filters can be specified.
  -F EXCLUDE_FILTER, --exclude-filter EXCLUDE_FILTER
                        Filter results to exclude subnets of a network. Multiple filters can be specified.
  -m {prefix,net,wildcard}, --mask-type {prefix,net,wildcard}
                        Use prefix length (default), net mask, or wildcard mask.
  -S, --sort            Sort the output, ascending order.
  -R, --reverse-sort    Sort the output, decending order.
  -A, --no-aggregate    Don't aggregate subnets. Just output valid networks and addresses.
  -u, --unique          Remove duplicates from the output, ignored if used without -A/--no-aggregate.
  -c, --count           Only output the count of the networks/IPs.

ip-aggregator v0.5.0
https://github.com/andrewtwin/ip-aggregator

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/
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

