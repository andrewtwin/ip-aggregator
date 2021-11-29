# ip-agregator
Argregate IPs


## Usage
```
usage: ip-agregator [-h] [-s] [-q] [-d OUTPUT_DELIMITER] [-m {prefix,net,wildcard}] [subnet ...]

Agregate subnets.

positional arguments:
  subnet                Subnets to agregate.

optional arguments:
  -h, --help            show this help message and exit
  -s, --stdin           Read addresses from stdin (only IPv4 Addresses Supported).
  -q, --quiet           Only produce output, no other information.
  -d OUTPUT_DELIMITER, --output-delimiter OUTPUT_DELIMITER
                        Sets the output delimeter, default is new line.
  -m {prefix,net,wildcard}, --mask-type {prefix,net,wildcard}
                        Use prefix length (default), net mask, or wildcard mask.

ip-agregator v0.1.0
```

## Examples

