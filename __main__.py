"""
Extract, filter, sort, and aggregate IPs from subnets into larger supernets.
Copyright (C) 2021 Andrew Twin

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
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

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

IP4_CLASSES = {
    "A": ipaddress.ip_network("10.0.0.0/8"),
    "B": ipaddress.ip_network("172.16.0.0/12"),
    "C": ipaddress.ip_network("192.168.0.0/16"),
    "D": ipaddress.ip_network("224.0.0.0/4"),
    "E": ipaddress.ip_network("240.0.0.0/4"),
    "N": ipaddress.ip_network("100.64.0.0/10"),
    "L": ipaddress.ip_network("127.0.0.0/8"),
    "U": ipaddress.ip_network("169.254.0.0/16"),
}


def main() -> None:

    parser = argparse.ArgumentParser(
        prog="ip-aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Extract, filter, sort, and aggregate subnets.
Copyright (C) 2021 Andrew Twin""",
        epilog="""ip-aggregator v0.5.0
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
""",
    )

    parser.add_argument("subnet", type=str, help="Subnets to aggregate.", nargs="*")

    parser.add_argument(
        "-s",
        "--stdin",
        help="Extract addresses from stdin (only IPv4 addresses supported).",
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
        help="Sets the output delimeter, default is a new line.",
        default="\n",
    )

    parser.add_argument(
        "-l",
        "--list-classes",
        help="List IP classes and exit. Classes can be used in filters, supports -m/--mask-type flag.",
        action="store_true",
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

    """If just listing the classes, print and exit"""
    if args.list_classes:
        print(
            "Recognised address class aliases."
            + NEWLINE
            + "These can be used alongside regular addresses in filters:"
            + NEWLINE
            + RULE * 2,
        )
        for ipclass, ipvalue in IP4_CLASSES.items():
            print(f"{ipclass}\t{format_address(ipvalue, args.mask_type)}")
        exit(0)

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
            if address in IP4_CLASSES.keys():
                includes.append(IP4_CLASSES.get(address))
            else:
                try:
                    includes.append(ipaddress.ip_network(address))
                except ValueError:
                    exit(
                        f"Supplied argument include {address} is not a valid IPv4 or IPv6 network."
                    )

    """Populate excludes list"""
    if args.exclude_filter is not None:
        for address in args.exclude_filter:
            if address in IP4_CLASSES.keys():
                excludes.append(IP4_CLASSES.get(address))
            else:
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
        """Remove duplciate subnets"""
        if args.unique:
            new_subnets = []
            for subnet in subnets:
                if subnet not in new_subnets:
                    new_subnets.append(subnet)
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

    """Do sorting if required"""
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
