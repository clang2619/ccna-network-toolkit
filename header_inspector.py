#!/usr/bin/env python3
"""
CCNA Interactive Frame & Header Inspector
Dissects Layer 2 through Layer 4 protocol headers and drills field values.
Requires Python 3 standard library only.
"""

import random
import sys
import time

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def clear_and_banner():
    print(f"\n{BOLD}{CYAN}===================================================={RESET}")
    print(f"{BOLD}{CYAN}   CCNA PROTOCOL & HEADER INSPECTION ENGINE        {RESET}")
    print(f"{BOLD}{CYAN}===================================================={RESET}\n")


def display_ethernet():
    print(f"{BOLD}{MAGENTA}[ LAYER 2: ETHERNET II FRAME ]{RESET}")
    print("+" + "-" * 74 + "+")
    print(
        f"| Preamble (7B) | SFD (1B) | Dest MAC (6B) | Src MAC (6B) | EtherType (2B) | Payload (46-1500B) | FCS (4B) |"
    )
    print("+" + "-" * 74 + "+")
    print(f"\n{BOLD}Key CCNA EtherTypes to Memorize:{RESET}")
    print(f"  • {YELLOW}0x0800{RESET} -> IPv4 (Internet Protocol v4)")
    print(f"  • {YELLOW}0x86DD{RESET} -> IPv6 (Internet Protocol v6)")
    print(f"  • {YELLOW}0x0806{RESET} -> ARP (Address Resolution Protocol)")
    print(f"  • {YELLOW}0x8100{RESET} -> 802.1Q (VLAN Tagged Frame)")
    print(
        f"\n{BOLD}Note on FCS:{RESET} Uses CRC-32 checksum. If verification fails, the switch silently drops the frame."
    )


def display_dot1q():
    print(f"{BOLD}{MAGENTA}[ LAYER 2: 802.1Q TRUNK TAG (4 Bytes Inserted) ]{RESET}")
    print("+" + "-" * 66 + "+")
    print(f"| TPID: 0x8100 (16 bits) | PCP (3 bits) | DEI (1 bit) | VID (12 bits)      |")
    print("+" + "-" * 66 + "+")
    print(f"\n{BOLD}Field Breakdown:{RESET}")
    print(
        f"  • {YELLOW}TPID (Tag Protocol Identifier):{RESET} Always 0x8100 to identify the 802.1Q tag."
    )
    print(
        f"  • {YELLOW}PCP (Priority Code Point):{RESET} 3 bits -> 8 Layer 2 CoS QoS priority levels (0-7)."
    )
    print(
        f"  • {YELLOW}DEI (Drop Eligible Indicator):{RESET} 1 bit -> Packet drop preference during congestion."
    )
    print(
        f"  • {YELLOW}VID (VLAN Identifier):{RESET} 12 bits -> 2^12 = 4096 possible IDs (1-4094 usable; 0 and 4095 reserved)."
    )


def display_ipv4():
    print(f"{BOLD}{CYAN}[ LAYER 3: IPv4 PACKET HEADER (20-60 Bytes) ]{RESET}")
    print(" 0                   1                   2                   3")
    print(" 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|Version|  IHL  |Type of Service|          Total Length         |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|         Identification        |Flags|     Fragment Offset     |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|  Time to Live |    Protocol   |        Header Checksum        |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|                       Source IP Address                       |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|                    Destination IP Address                     |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print(f"\n{BOLD}Key CCNA Fields:{RESET}")
    print(
        f"  • {YELLOW}TTL (Time to Live):{RESET} Decremented by 1 at each Layer 3 router hop. At 0, packet dropped with ICMP Time Exceeded (Type 11)."
    )
    print(f"  • {YELLOW}Protocol Numbers:{RESET}")
    print(f"      1  -> ICMP")
    print(f"      6  -> TCP")
    print(f"      17 -> UDP")
    print(f"      89 -> OSPF")


def display_ipv6():
    print(f"{BOLD}{CYAN}[ LAYER 3: IPv6 FIXED PACKET HEADER (Fixed 40 Bytes) ]{RESET}")
    print(" 0                   1                   2                   3")
    print(" 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|Version| Traffic Class |           Flow Label                  |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|         Payload Length        |  Next Header  |   Hop Limit   |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|                                                               |")
    print("|                  Source Address (128 bits)                    |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|                                                               |")
    print("|               Destination Address (128 bits)                  |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print(f"\n{BOLD}IPv6 vs IPv4 Differences:{RESET}")
    print(f"  • {YELLOW}Fixed Size:{RESET} Always 40 bytes (removes IHL field).")
    print(
        f"  • {YELLOW}No Checksum:{RESET} Relies on Layer 2 and Layer 4 checksums to increase routing speed."
    )
    print(
        f"  • {YELLOW}Next Header:{RESET} Replaces IPv4 Protocol field and points to extension headers or L4 payload."
    )
    print(f"  • {YELLOW}Hop Limit:{RESET} Direct equivalent of IPv4 TTL.")


def display_tcp():
    print(f"{BOLD}{GREEN}[ LAYER 4: TCP SEGMENT HEADER (20-60 Bytes) ]{RESET}")
    print(" 0                   1                   2                   3")
    print(" 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|          Source Port          |       Destination Port        |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|                        Sequence Number                        |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|                    Acknowledgment Number                      |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|  Data |       |U|A|P|R|S|F|                                   |")
    print("| Offset|  Res  |R|C|S|S|Y|I|            Window Size            |")
    print("|       |       |G|K|H|T|N|N|                                   |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("|           Checksum            |         Urgent Pointer        |")
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print(f"\n{BOLD}Handshake Control Flags:{RESET}")
    print(f"  • {YELLOW}SYN:{RESET} Synchronize sequence numbers (initiate connection).")
    print(
        f"  • {YELLOW}ACK:{RESET} Acknowledgment field valid (every packet after initial SYN)."
    )
    print(f"  • {YELLOW}FIN:{RESET} Graceful termination of sender's connection.")
    print(
        f"  • {YELLOW}RST:{RESET} Reset connection immediately (abrupt termination or refused port)."
    )


def run_quiz():
    questions = [
        {
            "q": "What is the EtherType hex value for an IPv4 packet inside an Ethernet frame?",
            "a": "0x0800",
            "aliases": ["0800", "0x0800"],
            "hint": "IPv6 is 0x86DD; IPv4 is 0x0800.",
        },
        {
            "q": "What is the EtherType hex value for an 802.1Q tagged frame?",
            "a": "0x8100",
            "aliases": ["8100", "0x8100"],
            "hint": "Starts with 81, followed by two zeroes.",
        },
        {
            "q": "What is the IPv4 Protocol number for OSPF?",
            "a": "89",
            "aliases": ["89"],
            "hint": "TCP is 6, UDP is 17, ICMP is 1, OSPF is 89.",
        },
        {
            "q": "What is the size of the fixed IPv6 base header in bytes?",
            "a": "40",
            "aliases": ["40", "40 bytes"],
            "hint": "IPv4 minimum is 20 bytes; IPv6 base header is exactly 40 bytes.",
        },
        {
            "q": "How many bits are allocated for the VLAN ID (VID) in an 802.1Q tag?",
            "a": "12",
            "aliases": ["12", "12 bits"],
            "hint": "2^12 = 4096 possible VLAN IDs.",
        },
        {
            "q": "Which field in the IPv6 header replaces the IPv4 'Time to Live' (TTL)?",
            "a": "Hop Limit",
            "aliases": ["hop limit", "hoplimit"],
            "hint": "Direct equivalent name describing hop bounds.",
        },
        {
            "q": "Which two TCP control flags are set during step 2 of the 3-way handshake?",
            "a": "SYN-ACK",
            "aliases": ["syn-ack", "syn ack", "syn/ack", "ack-syn"],
            "hint": "Sender sends SYN; Receiver answers with both SYN and ACK.",
        },
        {
            "q": "What is the IPv4 Protocol number for UDP?",
            "a": "17",
            "aliases": ["17"],
            "hint": "TCP is 6; UDP is 17.",
        },
    ]

    random.shuffle(questions)
    score = 0
    total = len(questions)

    print(f"\n{BOLD}{CYAN}--- HEADER & PROTOCOL SPEED DRILL ({total} Questions) ---{RESET}\n")

    for i, item in enumerate(questions, 1):
        print(f"{BOLD}Q{i}: {item['q']}{RESET}")
        ans = input(f"{CYAN}Your Answer: {RESET}").strip().lower()

        if ans in [a.lower() for a in item["aliases"]]:
            print(f"{GREEN}✔ Correct!{RESET}\n")
            score += 1
        else:
            print(f"{RED}✘ Incorrect.{RESET} Expected: {BOLD}{item['a']}{RESET}")
            print(f"{YELLOW}Review note: {item['hint']}{RESET}\n")

    pct = round((score / total) * 100)
    print(f"{BOLD}Final Score: {score}/{total} ({pct}%){RESET}\n")


def main_menu():
    while True:
        clear_and_banner()
        print("Select a Header or Action:")
        print("  1. Layer 2 - Ethernet II Frame & EtherTypes")
        print("  2. Layer 2 - 802.1Q VLAN Trunking Tag")
        print("  3. Layer 3 - IPv4 Packet Header & Protocol Numbers")
        print("  4. Layer 3 - IPv6 Packet Header & Field Differences")
        print("  5. Layer 4 - TCP Segment Header & Handshake Flags")
        print("  6. Launch Protocol Quiz Drill")
        print("  0. Exit")

        choice = input(f"\n{CYAN}Enter choice (0-6): {RESET}").strip()

        if choice == "1":
            display_ethernet()
        elif choice == "2":
            display_dot1q()
        elif choice == "3":
            display_ipv4()
        elif choice == "4":
            display_ipv6()
        elif choice == "5":
            display_tcp()
        elif choice == "6":
            run_quiz()
        elif choice == "0":
            print("\nExiting Header Inspector. Happy studying!\n")
            break
        else:
            print(f"{RED}Invalid selection.{RESET}")

        input(f"\n{CYAN}Press Enter to return to menu...{RESET}")


if __name__ == "__main__":
    main_menu()