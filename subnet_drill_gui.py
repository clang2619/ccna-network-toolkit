#!/usr/bin/env python3
"""
CCNA Subnet Speed-Drill GUI
Interactive graphical trainer for IPv4 subnet calculations.
Requires Python 3 standard library only (tkinter + ipaddress).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress
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
FONT_FAMILY = "Segoe UI" if tk.Tk().tk.call("tk", "windowingsystem") == "win32" else "DejaVu Sans"


class SubnetDrillApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CCNA Subnet Speed-Drill")
        self.geometry("640x680")
        self.minsize(580, 620)
        self.configure(bg=BG_DARK)

        self.score = 0
        self.total = 0
        self.start_time = 0
        self.current_network = None
        self.current_interface = None
        self.current_qtype = None
        self.expected_answer = ""

        self.question_types = [
            ("Network ID", "network"),
            ("Broadcast Address", "broadcast"),
            ("First Usable Host", "first_host"),
            ("Last Usable Host", "last_host"),
            ("Usable Host Count (2^H - 2)", "usable_hosts"),
            ("Wildcard Mask", "wildcard")
        ]

        self.build_ui()
        self.generate_new_scenario()

    def build_ui(self):
        # Header / Score Banner
        header_frame = tk.Frame(self, bg=BG_DARK, pady=12)
        header_frame.pack(fill=tk.X, padx=20)

        title_lbl = tk.Label(
            header_frame, 
            text="⚡ CCNA SUBMISSION SPEED-DRILL", 
            font=(FONT_FAMILY, 15, "bold"), 
            fg=ACCENT_CYAN, 
            bg=BG_DARK
        )
        title_lbl.pack(side=tk.LEFT)

        self.score_lbl = tk.Label(
            header_frame, 
            text="Score: 0/0 (0%)", 
            font=(FONT_FAMILY, 11, "bold"), 
            fg=TEXT_COLOR, 
            bg=BG_DARK
        )
        self.score_lbl.pack(side=tk.RIGHT)

        # Scenario Card
        card = tk.Frame(self, bg=BG_CARD, bd=0, padx=20, pady=18, highlightbackground="#3d3d4d", highlightthickness=1)
        card.pack(fill=tk.X, padx=20, pady=8)

        tk.Label(card, text="GIVEN HOST & PREFIX:", font=(FONT_FAMILY, 9, "bold"), fg="#8b8b9e", bg=BG_CARD).pack(anchor=tk.W)
        self.ip_display = tk.Label(card, text="192.168.1.50/26", font=("Consolas", 20, "bold"), fg=ACCENT_YELLOW, bg=BG_CARD)
        self.ip_display.pack(anchor=tk.W, pady=(2, 8))

        tk.Label(card, text="SUBNET MASK:", font=(FONT_FAMILY, 9, "bold"), fg="#8b8b9e", bg=BG_CARD).pack(anchor=tk.W)
        self.mask_display = tk.Label(card, text="255.255.255.192", font=("Consolas", 14), fg=TEXT_COLOR, bg=BG_CARD)
        self.mask_display.pack(anchor=tk.W, pady=(2, 4))

        # Question / Input Section
        input_frame = tk.Frame(self, bg=BG_DARK, pady=15)
        input_frame.pack(fill=tk.X, padx=20)

        self.q_prompt_lbl = tk.Label(
            input_frame, 
            text="Calculate the Network ID:", 
            font=(FONT_FAMILY, 12, "bold"), 
            fg=TEXT_COLOR, 
            bg=BG_DARK
        )
        self.q_prompt_lbl.pack(anchor=tk.W, pady=(0, 8))

        entry_container = tk.Frame(input_frame, bg=BG_DARK)
        entry_container.pack(fill=tk.X)

        self.entry_var = tk.StringVar()
        self.answer_entry = tk.Entry(
            entry_container, 
            textvariable=self.entry_var, 
            font=("Consolas", 14), 
            bg="#121217", 
            fg="#ffffff", 
            insertbackground="#ffffff",
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#444455",
            highlightcolor=ACCENT_CYAN
        )
        self.answer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
        self.answer_entry.bind("<Return>", lambda event: self.check_answer())
        self.answer_entry.focus_set()

        self.submit_btn = tk.Button(
            entry_container, 
            text="Submit ↵", 
            font=(FONT_FAMILY, 10, "bold"), 
            bg=ACCENT_CYAN, 
            fg="#121217", 
            activebackground="#00b4d8", 
            relief=tk.FLAT, 
            padx=18, 
            cursor="hand2",
            command=self.check_answer
        )
        self.submit_btn.pack(side=tk.RIGHT, fill=tk.Y)

        # Feedback & Diagnostic Area
        self.feedback_frame = tk.Frame(self, bg=BG_CARD, padx=18, pady=16, highlightbackground="#3d3d4d", highlightthickness=1)
        self.feedback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 15))

        self.status_lbl = tk.Label(self.feedback_frame, text="Ready for drill...", font=(FONT_FAMILY, 12, "bold"), fg="#8b8b9e", bg=BG_CARD)
        self.status_lbl.pack(anchor=tk.W)

        self.expected_lbl = tk.Label(self.feedback_frame, text="", font=("Consolas", 11), fg=TEXT_COLOR, bg=BG_CARD)
        self.expected_lbl.pack(anchor=tk.W, pady=(4, 6))

        self.hint_lbl = tk.Label(self.feedback_frame, text="", font=(FONT_FAMILY, 10), fg="#a0a0b2", bg=BG_CARD, wraplength=520, justify=tk.LEFT)
        self.hint_lbl.pack(anchor=tk.W)

        # Bottom Buttons
        bottom_frame = tk.Frame(self, bg=BG_DARK)
        bottom_frame.pack(fill=tk.X, padx=20, pady=(0, 18))

        self.next_btn = tk.Button(
            bottom_frame, 
            text="Skip / Next Scenario ➔", 
            font=(FONT_FAMILY, 10), 
            bg="#3b3b4f", 
            fg=TEXT_COLOR, 
            relief=tk.FLAT, 
            padx=14, 
            pady=6, 
            cursor="hand2",
            command=self.generate_new_scenario
        )
        self.next_btn.pack(side=tk.RIGHT)

    def calculate_wildcard(self, netmask):
        mask_octets = [int(o) for o in str(netmask).split(".")]
        return ".".join(str(255 - o) for o in mask_octets)

    def get_block_breakdown(self, network):
        prefix = network.prefixlen
        if prefix >= 24:
            octet = 4
            borrowed = prefix - 24
        elif prefix >= 16:
            octet = 3
            borrowed = prefix - 16
        else:
            octet = 2
            borrowed = prefix - 8
        block_size = 2 ** (8 - borrowed)
        return (
            f"Mental Math Diagnostic:\n"
            f"• Prefix: /{prefix} (borrowed {borrowed} host bits in Octet #{octet})\n"
            f"• Block Size (Magic Number): 256 - mask = {block_size}\n"
            f"• Valid subnets in Octet #{octet} step by intervals of {block_size}."
        )

    def generate_new_scenario(self):
        # Generate prefix and IP
        prefix = random.randint(16, 30)
        pools = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "198.51.100.0/24"]
        base_pool = ipaddress.ip_network(random.choice(pools))
        rand_int = random.randint(int(base_pool.network_address) + 1, int(base_pool.broadcast_address) - 1)
        ip_obj = ipaddress.ip_address(rand_int)

        self.current_interface = ipaddress.ip_interface(f"{ip_obj}/{prefix}")
        self.current_network = self.current_interface.network

        label, self.current_qtype = random.choice(self.question_types)

        if self.current_qtype == "network":
            self.expected_answer = str(self.current_network.network_address)
        elif self.current_qtype == "broadcast":
            self.expected_answer = str(self.current_network.broadcast_address)
        elif self.current_qtype == "first_host":
            self.expected_answer = str(self.current_network.network_address + 1) if self.current_network.num_addresses > 2 else "N/A"
        elif self.current_qtype == "last_host":
            self.expected_answer = str(self.current_network.broadcast_address - 1) if self.current_network.num_addresses > 2 else "N/A"
        elif self.current_qtype == "usable_hosts":
            self.expected_answer = str(max(0, self.current_network.num_addresses - 2)) if self.current_network.prefixlen <= 30 else "0"
        elif self.current_qtype == "wildcard":
            self.expected_answer = self.calculate_wildcard(self.current_network.netmask)

        # Update labels
        self.ip_display.config(text=str(self.current_interface))
        self.mask_display.config(text=str(self.current_network.netmask))
        self.q_prompt_lbl.config(text=f"Calculate the {label}:")
        self.entry_var.set("")
        self.answer_entry.config(state=tk.NORMAL)
        self.answer_entry.focus_set()
        self.status_lbl.config(text="Awaiting response...", fg="#8b8b9e")
        self.expected_lbl.config(text="")
        self.hint_lbl.config(text="")
        self.start_time = time.time()

    def check_answer(self):
        user_input = self.entry_var.get().strip()
        if not user_input:
            return

        elapsed = round(time.time() - self.start_time, 2)
        self.total += 1

        if user_input == self.expected_answer:
            self.score += 1
            self.status_lbl.config(text=f"✔ CORRECT! ({elapsed}s)", fg=ACCENT_GREEN)
            self.expected_lbl.config(text=f"Value: {self.expected_answer}", fg=ACCENT_GREEN)
            self.hint_lbl.config(text=f"Great job! Fast mental block calculation.")
            # Automatically load the next challenge after a brief delay
            self.after(900, self.generate_new_scenario)
        else:
            self.status_lbl.config(text=f"✘ INCORRECT ({elapsed}s)", fg=ACCENT_RED)
            self.expected_lbl.config(
                text=f"Expected: {self.expected_answer}  |  You entered: {user_input}",
                fg=TEXT_COLOR
            )
            self.hint_lbl.config(
                text=self.get_block_breakdown(self.current_network),
                fg=ACCENT_YELLOW
            )

        pct = round((self.score / self.total) * 100, 1)
        self.score_lbl.config(text=f"Score: {self.score}/{self.total} ({pct}%)")


if __name__ == "__main__":
    app = SubnetDrillApp()
    app.mainloop()