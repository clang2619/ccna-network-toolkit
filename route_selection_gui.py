#!/usr/bin/env python3
"""
CCNA Route Selection Duel & AD Trainer GUI
Drills routing table lookup order: Longest Prefix Match -> AD -> Metric.
Requires Python 3 standard library only (tkinter + ipaddress).
"""

import tkinter as tk
from tkinter import ttk
import ipaddress
import random
import time

# --- Dark Terminal Styling ---
BG_DARK = "#1e1e24"
BG_CARD = "#2b2b36"
TEXT_COLOR = "#f0f0f5"
ACCENT_CYAN = "#00d4ff"
ACCENT_GREEN = "#2ecc71"
ACCENT_RED = "#e74c3c"
ACCENT_YELLOW = "#f39c12"
FONT_FAMILY = "Segoe UI"


class RouteSelectionApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("CCNA Route Selection & AD Trainer")
        self.geometry("820x760")
        self.minsize(740, 700)
        self.configure(bg=BG_DARK)

        self.score = 0
        self.total = 0
        self.start_time = 0
        self.current_scenario = None
        self.is_waiting_for_next = False
        self.selected_choice = tk.IntVar(value=-1)

        self.build_ui()
        self.generate_new_scenario()

    def build_ui(self):
        header = tk.Frame(self, bg=BG_DARK, pady=10)
        header.pack(fill=tk.X, padx=20)

        title_lbl = tk.Label(
            header,
            text="🧭 CCNA ROUTE SELECTION DUEL",
            font=(FONT_FAMILY, 15, "bold"),
            fg=ACCENT_CYAN,
            bg=BG_DARK
        )
        title_lbl.pack(side=tk.LEFT)

        self.score_lbl = tk.Label(
            header,
            text="Score: 0/0 (0%)",
            font=(FONT_FAMILY, 11, "bold"),
            fg=TEXT_COLOR,
            bg=BG_DARK
        )
        self.score_lbl.pack(side=tk.RIGHT)

        # Inbound packet scenario banner
        self.card = tk.Frame(self, bg=BG_CARD, padx=16, pady=12, highlightbackground="#3d3d4d", highlightthickness=1)
        self.card.pack(fill=tk.X, padx=20, pady=(5, 10))

        self.mode_lbl = tk.Label(
            self.card,
            text="SCENARIO TYPE",
            font=(FONT_FAMILY, 9, "bold"),
            fg="#8b8b9e",
            bg=BG_CARD
        )
        self.mode_lbl.pack(anchor=tk.W)

        self.packet_desc_lbl = tk.Label(
            self.card,
            text="Destination Packet IP...",
            font=("Consolas", 12, "bold"),
            fg=ACCENT_YELLOW,
            bg=BG_CARD
        )
        self.packet_desc_lbl.pack(anchor=tk.W, pady=(4, 2))

        # Candidate routes container
        self.routes_frame = tk.Frame(self, bg="#16161c", padx=14, pady=10, highlightbackground="#3d3d4d", highlightthickness=1)
        self.routes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        tk.Label(
            self.routes_frame,
            text="CANDIDATE ROUTES (Select the path the router will choose):",
            font=(FONT_FAMILY, 9, "bold"),
            fg="#8b8b9e",
            bg="#16161c"
        ).pack(anchor=tk.W, pady=(0, 8))

        self.radio_container = tk.Frame(self.routes_frame, bg="#16161c")
        self.radio_container.pack(fill=tk.BOTH, expand=True)

        # Control Row
        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(fill=tk.X, padx=20, pady=(0, 8))

        self.action_btn = tk.Button(
            btn_row,
            text="Select Route ↵",
            font=(FONT_FAMILY, 10, "bold"),
            bg=ACCENT_CYAN,
            fg="#121217",
            activebackground="#00b4d8",
            relief=tk.FLAT,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self.handle_action
        )
        self.action_btn.pack(side=tk.RIGHT)

        # Diagnostic review box
        self.feedback_box = tk.Frame(self, bg=BG_CARD, padx=14, pady=12, highlightbackground="#3d3d4d", highlightthickness=1)
        self.feedback_box.pack(fill=tk.X, padx=20, pady=(0, 14))

        self.status_lbl = tk.Label(
            self.feedback_box,
            text="Select the chosen routing table entry and click submit.",
            font=(FONT_FAMILY, 11, "bold"),
            fg="#8b8b9e",
            bg=BG_CARD
        )
        self.status_lbl.pack(anchor=tk.W)

        self.explanation_lbl = tk.Label(
            self.feedback_box,
            text="",
            font=(FONT_FAMILY, 9),
            fg=TEXT_COLOR,
            bg=BG_CARD,
            wraplength=760,
            justify=tk.LEFT
        )
        self.explanation_lbl.pack(anchor=tk.W, pady=(4, 2))

        self.rule_lbl = tk.Label(
            self.feedback_box,
            text="",
            font=("Consolas", 9),
            fg=ACCENT_CYAN,
            bg=BG_CARD,
            wraplength=760,
            justify=tk.LEFT
        )
        self.rule_lbl.pack(anchor=tk.W)

        self.bind("<Return>", lambda e: self.handle_action())

    def handle_action(self):
        if self.is_waiting_for_next:
            self.generate_new_scenario()
        else:
            self.check_answer()

    def generate_longest_prefix_drill(self):
        dest_ip = ipaddress.ip_address("172.16.10.45")
        routes = [
            {"src": "Static", "ad": 1, "net": "172.16.0.0/16", "via": "via 192.168.1.1", "metric": 0},
            {"src": "OSPF", "ad": 110, "net": "172.16.10.0/24", "via": "via 10.0.0.2", "metric": 20},
            {"src": "RIP", "ad": 120, "net": "172.16.10.32/27", "via": "via 10.1.1.2", "metric": 3},
            {"src": "Connected", "ad": 0, "net": "10.0.0.0/8", "via": "is directly connected", "metric": 0}
        ]

        # 172.16.10.45 fits:
        # /16 (172.16.0.0 - 172.16.255.255)
        # /24 (172.16.10.0 - 172.16.10.255)
        # /27 (172.16.10.32 - 172.16.10.63) -> 45 is inside this range! /27 is longest!
        correct_idx = 2

        return {
            "mode": "PACKET FORWARDING: LONGEST PREFIX MATCH",
            "packet": f"Inbound Packet Destination IP: {dest_ip}",
            "routes": routes,
            "correct_idx": correct_idx,
            "explanation": (
                "Even though Static (AD 1) and OSPF (AD 110) have much lower Administrative Distances than RIP (AD 120), "
                "the router evaluates the LONGEST PREFIX MATCH first! The /27 mask is the most specific route matching 172.16.10.45."
            ),
            "rule": "CCNA Law: 1) Longest Prefix Match ALWAYS wins. 2) AD only compares identical prefix lengths."
        }

    def generate_ad_drill(self):
        dest_ip = ipaddress.ip_address("192.168.50.10")
        target_net = "192.168.50.0/24"

        routes = [
            {"src": "OSPF", "ad": 110, "net": target_net, "via": "via 10.1.1.1", "metric": 10},
            {"src": "EIGRP (Internal)", "ad": 90, "net": target_net, "via": "via 10.2.2.1", "metric": 307200},
            {"src": "RIPv2", "ad": 120, "net": target_net, "via": "via 10.3.3.1", "metric": 2},
            {"src": "External EIGRP", "ad": 170, "net": target_net, "via": "via 10.4.4.1", "metric": 281600}
        ]
        # Identical prefix length (/24): Lowest AD wins -> EIGRP Internal (AD 90)
        correct_idx = 1

        return {
            "mode": "ROUTE INSTALLATION: ADMINISTRATIVE DISTANCE (AD)",
            "packet": f"Router learns identical prefix '{target_net}' from 4 routing sources simultaneously:",
            "routes": routes,
            "correct_idx": correct_idx,
            "explanation": (
                "When multiple routing protocols advertise the EXACT same prefix length (/24), "
                "the routing process compares Administrative Distance (believability). EIGRP Internal has an AD of 90, "
                "which beats OSPF (110), RIP (120), and External EIGRP (170)."
            ),
            "rule": "AD Hierarchy: Connected (0) < Static (1) < eBGP (20) < EIGRP (90) < OSPF (110) < RIP (120) < Ext EIGRP (170) < iBGP (200)."
        }

    def generate_floating_static_drill(self):
        target_net = "10.50.0.0/16"
        routes = [
            {"src": "OSPF Primary Link", "ad": 110, "net": target_net, "via": "via 172.16.1.1", "metric": 110},
            {"src": "Floating Static Backup", "ad": 115, "net": target_net, "via": "via 172.16.2.1 (AD 115)", "metric": 0},
            {"src": "RIP Legacy Path", "ad": 120, "net": target_net, "via": "via 172.16.3.1", "metric": 4}
        ]
        # While OSPF link is Up, OSPF AD 110 beats Floating Static AD 115
        correct_idx = 0

        return {
            "mode": "FLOATING STATIC ROUTE EVALUATION",
            "packet": f"Target Subnet: {target_net} (All interfaces are UP / UP)",
            "routes": routes,
            "correct_idx": correct_idx,
            "explanation": (
                "A Floating Static route is configured with an Administrative Distance higher than the dynamic routing protocol "
                "(here AD 115 vs OSPF 110). Because the primary link is active, OSPF (110) is installed into the routing table. "
                "The floating static route will only enter the table if the OSPF route goes down."
            ),
            "rule": "Floating Static Formula: Configured with AD > Dynamic Protocol AD (e.g. 'ip route 10.50.0.0 255.255.0.0 172.16.2.1 115')."
        }

    def generate_new_scenario(self):
        generators = [
            self.generate_longest_prefix_drill,
            self.generate_ad_drill,
            self.generate_floating_static_drill
        ]
        self.current_scenario = random.choice(generators)()
        self.is_waiting_for_next = False
        self.selected_choice.set(-1)
        self.action_btn.config(text="Select Route ↵", bg=ACCENT_CYAN)

        self.mode_lbl.config(text=f"TOPIC: {self.current_scenario['mode']}")
        self.packet_desc_lbl.config(text=self.current_scenario["packet"])
        self.status_lbl.config(text="Select the route the router will use to forward or install traffic:", fg="#8b8b9e")
        self.explanation_lbl.config(text="")
        self.rule_lbl.config(text="")

        for child in self.radio_container.winfo_children():
            child.destroy()

        self.radio_buttons = []
        for idx, r in enumerate(self.current_scenario["routes"]):
            line_txt = f"[{r['src'].upper()}]  Prefix: {r['net']:<18} | AD: {r['ad']:<3} | Metric: {r['metric']:<6} | {r['via']}"
            rb = tk.Radiobutton(
                self.radio_container,
                text=f"  {line_txt}",
                variable=self.selected_choice,
                value=idx,
                font=("Consolas", 10),
                bg="#16161c",
                fg=TEXT_COLOR,
                activebackground="#16161c",
                activeforeground=ACCENT_CYAN,
                selectcolor="#2b2b36",
                anchor=tk.W,
                pady=4,
                cursor="hand2"
            )
            rb.pack(fill=tk.X)
            self.radio_buttons.append(rb)

        self.start_time = time.time()

    def check_answer(self):
        choice = self.selected_choice.get()
        if choice == -1:
            self.status_lbl.config(text="Please select one of the candidate routes first.", fg=ACCENT_YELLOW)
            return

        elapsed = round(time.time() - self.start_time, 2)
        self.total += 1
        correct_idx = self.current_scenario["correct_idx"]

        for rb in self.radio_buttons:
            rb.config(state=tk.DISABLED)

        if choice == correct_idx:
            self.score += 1
            self.status_lbl.config(text=f"✔ CORRECT PATH SELECTED! ({elapsed}s)", fg=ACCENT_GREEN)
            self.radio_buttons[correct_idx].config(fg=ACCENT_GREEN)
            btn_color = ACCENT_GREEN
        else:
            self.status_lbl.config(text=f"✘ INCORRECT PATH ({elapsed}s)", fg=ACCENT_RED)
            self.radio_buttons[choice].config(fg=ACCENT_RED)
            self.radio_buttons[correct_idx].config(fg=ACCENT_GREEN)
            btn_color = "#3b3b4f"

        self.explanation_lbl.config(
            text=f"Analysis:\n{self.current_scenario['explanation']}"
        )
        self.rule_lbl.config(
            text=f"Routing Rule:\n{self.current_scenario['rule']}"
        )

        self.is_waiting_for_next = True
        self.action_btn.config(text="Next Scenario ➔", bg=btn_color)

        pct = round((self.score / self.total) * 100, 1)
        self.score_lbl.config(text=f"Score: {self.score}/{self.total} ({pct}%)")


if __name__ == "__main__":
    app = RouteSelectionApp()
    app.mainloop()