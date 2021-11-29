import ipaddress
import argparse
import sys
import re

# Regexes
SEPERATOR = r"[\s,;:]"
END = r"(?=" + SEPERATOR + ")"

# IPv4
# IP4_OCTET = r"(?:2[0-5]{,2}|1[0-9]{,2}|[0-9])" # Can be fooled into getting partial but valid addresses
IP4_OCTET = r"(?:[0-9]{1,3})"
IP4_DOT = r"\."
IP4_MASK = r"(?:\/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|\/3[0-2]|\/[1-2][0-9]|\/[0-9])?"
IP4_REGEX = (
    IP4_OCTET
    + IP4_DOT
    + IP4_OCTET
    + IP4_DOT
    + IP4_OCTET
    + IP4_DOT
    + IP4_OCTET
    + IP4_MASK
    + END
)


def main():

    parser = argparse.ArgumentParser(
        description="Aggregate subnets.",
        epilog="ip-aggregator v0.1.0",
    )

    parser.add_argument("subnet", type=str, help="Subnets to aggregate.", nargs="*")

    parser.add_argument(
        "-s",
        "--stdin",
        help="Read addresses from stdin (only IPv4 addresses supported).",
        action="store_true",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        help="Only produce output, no other information.",
        action="store_false",
        dest="notquiet",
    )

    parser.add_argument(
        "-d",
        "--output-delimiter",
        type=str,
        help="Sets the output delimeter, default is new line.",
        default="\n",
    )

    parser.add_argument(
        "-m",
        "--mask-type",
        help="Use prefix length (default), net mask, or wildcard mask.",
        type=str,
        choices=["prefix", "net", "wildcard"],
        default="prefix",
    )

    args = parser.parse_args()

    delimiter = args.output_delimiter

    subnets = []

    if args.stdin:

        for line in sys.stdin:
            read_subnets = re.findall(IP4_REGEX, line)

            for address in read_subnets:
                try:
                    subnets.append(ipaddress.ip_network(address))
                except ValueError:
                    print(
                        f"WARNING: Address {address} from stdin is not a valid IPv4 network, ignoring",
                        file=sys.stderr,
                    )

    for subnet in args.subnet:
        try:
            subnets.append(ipaddress.ip_network(subnet))
        except ValueError:
            exit(f"Supplied argument {subnet} is not a valid IPv4 or IPv6 network.")

    if args.notquiet:
        print(
            f"Input {len(subnets)} addresses: {delimiter.join(format_address(i, args.mask_type) for i in subnets)}"
        )
        print("=" * 18)

    new_subnets = aggregate_subnets(subnets)

    print(f"{delimiter.join(format_address(i, args.mask_type) for i in new_subnets)}")

    if args.notquiet:
        print("=" * 18)
        print(f"{len(new_subnets)} subnets total")


def aggregate_subnets(subnets):
    return list(ipaddress.collapse_addresses(subnets))


def format_address(address, mask="prefix"):
    if mask == "net":
        return address.with_netmask
    elif mask == "wildcard":
        return address.with_hostmask
    else:
        return address.with_prefixlen


if __name__ == "__main__":

    main()
