import ipaddress
import argparse
import sys
import re

"""Formatting"""
NEWLINE = "\n"
RULE = "=" * 18

"""Regex Definitions"""
SEPERATOR = r"[\D]"
END = r"(?=" + SEPERATOR + ")"

"""IPV4"""
# IP4_OCTET = r"(?:2[0-5]{,2}|1[0-9]{,2}|[0-9])" # Can be fooled into getting partial but valid addresses
IP4_OCTET = r"(?:[\d]{1,3})"
IP4_DOT = r"\."
IP4_MASK = (
    r"(?:\/[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}|\/3[0-2]|\/[1-2][\d]|\/[\d])?"
)
IP4_REGEX = re.compile(
    IP4_OCTET
    + IP4_DOT
    + IP4_OCTET
    + IP4_DOT
    + IP4_OCTET
    + IP4_DOT
    + IP4_OCTET
    + IP4_MASK
    + END,
    re.ASCII,
)


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Gather and aggregate subnets.",
        epilog="ip-aggregator v0.3.0",
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
        "-f",
        "--include-filter",
        type=str,
        help="Filter results to include subnets of a network. Multiple filters can be specified.",
        action="append",
    )

    parser.add_argument(
        "-F",
        "--exclude-filter",
        type=str,
        help="Filter results to exclude subnets of a network. Multiple filters can be specified.",
        action="append",
    )

    parser.add_argument(
        "-m",
        "--mask-type",
        help="Use prefix length (default), net mask, or wildcard mask.",
        type=str,
        choices=["prefix", "net", "wildcard"],
        default="prefix",
    )

    sorting_options = parser.add_mutually_exclusive_group()

    sorting_options.add_argument(
        "-S",
        "--sort",
        help="Sort the output, ascending order.",
        action="store_true",
    )

    sorting_options.add_argument(
        "-R",
        "--reverse-sort",
        help="Sort the output, decending order.",
        action="store_true",
    )

    parser.add_argument(
        "-A",
        "--no-aggregate",
        help="Don't aggregate subnets. Just output valid networks and addresses.",
        action="store_true",
    )

    parser.add_argument(
        "-u",
        "--unique",
        help="Remove duplicates from the output, ignored if used without -A/--no-aggregate.",
        action="store_true",
    )

    parser.add_argument(
        "-c",
        "--count",
        help="Only output the count of the networks/IPs.",
        action="store_true",
    )

    args = parser.parse_args()

    delimiter = args.output_delimiter

    subnets = []
    includes = []
    excludes = []

    """Populate subnets to process"""
    if args.stdin:
        for line in sys.stdin:
            read_subnets = re.findall(IP4_REGEX, line)
            for address in read_subnets:
                try:
                    subnets.append(ipaddress.ip_network(address))
                except ValueError:
                    print(
                        f"WARNING: Address {address} from stdin is not a valid IPv4 address or network, ignoring",
                        file=sys.stderr,
                    )

    for subnet in args.subnet:
        try:
            subnets.append(ipaddress.ip_network(subnet))
        except ValueError:
            exit(f"Supplied argument {subnet} is not a valid IPv4 or IPv6 network.")

    """If there are no subnets to operate on exit with an error"""
    if len(subnets) < 1:
        exit("No subnets found to aggregate")

    """Populate includes list"""
    if args.include_filter is not None:
        for address in args.include_filter:
            try:
                includes.append(ipaddress.ip_network(address))
            except ValueError:
                exit(
                    f"Supplied argument include {address} is not a valid IPv4 or IPv6 network."
                )

    """Populate excludes list"""
    if args.exclude_filter is not None:
        for address in args.exclude_filter:
            try:
                excludes.append(ipaddress.ip_network(address))
            except ValueError:
                exit(
                    f"Supplied argument exclude {address} is not a valid IPv4 or IPv6 network."
                )

    if args.notquiet:
        print(
            f"Input {len(subnets)} addresses: "
            + f"{delimiter.join(format_address(i, args.mask_type) for i in subnets)}"
            + NEWLINE
            + RULE
        )

    """Start processing subnets"""
    if args.no_aggregate:
        if args.notquiet:
            print(
                "Not aggregating subnets as requested." + NEWLINE + RULE,
                file=sys.stderr,
            )
        if args.unique:
            new_subnets = list(set(subnets))
        else:
            new_subnets = subnets
    else:
        new_subnets = aggregate_subnets(subnets)

    processed_subnets = []

    """Process Includes and Excludes"""
    if len(includes) > 0:
        included_subnets = []
        include_subnets = aggregate_subnets(includes)
        for include in include_subnets:
            for subnet in new_subnets:
                if subnet.subnet_of(include):
                    included_subnets.append(subnet)
    else:
        included_subnets = new_subnets

    if len(excludes) > 0:
        exclude_subnets = aggregate_subnets(excludes)
        for subnet in included_subnets:
            exclude_subnet = False
            for exclude in exclude_subnets:
                if subnet.subnet_of(exclude):
                    exclude_subnet = True
            if not exclude_subnet:
                processed_subnets.append(subnet)
    else:
        processed_subnets = included_subnets

    if args.sort:
        processed_subnets.sort()
    elif args.reverse_sort:
        processed_subnets.sort(reverse=True)

    """Output addresses"""
    if args.count:
        print(f"{len(processed_subnets)}")
    else:
        print(
            f"{delimiter.join(format_address(i, args.mask_type) for i in processed_subnets)}"
        )

    if args.notquiet:
        print(RULE + NEWLINE + f"{len(processed_subnets)} subnets total")


def aggregate_subnets(subnets) -> list:
    """return a list

    aggregate subnets
    """
    return list(ipaddress.collapse_addresses(subnets))


def format_address(address, mask="prefix") -> str:
    """return a string

    format the network
    """
    if mask == "net":
        return address.with_netmask
    elif mask == "wildcard":
        return address.with_hostmask
    else:
        return address.with_prefixlen


if __name__ == "__main__":

    main()
