#!/usr/bin/env python3
"""
CCNA Subnet Speed-Drill CLI
Drills network address, broadcast, valid host range, usable hosts, and wildcard masks.
"""

import ipaddress
import random
import sys
import time

# ANSI Terminal Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def generate_scenario():
    """Generates a random IPv4 address and prefix length."""
    # Weight prefixes towards common exam CIDRs (/16 through /30)
    prefix = random.randint(16, 30)

    # Mix of private ranges and common routable subnets
    network_pools = [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "198.51.100.0/24",
        "203.0.113.0/24",
    ]
    base_pool = ipaddress.ip_network(random.choice(network_pools))

    # Pick a random host within the base pool
    random_int = random.randint(
        int(base_pool.network_address) + 1, int(base_pool.broadcast_address) - 1
    )
    ip_obj = ipaddress.ip_address(random_int)

    # Form the candidate interface
    interface = ipaddress.ip_interface(f"{ip_obj}/{prefix}")
    network = interface.network

    return interface, network


def calculate_wildcard(netmask):
    """Calculates inverse wildcard mask (e.g. 255.255.255.0 -> 0.0.0.255)."""
    mask_octets = [int(o) for o in str(netmask).split(".")]
    wildcard_octets = [str(255 - o) for o in mask_octets]
    return ".".join(wildcard_octets)


def get_block_size_explanation(network):
    """Provides the mental math breakdown for review."""
    prefix = network.prefixlen
    if prefix >= 24:
        interesting_octet = 4
        borrowed = prefix - 24
        block_size = 2 ** (8 - borrowed)
    elif prefix >= 16:
        interesting_octet = 3
        borrowed = prefix - 16
        block_size = 2 ** (8 - borrowed)
    else:
        interesting_octet = 2
        borrowed = prefix - 8
        block_size = 2 ** (8 - borrowed)

    return (
        f"Prefix /{prefix} -> Interesting Octet: #{interesting_octet} | "
        f"Block Size (Magic Number): 256 - mask = {block_size}"
    )


def run_drill():
    score = 0
    total = 0

    print(f"\n{BOLD}{CYAN}=== CCNA SUBMISSION SPEED-DRILL ==={RESET}")
    print("Type your answer and press Enter. Enter 'q' at any prompt to exit.\n")

    question_types = [
        "network",
        "broadcast",
        "first_host",
        "last_host",
        "usable_hosts",
        "wildcard",
    ]

    while True:
        interface, network = generate_scenario()
        q_type = random.choice(question_types)
        total += 1

        print(f"\n{BOLD}Scenario #{total}:{RESET}")
        print(f"Given Host Interface: {YELLOW}{interface}{RESET}")
        print(f"Subnet Mask:          {network.netmask}")

        # Determine prompt and expected answer
        if q_type == "network":
            prompt = "Enter Network ID: "
            expected = str(network.network_address)
        elif q_type == "broadcast":
            prompt = "Enter Broadcast Address: "
            expected = str(network.broadcast_address)
        elif q_type == "first_host":
            prompt = "Enter First Usable Host: "
            expected = (
                str(network.network_address + 1)
                if network.num_addresses > 2
                else "N/A"
            )
        elif q_type == "last_host":
            prompt = "Enter Last Usable Host: "
            expected = (
                str(network.broadcast_address - 1)
                if network.num_addresses > 2
                else "N/A"
            )
        elif q_type == "usable_hosts":
            prompt = "Total Usable Host Count (2^H - 2): "
            # Account for /31 and /32 edge cases if any
            expected = (
                str(max(0, network.num_addresses - 2))
                if network.prefixlen <= 30
                else "0"
            )
        elif q_type == "wildcard":
            prompt = "Enter Wildcard Mask (for ACL/OSPF): "
            expected = calculate_wildcard(network.netmask)

        start_time = time.time()
        try:
            user_input = input(f"{CYAN}{prompt}{RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession aborted.")
            break

        elapsed = round(time.time() - start_time, 2)

        if user_input.lower() == "q":
            total -= 1
            break

        # Check result
        if user_input == expected:
            score += 1
            print(f"{GREEN}✔ CORRECT!{RESET} ({elapsed}s)")
        else:
            print(f"{RED}✘ INCORRECT.{RESET}")
            print(f"Expected: {BOLD}{expected}{RESET} | Your input: {user_input}")
            print(f"{YELLOW}Hint: {get_block_size_explanation(network)}{RESET}")

    # Summary
    print(f"\n{BOLD}--- DRILL SESSION COMPLETE ---{RESET}")
    if total > 0:
        accuracy = round((score / total) * 100, 1)
        print(f"Total Drills: {total}")
        print(f"Score:        {score}/{total} ({accuracy}%)")
    print(f"Keep drilling until calculations take under 10 seconds without hesitation!\n")


if __name__ == "__main__":
    run_drill()