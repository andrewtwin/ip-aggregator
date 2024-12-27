SYNOPSYS = """ip-aggregator - Extract, filter, sort, and aggregate IPs from subnets into larger supernets."""

LICENCE = """
Copyright (C) 2024 Andrew Twin

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

VERSION = "v0.7.0"

import ipaddress
import argparse
from sys import stderr, stdin, exit as sysexit
import re


"""Formatting Constants"""
SPACE = " "
NEWLINE = "\n"
RULE = "-" * 18

"""Regex Definitions"""
SEPERATOR = r"[\D]"
RANGE_SEPERATOR = r"[-]?"
CAPTURE_START = r"("
CAPTURE_END = r")"
END = r"(?=" + SEPERATOR + ")"

"""IPV4"""
# IP4_OCTET = r"(?:2[0-5]{,2}|1[0-9]{,2}|[0-9])" # Can be fooled into getting partial but valid addresses
IP4_OCTET = r"(?:[\d]{1,3})"
IP4_DOT = r"\."
IP4_MASK = (
    r"(?:\/[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}|\/3[0-2]|\/[1-2][\d]|\/[\d])?"
)
IP4_ADDRESS = (
    IP4_OCTET + IP4_DOT + IP4_OCTET + IP4_DOT + IP4_OCTET + IP4_DOT + IP4_OCTET
)

IP4_NETWORK = re.compile(
    IP4_ADDRESS + IP4_MASK + END,
    re.ASCII,
)
IP4_RANGE = re.compile(
    CAPTURE_START + IP4_ADDRESS + CAPTURE_END + RANGE_SEPERATOR,
    re.ASCII,
)

"""IP Network Constants"""
IP4_CLASS_A = [ipaddress.ip_network("10.0.0.0/8")]
IP4_CLASS_B = [ipaddress.ip_network("172.16.0.0/12")]
IP4_CLASS_C = [ipaddress.ip_network("192.168.0.0/16")]
IP4_CLASS_D = [ipaddress.ip_network("224.0.0.0/4")]
IP4_CLASS_E = [ipaddress.ip_network("240.0.0.0/4")]
IP4_CGNAT = [ipaddress.ip_network("100.64.0.0/10")]
IP4_LOCAL = [ipaddress.ip_network("127.0.0.0/8")]
IP4_LINK_LOCAL = [ipaddress.ip_network("169.254.0.0/16")]

IP4_RFC1918_ADDRESSES = IP4_CLASS_A + IP4_CLASS_B + IP4_CLASS_C
IP4_NON_ROUTABLE = IP4_LOCAL + IP4_LINK_LOCAL
IP4_NON_GLOBAL = IP4_RFC1918_ADDRESSES + IP4_NON_ROUTABLE

IP4_ALIASES = {
    "A": IP4_CLASS_A,
    "B": IP4_CLASS_B,
    "C": IP4_CLASS_C,
    "D": IP4_CLASS_D,
    "E": IP4_CLASS_E,
    "CGNAT": IP4_CGNAT,
    "LOCAL": IP4_LOCAL,
    "LINK": IP4_LINK_LOCAL,
    "PRIVATE": IP4_RFC1918_ADDRESSES,
    "NOROUTE": IP4_NON_ROUTABLE,
    "NOGLOBAL": IP4_NON_GLOBAL,
}


def main() -> None:
    """no return

    Main function.
    """
    parser = argparse.ArgumentParser(
        prog="ip-aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Extract, filter, sort, and aggregate subnets.
Copyright (C) 2024 Andrew Twin - GNU GPLv3 - see version for more information.""",
        epilog=f"{VERSION}",
    )

    """Input args"""
    input_args = parser.add_argument_group(
        title="input options", description="How to provide input."
    )

    input_args.add_argument(
        "subnet", type=str, help="Subnets or ip ranges to aggregate.", nargs="*"
    )

    input_args.add_argument(
        "-s",
        "--stdin",
        help="Extract addresses from stdin (only IPv4 addresses supported, aliases not supported).",
        action="store_true",
    )

    """Filter args"""
    filter_args = parser.add_argument_group(
        title="filter options",
        description="Filering of input networks, includes are processed before excludes.",
    )

    filter_args.add_argument(
        "-f",
        "--include-filter",
        type=str,
        help="Filter results to include subnets of a network. Multiple filters can be specified.",
        action="append",
    )

    filter_args.add_argument(
        "-F",
        "--exclude-filter",
        type=str,
        help="Filter results to exclude subnets of a network. Multiple filters can be specified.",
        action="append",
    )

    """Output args"""
    output_args = parser.add_argument_group(
        title="output options", description="How to display output."
    )

    output_args.add_argument(
        "-q",
        "--quiet",
        help="Only produce output, no other information.",
        action="store_false",
        dest="notquiet",
    )

    format_args = output_args.add_mutually_exclusive_group(required=False)

    format_args.add_argument(
        "-d",
        "--output-delimiter",
        type=str,
        help="Sets the output delimeter, default is a new line.",
        default="\n",
    )

    format_args.add_argument(
        "-y",
        "--yaml",
        help="Output as YAML list, with N spaces indent",
        type=int,
        default=-1,
    )

    output_args.add_argument(
        "-Q",
        "--quote",
        help="Wrap addresses in QUOTE characters",
        type=str,
        default="",
    )

    output_args.add_argument(
        "-m",
        "--mask-type",
        help="Use prefix length (default), net mask, or wildcard mask.",
        type=str,
        choices=["prefix", "net", "wildcard"],
        default="prefix",
    )

    output_args.add_argument(
        "-S",
        "--sort",
        help="Sort the output, ascending order.",
        action="store_true",
    )

    output_args.add_argument(
        "-R",
        "--reverse-sort",
        help="Sort the output, decending order.",
        action="store_true",
    )

    output_args.add_argument(
        "-A",
        "--no-aggregate",
        help="Don't aggregate subnets. Just output valid networks and addresses.",
        action="store_true",
    )

    output_args.add_argument(
        "-u",
        "--unique",
        help="Remove duplicates from the output, redundant without -A/--no-aggregate.",
        action="store_true",
    )

    output_args.add_argument(
        "-c",
        "--count",
        help="Only output the count of the networks/IPs.",
        action="store_true",
    )

    """Misc args"""
    parser.add_argument(
        "-V",
        "--version",
        help="Print version and licence information and exit",
        action="store_true",
    )

    parser.add_argument(
        "-l",
        "--list-aliases",
        help="List IP aliases and exit. Alises can be used in place of regular addresses. Supports -m/--mask-type flag.",
        action="store_true",
    )

    args = parser.parse_args()

    """If displaying version and licence, print and exit"""
    if args.version:
        print(f"{VERSION}" + LICENCE)
        sysexit(0)

    """If just listing the classes, print and exit"""
    if args.list_aliases:
        delimiter = ", "
        print(
            "Recognised address aliases."
            + NEWLINE
            + "These can be used alongside regular addresses:"
            + NEWLINE
            + RULE * 2,
        )
        for ipclass, ipvalue in IP4_ALIASES.items():
            print(
                f"{ipclass.rjust(8)}: "
                f"{delimiter.join(format_address(i, args.mask_type) for i in ipvalue)}"
            )
        sysexit(0)

    delimiter = args.output_delimiter

    """Populate subnets to process"""
    subnets = []
    if args.stdin:
        for line in stdin:
            read_subnets = re.findall(IP4_NETWORK, line)
            for address in read_subnets:
                try:
                    subnets.append(ipaddress.ip_network(address))
                except ValueError:
                    print(
                        f"WARNING: Address {address} from stdin is not a valid IPv4 address or network, ignoring",
                        file=stderr,
                    )

    """Check for IP range otherwise assume single ip or subnet"""
    for subnet in args.subnet:
        subnet_range_list = re.findall(IP4_RANGE, subnet)
        if len(subnet_range_list) == 2:
            try:
                subnet_range = ipaddress.summarize_address_range(
                    ipaddress.ip_address(subnet_range_list[0]),
                    ipaddress.ip_address(subnet_range_list[1]),
                )
                subnets.extend(subnet_range)
            except ValueError:
                print(
                    f"Supplied argument {subnet} are not a valid IPv4 or IPv6 addresses.",
                    file=stderr,
                )
                sysexit(2)
        else:
            if subnet in IP4_ALIASES.keys():
                subnets.extend(IP4_ALIASES.get(subnet))
            else:
                try:
                    subnets.append(ipaddress.ip_network(subnet))
                except ValueError:
                    print(
                        f"Supplied argument {subnet} is not a valid IPv4 or IPv6 network.",
                        file=stderr,
                    )
                    sysexit(2)

    """If there are no subnets to operate on exit with an error"""
    if len(subnets) < 1:
        print("No subnets found to aggregate", file=stderr)
        sysexit(1)

    """Print subnets being processed"""
    if args.notquiet:
        print(
            f"Input {len(subnets)} addresses: "
            + NEWLINE
            + f"{delimiter.join(format_address(i, args.mask_type) for i in subnets)}"
            + NEWLINE
            + RULE,
            file=stderr,
        )

    """Populate includes list"""
    includes = []
    if args.include_filter is not None:
        for address in args.include_filter:
            if address in IP4_ALIASES.keys():
                includes.extend(IP4_ALIASES.get(address))
            else:
                try:
                    includes.append(ipaddress.ip_network(address))
                except ValueError:
                    print(
                        f"Supplied argument include {address} is not a valid IPv4 or IPv6 network.",
                        file=stderr,
                    )
                    sysexit(2)

    """Populate excludes list"""
    excludes = []
    if args.exclude_filter is not None:
        for address in args.exclude_filter:
            if address in IP4_ALIASES.keys():
                excludes.extend(IP4_ALIASES.get(address))
            else:
                try:
                    excludes.append(ipaddress.ip_network(address))
                except ValueError:
                    print(
                        f"Supplied argument exclude {address} is not a valid IPv4 or IPv6 network.",
                        file=stderr,
                    )
                    sysexit(2)

    """Start processing subnets
    Duplicates can be removed before filters applied
    no need to remove duplicates if the subnets are going to be aggrerated.
    """
    if args.no_aggregate and args.unique:
        unique_subnets = []
        for subnet in subnets:
            if subnet not in unique_subnets:
                unique_subnets.append(subnet)
        subnets.clear()
        subnets = unique_subnets

    """Process filtering"""
    filtered_subnets = []

    """Includes"""
    if len(includes) > 0:
        included_subnets = []
        include_subnets = aggregate_subnets(includes)
        if args.notquiet:
            print(
                "Including only addresses in: "
                + f"{', '.join(format_address(i, args.mask_type) for i in include_subnets)}",
                file=stderr,
            )
        for include in include_subnets:
            for subnet in subnets:
                if subnet.subnet_of(include):
                    included_subnets.append(subnet)
        filtered_subnets = included_subnets
    else:
        filtered_subnets = subnets

    """Excludes"""
    if len(excludes) > 0:
        exclude_subnets = aggregate_subnets(excludes)
        not_excluded_subnets = []
        if args.notquiet:
            print(
                "Excluding addresses in: "
                + f"{', '.join(format_address(i, args.mask_type) for i in exclude_subnets)}",
                file=stderr,
            )
        for subnet in filtered_subnets:
            exclude_subnet = False
            for exclude in exclude_subnets:
                if subnet.subnet_of(exclude):
                    exclude_subnet = True
            if not exclude_subnet:
                not_excluded_subnets.append(subnet)
        filtered_subnets.clear
        filtered_subnets = not_excluded_subnets

    """Check if subnets should be aggregated"""
    if args.no_aggregate:
        if args.notquiet:
            print(
                "Not aggregating subnets as requested.",
                file=stderr,
            )
        processed_subnets = filtered_subnets
    else:
        processed_subnets = aggregate_subnets(filtered_subnets)

    """Do sorting if required"""
    if args.sort:
        processed_subnets.sort()
    elif args.reverse_sort:
        processed_subnets.sort(reverse=True)

    """Output addresses"""
    if (args.no_aggregate or len(includes) > 0 or len(excludes) > 0) and args.notquiet:
        print(f"{RULE}", file=stderr)
    if args.count:
        print(f"{len(processed_subnets)}")
    elif len(processed_subnets) > 0:
        if args.notquiet:
            print(f"Output {len(processed_subnets)} addresses: ", file=stderr)
        if args.yaml >= 0:
            indent_chars = SPACE * args.yaml
            for subnet in processed_subnets:
                print(
                    indent_chars
                    + f"- {format_address(subnet, args.mask_type, args.quote)}"
                )
        else:
            print(
                f"{delimiter.join(format_address(i, args.mask_type, args.quote) for i in processed_subnets)}"
            )


def aggregate_subnets(subnets) -> list:
    """return a list

    aggregate subnets
    """
    return list(ipaddress.collapse_addresses(subnets))


def format_address(address, mask="prefix", quotes="") -> str:
    """return a string

    format the network address
    """
    if mask == "net":
        network =  address.with_netmask
    elif mask == "wildcard":
        network =  address.with_hostmask
    else:
        network =  address.with_prefixlen

    return quotes + network + quotes


if __name__ == "__main__":

    main()
