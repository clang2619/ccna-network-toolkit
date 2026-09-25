#!/usr/bin/env python3
"""
CCNA Interactive Frame & Header Inspector GUI
Visual dissection engine & speed quiz for Layer 2 through Layer 4 headers.
Requires Python 3 standard library only (tkinter).
"""

import tkinter as tk
from tkinter import ttk
import random
import time

# --- Color Scheme (Dark Terminal Style) ---
BG_DARK = "#1e1e24"
BG_CARD = "#2b2b36"
TEXT_COLOR = "#f0f0f5"
ACCENT_CYAN = "#00d4ff"
ACCENT_GREEN = "#2ecc71"
ACCENT_RED = "#e74c3c"
ACCENT_YELLOW = "#f39c12"
ACCENT_MAGENTA = "#c678dd"
FONT_FAMILY = "Segoe UI"


class HeaderInspectorApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("CCNA Frame & Header Inspector")
        self.geometry("780x740")
        self.minsize(700, 650)
        self.configure(bg=BG_DARK)

        # Quiz State Variables
        self.score = 0
        self.total = 0
        self.start_time = 0
        self.current_q = None
        self.is_waiting_for_next = False

        self.questions_bank = [
            {
                "q": "What is the EtherType hex value for an IPv4 packet inside an Ethernet frame?",
                "a": "0x0800",
                "aliases": ["0800", "0x0800"],
                "hint": "IPv6 is 0x86DD; IPv4 is 0x0800.",
            },
            {
                "q": "What is the EtherType hex value indicating an 802.1Q tagged frame?",
                "a": "0x8100",
                "aliases": ["8100", "0x8100"],
                "hint": "TPID is always 0x8100 for standard 802.1Q tagging.",
            },
            {
                "q": "What is the IPv4 Protocol number for OSPF?",
                "a": "89",
                "aliases": ["89"],
                "hint": "ICMP is 1, TCP is 6, UDP is 17, and OSPF is 89.",
            },
            {
                "q": "What is the fixed size of the IPv6 base header in bytes?",
                "a": "40",
                "aliases": ["40", "40 bytes", "40b"],
                "hint": "IPv4 minimum is 20 bytes; IPv6 base header is fixed at 40 bytes.",
            },
            {
                "q": "How many bits are allocated for the VLAN ID (VID) in an 802.1Q tag?",
                "a": "12",
                "aliases": ["12", "12 bits"],
                "hint": "2^12 = 4096 possible IDs (1 to 4094 usable).",
            },
            {
                "q": "Which field in the IPv6 header replaces IPv4's Time to Live (TTL)?",
                "a": "Hop Limit",
                "aliases": ["hop limit", "hoplimit"],
                "hint": "It decrements at each Layer 3 router hop.",
            },
            {
                "q": "Which two TCP control flags are set during step 2 of the 3-way handshake?",
                "a": "SYN-ACK",
                "aliases": ["syn-ack", "syn ack", "syn/ack", "ack-syn"],
                "hint": "Sender sends SYN; Receiver responds with SYN and ACK.",
            },
            {
                "q": "What is the IPv4 Protocol number for UDP?",
                "a": "17",
                "aliases": ["17"],
                "hint": "TCP is 6; UDP is 17.",
            },
            {
                "q": "How many bits are used for Priority Code Point (PCP / CoS) in an 802.1Q tag?",
                "a": "3",
                "aliases": ["3", "3 bits"],
                "hint": "3 bits allow 8 distinct Class of Service QoS priority values (0-7).",
            },
            {
                "q": "What Layer 2 mechanism is used in the Ethernet FCS field to detect frame corruption?",
                "a": "CRC-32",
                "aliases": ["crc", "crc-32", "crc32", "cyclic redundancy check"],
                "hint": "Cyclic Redundancy Check (CRC-32) calculation.",
            },
        ]
        self.available_questions = list(self.questions_bank)
        random.shuffle(self.available_questions)

        self.setup_styles()
        self.build_ui()
        self.next_quiz_question()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "TNotebook",
            background=BG_DARK,
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            background="#2a2a35",
            foreground=TEXT_COLOR,
            padding=[14, 6],
            font=(FONT_FAMILY, 9, "bold"),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", ACCENT_CYAN)],
            foreground=[("selected", "#121217")],
        )

    def build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=BG_DARK, pady=10)
        header.pack(fill=tk.X, padx=20)

        title_lbl = tk.Label(
            header,
            text="🔬 CCNA PROTOCOL & HEADER INSPECTOR",
            font=(FONT_FAMILY, 15, "bold"),
            fg=ACCENT_CYAN,
            bg=BG_DARK,
        )
        title_lbl.pack(side=tk.LEFT)

        # Tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 15))

        # Add tabs
        self.notebook.add(self.create_ethernet_tab(), text="Layer 2: Ethernet II")
        self.notebook.add(self.create_dot1q_tab(), text="Layer 2: 802.1Q Tag")
        self.notebook.add(self.create_ipv4_tab(), text="Layer 3: IPv4")
        self.notebook.add(self.create_ipv6_tab(), text="Layer 3: IPv6")
        self.notebook.add(self.create_tcp_tab(), text="Layer 4: TCP")
        self.notebook.add(self.create_quiz_tab(), text="⚡ Protocol Quiz")

    def create_card_frame(self, parent):
        card = tk.Frame(
            parent,
            bg=BG_CARD,
            padx=18,
            pady=16,
            highlightbackground="#3d3d4d",
            highlightthickness=1,
        )
        card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        return card

    def create_ethernet_tab(self):
        tab = tk.Frame(self.notebook, bg=BG_DARK)
        card = self.create_card_frame(tab)

        tk.Label(
            card,
            text="ETHERNET II FRAME STRUCTURE",
            font=(FONT_FAMILY, 13, "bold"),
            fg=ACCENT_MAGENTA,
            bg=BG_CARD,
        ).pack(anchor=tk.W)

        diagram = (
            "+---------------+----------+---------------+---------------+----------------+----------------------+----------+\n"
            "| Preamble (7B) | SFD (1B) | Dest MAC (6B) | Src MAC (6B)  | EtherType (2B) | Payload (46-1500B)   | FCS (4B) |\n"
            "+---------------+----------+---------------+---------------+----------------+----------------------+----------+"
        )
        lbl_diag = tk.Label(
            card,
            text=diagram,
            font=("Consolas", 9),
            fg=ACCENT_CYAN,
            bg="#181820",
            justify=tk.LEFT,
            padx=10,
            pady=10,
        )
        lbl_diag.pack(fill=tk.X, pady=12)

        notes = (
            "• Preamble & SFD: 7 bytes of 10101010 sync pattern + 1 byte Start Frame Delimiter (10101011).\n"
            "• MAC Addresses: 48 bits (6 bytes). First 24 bits = OUI (Vendor ID); Last 24 bits = Device NIC.\n"
            "• EtherTypes to Memorize:\n"
            "    - 0x0800 -> IPv4\n"
            "    - 0x86DD -> IPv6\n"
            "    - 0x0806 -> ARP\n"
            "    - 0x8100 -> IEEE 802.1Q (VLAN-tagged frame)\n"
            "• FCS (Frame Check Sequence): 4-byte CRC-32 checksum. Corrupted frames are silently dropped."
        )
        tk.Label(
            card,
            text=notes,
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_CARD,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=5)
        return tab

    def create_dot1q_tab(self):
        tab = tk.Frame(self.notebook, bg=BG_DARK)
        card = self.create_card_frame(tab)

        tk.Label(
            card,
            text="802.1Q VLAN TRUNKING TAG (4 BYTES INSERTED)",
            font=(FONT_FAMILY, 13, "bold"),
            fg=ACCENT_MAGENTA,
            bg=BG_CARD,
        ).pack(anchor=tk.W)

        diagram = (
            "+-----------------------------------+--------------+-------------+-----------------------+\n"
            "|     TPID: 0x8100 (16 bits)        | PCP (3 bits) | DEI (1 bit) |     VID (12 bits)     |\n"
            "+-----------------------------------+--------------+-------------+-----------------------+"
        )
        lbl_diag = tk.Label(
            card,
            text=diagram,
            font=("Consolas", 9),
            fg=ACCENT_CYAN,
            bg="#181820",
            justify=tk.LEFT,
            padx=10,
            pady=10,
        )
        lbl_diag.pack(fill=tk.X, pady=12)

        notes = (
            "• Placement: Tag is inserted between the Source MAC and EtherType fields of the original frame.\n"
            "• TPID (Tag Protocol Identifier): Fixed at 0x8100. Flags that an 802.1Q header follows.\n"
            "• PCP (Priority Code Point): 3 bits -> Defines 8 Class of Service (CoS) priority levels (0 to 7).\n"
            "• DEI (Drop Eligible Indicator): 1 bit -> Discard preference when trunk links encounter congestion.\n"
            "• VID (VLAN Identifier): 12 bits -> 2^12 = 4096 IDs:\n"
            "    - 0 and 4095: Reserved.\n"
            "    - 1 to 4094: Usable VLAN range (1-1005 standard, 1006-4094 extended)."
        )
        tk.Label(
            card,
            text=notes,
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_CARD,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=5)
        return tab

    def create_ipv4_tab(self):
        tab = tk.Frame(self.notebook, bg=BG_DARK)
        card = self.create_card_frame(tab)

        tk.Label(
            card,
            text="IPv4 PACKET HEADER (20-60 BYTES)",
            font=(FONT_FAMILY, 13, "bold"),
            fg=ACCENT_CYAN,
            bg=BG_CARD,
        ).pack(anchor=tk.W)

        diagram = (
            "+---------------+---------------+---------------+---------------+\n"
            "|Version|  IHL  |Type of Service|          Total Length         |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|         Identification        |Flags|     Fragment Offset     |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|  Time to Live |    Protocol   |        Header Checksum        |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|                       Source IP Address                       |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|                    Destination IP Address                     |\n"
            "+---------------+---------------+---------------+---------------+"
        )
        lbl_diag = tk.Label(
            card,
            text=diagram,
            font=("Consolas", 8),
            fg=ACCENT_CYAN,
            bg="#181820",
            justify=tk.LEFT,
            padx=10,
            pady=8,
        )
        lbl_diag.pack(fill=tk.X, pady=8)

        notes = (
            "• TTL (Time to Live): Decremented by 1 at each router hop. When it reaches 0, router drops\n"
            "  packet and generates an ICMP Type 11 (Time Exceeded) message back to the sender.\n"
            "• Protocol Numbers to Know for CCNA:\n"
            "    - 1  -> ICMP\n"
            "    - 6  -> TCP\n"
            "    - 17 -> UDP\n"
            "    - 89 -> OSPF\n"
            "• Header Checksum: Verifies L3 header integrity only (recomputed at every hop as TTL changes)."
        )
        tk.Label(
            card,
            text=notes,
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_CARD,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=4)
        return tab

    def create_ipv6_tab(self):
        tab = tk.Frame(self.notebook, bg=BG_DARK)
        card = self.create_card_frame(tab)

        tk.Label(
            card,
            text="IPv6 FIXED BASE HEADER (EXACTLY 40 BYTES)",
            font=(FONT_FAMILY, 13, "bold"),
            fg=ACCENT_CYAN,
            bg=BG_CARD,
        ).pack(anchor=tk.W)

        diagram = (
            "+---------------+---------------+---------------+---------------+\n"
            "|Version| Traffic Class |                  Flow Label           |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|         Payload Length        |  Next Header  |   Hop Limit   |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|                  Source IPv6 Address (128 bits)               |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|               Destination IPv6 Address (128 bits)             |\n"
            "+---------------+---------------+---------------+---------------+"
        )
        lbl_diag = tk.Label(
            card,
            text=diagram,
            font=("Consolas", 8),
            fg=ACCENT_CYAN,
            bg="#181820",
            justify=tk.LEFT,
            padx=10,
            pady=8,
        )
        lbl_diag.pack(fill=tk.X, pady=8)

        notes = (
            "• Streamlined Header: Exactly 8 fields (IPv4 has 14). Fixed 40-byte size accelerates router lookups.\n"
            "• Hop Limit: Direct equivalent to IPv4 TTL.\n"
            "• Next Header: Replaces IPv4 Protocol field. Points directly to L4 payload (e.g. 6 TCP) or to\n"
            "  chained IPv6 extension headers (Routing, Fragmentation, Security).\n"
            "• No L3 Header Checksum: IPv6 relies on Layer 2 and Layer 4 checksums, reducing per-hop CPU load."
        )
        tk.Label(
            card,
            text=notes,
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_CARD,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=4)
        return tab

    def create_tcp_tab(self):
        tab = tk.Frame(self.notebook, bg=BG_DARK)
        card = self.create_card_frame(tab)

        tk.Label(
            card,
            text="TCP SEGMENT HEADER (20-60 BYTES)",
            font=(FONT_FAMILY, 13, "bold"),
            fg=ACCENT_GREEN,
            bg=BG_CARD,
        ).pack(anchor=tk.W)

        diagram = (
            "+---------------+---------------+---------------+---------------+\n"
            "|          Source Port          |       Destination Port        |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|                        Sequence Number                        |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|                    Acknowledgment Number                      |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|  Data |       |U|A|P|R|S|F|                                   |\n"
            "| Offset|  Res  |R|C|S|S|Y|I|            Window Size            |\n"
            "|       |       |G|K|H|T|N|N|                                   |\n"
            "+---------------+---------------+---------------+---------------+\n"
            "|           Checksum            |         Urgent Pointer        |\n"
            "+---------------+---------------+---------------+---------------+"
        )
        lbl_diag = tk.Label(
            card,
            text=diagram,
            font=("Consolas", 8),
            fg=ACCENT_GREEN,
            bg="#181820",
            justify=tk.LEFT,
            padx=10,
            pady=8,
        )
        lbl_diag.pack(fill=tk.X, pady=8)

        notes = (
            "• 3-Way Handshake Flags: Step 1 (SYN) -> Step 2 (SYN-ACK) -> Step 3 (ACK).\n"
            "• Core Control Flags:\n"
            "    - SYN: Synchronize initial sequence numbers.\n"
            "    - ACK: Acknowledgment field valid (present on all packets after initial SYN).\n"
            "    - FIN: Graceful connection termination.\n"
            "    - RST: Reset connection immediately (closed port or rejected handshake).\n"
            "• Window Size: Flow control mechanism indicating receiver buffer capacity in bytes."
        )
        tk.Label(
            card,
            text=notes,
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_CARD,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=4)
        return tab

    def create_quiz_tab(self):
        tab = tk.Frame(self.notebook, bg=BG_DARK)
        card = self.create_card_frame(tab)

        top_row = tk.Frame(card, bg=BG_CARD)
        top_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            top_row,
            text="⚡ PROTOCOL & FIELD SPEED-DRILL",
            font=(FONT_FAMILY, 13, "bold"),
            fg=ACCENT_CYAN,
            bg=BG_CARD,
        ).pack(side=tk.LEFT)

        self.quiz_score_lbl = tk.Label(
            top_row,
            text="Score: 0/0 (0%)",
            font=(FONT_FAMILY, 11, "bold"),
            fg=TEXT_COLOR,
            bg=BG_CARD,
        )
        self.quiz_score_lbl.pack(side=tk.RIGHT)

        # Question area
        self.q_text_lbl = tk.Label(
            card,
            text="Loading drill question...",
            font=(FONT_FAMILY, 12, "bold"),
            fg=ACCENT_YELLOW,
            bg=BG_CARD,
            wraplength=660,
            justify=tk.LEFT,
        )
        self.q_text_lbl.pack(anchor=tk.W, pady=(15, 12))

        # Entry row
        entry_row = tk.Frame(card, bg=BG_CARD)
        entry_row.pack(fill=tk.X, pady=(0, 15))

        self.entry_var = tk.StringVar()
        self.quiz_entry = tk.Entry(
            entry_row,
            textvariable=self.entry_var,
            font=("Consolas", 14),
            bg="#121217",
            fg="#ffffff",
            insertbackground="#ffffff",
            bd=0,
            highlightthickness=1,
            highlightbackground="#444455",
            highlightcolor=ACCENT_CYAN,
        )
        self.quiz_entry.pack(
            side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10)
        )
        self.quiz_entry.bind("<Return>", lambda event: self.handle_action())

        self.action_btn = tk.Button(
            entry_row,
            text="Submit ↵",
            font=(FONT_FAMILY, 10, "bold"),
            bg=ACCENT_CYAN,
            fg="#121217",
            activebackground="#00b4d8",
            relief=tk.FLAT,
            padx=18,
            cursor="hand2",
            command=self.handle_action,
        )
        self.action_btn.pack(side=tk.RIGHT, fill=tk.Y)

        # Feedback box
        self.quiz_feedback_frame = tk.Frame(
            card,
            bg="#21212a",
            padx=15,
            pady=15,
            highlightbackground="#3d3d4d",
            highlightthickness=1,
        )
        self.quiz_feedback_frame.pack(fill=tk.BOTH, expand=True)

        self.quiz_status_lbl = tk.Label(
            self.quiz_feedback_frame,
            text="Type your answer above and press Enter.",
            font=(FONT_FAMILY, 12, "bold"),
            fg="#8b8b9e",
            bg="#21212a",
        )
        self.quiz_status_lbl.pack(anchor=tk.W)

        self.quiz_answer_lbl = tk.Label(
            self.quiz_feedback_frame,
            text="",
            font=("Consolas", 11),
            fg=TEXT_COLOR,
            bg="#21212a",
        )
        self.quiz_answer_lbl.pack(anchor=tk.W, pady=(4, 6))

        self.quiz_hint_lbl = tk.Label(
            self.quiz_feedback_frame,
            text="",
            font=(FONT_FAMILY, 10),
            fg="#a0a0b2",
            bg="#21212a",
            wraplength=640,
            justify=tk.LEFT,
        )
        self.quiz_hint_lbl.pack(anchor=tk.W)

        return tab

    def handle_action(self):
        if self.is_waiting_for_next:
            self.next_quiz_question()
        else:
            self.check_quiz_answer()

    def next_quiz_question(self):
        if not self.available_questions:
            self.available_questions = list(self.questions_bank)
            random.shuffle(self.available_questions)

        self.current_q = self.available_questions.pop()
        self.is_waiting_for_next = False
        self.action_btn.config(text="Submit ↵", bg=ACCENT_CYAN)

        self.q_text_lbl.config(text=self.current_q["q"])
        self.entry_var.set("")
        self.quiz_entry.config(state=tk.NORMAL)
        self.quiz_entry.focus_set()
        self.quiz_status_lbl.config(
            text="Awaiting response...", fg="#8b8b9e"
        )
        self.quiz_answer_lbl.config(text="")
        self.quiz_hint_lbl.config(text="")
        self.start_time = time.time()

    def check_quiz_answer(self):
        user_input = self.entry_var.get().strip().lower()
        if not user_input:
            return

        elapsed = round(time.time() - self.start_time, 2)
        self.total += 1

        valid_answers = [a.lower() for a in self.current_q["aliases"]]

        if user_input in valid_answers:
            self.score += 1
            self.quiz_status_lbl.config(
                text=f"✔ CORRECT! ({elapsed}s)", fg=ACCENT_GREEN
            )
            self.quiz_answer_lbl.config(
                text=f"Expected: {self.current_q['a']}", fg=ACCENT_GREEN
            )
            self.quiz_hint_lbl.config(
                text="Press Enter or click 'Next ➔' to continue.",
                fg="#a0a0b2",
            )
            btn_color = ACCENT_GREEN
        else:
            self.quiz_status_lbl.config(
                text=f"✘ INCORRECT ({elapsed}s)", fg=ACCENT_RED
            )
            self.quiz_answer_lbl.config(
                text=f"Expected: {self.current_q['a']}  |  You entered: {self.entry_var.get()}",
                fg=TEXT_COLOR,
            )
            self.quiz_hint_lbl.config(
                text=f"Review Note: {self.current_q['hint']}",
                fg=ACCENT_YELLOW,
            )
            btn_color = "#3b3b4f"

        self.is_waiting_for_next = True
        self.action_btn.config(text="Next ➔", bg=btn_color)

        pct = round((self.score / self.total) * 100, 1)
        self.quiz_score_lbl.config(
            text=f"Score: {self.score}/{self.total} ({pct}%)"
        )


if __name__ == "__main__":
  app = HeaderInspectorApp()
  app.mainloop()