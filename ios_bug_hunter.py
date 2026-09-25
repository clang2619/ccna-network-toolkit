#!/usr/bin/env python3
"""
CCNA Cisco IOS Config & Bug Hunter GUI
Troubleshoot broken running-config snippets and identify flawed commands.
Requires Python 3 standard library only (tkinter).
"""

import tkinter as tk
from tkinter import ttk
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


class IOSBugHunterApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("CCNA Cisco IOS Bug Hunter")
        self.geometry("820x760")
        self.minsize(740, 700)
        self.configure(bg=BG_DARK)

        self.score = 0
        self.total = 0
        self.start_time = 0
        self.current_scenario = None
        self.is_waiting_for_next = False
        self.selected_choice = tk.IntVar(value=-1)

        self.scenario_pool = [
            {
                "title": "VLAN Trunking: Native VLAN Mismatch",
                "symptom": "CDP reports '%CDP-4-NATIVE_VLAN_MISMATCH' on GigabitEthernet0/1 between SW1 and SW2. Traffic in VLAN 10 leaks into VLAN 20.",
                "config_lines": [
                    "interface GigabitEthernet0/1",
                    " description Trunk link to SW2",
                    " switchport trunk encapsulation dot1q",
                    " switchport mode trunk",
                    " switchport trunk native vlan 20",
                    " switchport trunk allowed vlan 10,20,30",
                    " no shutdown"
                ],
                "bug_index": 4,
                "explanation": "SW1 has native VLAN set to 20 while SW2 is set to 10 (or default 1). Native VLAN IDs must match on both ends of an 802.1Q trunk to prevent untagged frame cross-talk.",
                "verify_cmd": "show interfaces trunk | show interfaces gigabitEthernet 0/1 switchport"
            },
            {
                "title": "OSPF: Wildcard Mask Logic Error",
                "symptom": "R1 is supposed to advertise subnet 192.168.10.0/26 into Area 0, but neighbors never receive routes for this subnet.",
                "config_lines": [
                    "router ospf 1",
                    " router-id 1.1.1.1",
                    " log-adjacency-changes",
                    " network 192.168.10.0 0.0.0.128 area 0",
                    " exit"
                ],
                "bug_index": 3,
                "explanation": "A /26 subnet has netmask 255.255.255.192. The correct inverse wildcard mask is 0.0.0.63 (255 - 192 = 63), NOT 0.0.0.128.",
                "verify_cmd": "show ip protocols | show ip ospf interface brief"
            },
            {
                "title": "OSPF: Passive Interface on Peer Link",
                "symptom": "R1 and R2 are directly connected via Gi0/0. Both are configured for OSPF Area 0, but neighbor adjacency remains in DOWN state.",
                "config_lines": [
                    "interface GigabitEthernet0/0",
                    " ip address 10.0.0.1 255.255.255.252",
                    " no shutdown",
                    "router ospf 1",
                    " router-id 1.1.1.1",
                    " passive-interface GigabitEthernet0/0",
                    " network 10.0.0.0 0.0.0.3 area 0"
                ],
                "bug_index": 5,
                "explanation": "The 'passive-interface GigabitEthernet0/0' command suppresses sending and receiving OSPF Hello packets on that link, preventing neighbor formation.",
                "verify_cmd": "show ip ospf neighbor | show ip protocols"
            },
            {
                "title": "Router-on-a-Stick: Missing Subinterface 802.1Q Encapsulation",
                "symptom": "R1 subinterface for VLAN 30 fails to route traffic from hosts on SW1 port Fa0/1.",
                "config_lines": [
                    "interface GigabitEthernet0/0.30",
                    " description Gateway for VLAN 30 Sales",
                    " ip address 192.168.30.1 255.255.255.0",
                    " no shutdown"
                ],
                "bug_index": 2,
                "explanation": "Before assigning an IP address to a router subinterface for 802.1Q trunking, you must execute 'encapsulation dot1Q <vlan-id>'. Without it, the router cannot tag or decapsulate frames.",
                "verify_cmd": "show ip interface brief | show vlans"
            },
            {
                "title": "SSH Access: Missing Domain Name for RSA Key Generation",
                "symptom": "Administrator attempts to generate cryptographic keys for SSH using 'crypto key generate rsa', but the router rejects the command.",
                "config_lines": [
                    "hostname Core-Rtr",
                    "username admin privilege 15 secret C1sc0123",
                    "line vty 0 4",
                    " login local",
                    " transport input ssh",
                    "crypto key generate rsa modulus 2048"
                ],
                "bug_index": 5,
                "explanation": "Cisco IOS requires a domain name ('ip domain-name example.com') prior to generating RSA key pairs because the Fully Qualified Domain Name (FQDN) forms the key certificate name.",
                "verify_cmd": "show ip ssh | show running-config | include domain"
            },
            {
                "title": "Standard ACL: Applied Close to Source Instead of Destination",
                "symptom": "Administrator applies Standard ACL 10 on R1 GigabitEthernet0/0 inbound to stop PC1 from reaching Server A (10.2.2.10). Suddenly PC1 cannot access the Internet or local printers either.",
                "config_lines": [
                    "access-list 10 deny host 192.168.1.50",
                    "access-list 10 permit any",
                    "interface GigabitEthernet0/0",
                    " description Default Gateway for LAN 1",
                    " ip access-group 10 in"
                ],
                "bug_index": 4,
                "explanation": "Standard ACLs evaluate ONLY source IP addresses. Best practice dictates standard ACLs must be placed as close to the DESTINATION as possible. Placing it inbound on PC1's local gateway cuts off all traffic everywhere.",
                "verify_cmd": "show access-lists | show ip interface GigabitEthernet0/0"
            }
        ]
        self.remaining_scenarios = list(self.scenario_pool)
        random.shuffle(self.remaining_scenarios)

        self.build_ui()
        self.generate_new_scenario()

    def build_ui(self):
        # Header banner
        header = tk.Frame(self, bg=BG_DARK, pady=10)
        header.pack(fill=tk.X, padx=20)

        title_lbl = tk.Label(
            header,
            text="🕵️ CISCO IOS CONFIG & BUG HUNTER",
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

        # Scenario Title and Symptom Card
        self.card = tk.Frame(self, bg=BG_CARD, padx=16, pady=12, highlightbackground="#3d3d4d", highlightthickness=1)
        self.card.pack(fill=tk.X, padx=20, pady=(5, 10))

        self.scenario_title_lbl = tk.Label(
            self.card,
            text="SCENARIO TITLE",
            font=(FONT_FAMILY, 11, "bold"),
            fg=ACCENT_YELLOW,
            bg=BG_CARD
        )
        self.scenario_title_lbl.pack(anchor=tk.W)

        self.symptom_lbl = tk.Label(
            self.card,
            text="Symptom description...",
            font=(FONT_FAMILY, 10),
            fg=TEXT_COLOR,
            bg=BG_CARD,
            wraplength=760,
            justify=tk.LEFT
        )
        self.symptom_lbl.pack(anchor=tk.W, pady=(4, 2))

        # Config lines selection area
        self.lines_frame = tk.Frame(self, bg="#16161c", padx=14, pady=10, highlightbackground="#3d3d4d", highlightthickness=1)
        self.lines_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        tk.Label(
            self.lines_frame,
            text="RUNNING-CONFIG SNIPPET (Select the flawed command line):",
            font=(FONT_FAMILY, 9, "bold"),
            fg="#8b8b9e",
            bg="#16161c"
        ).pack(anchor=tk.W, pady=(0, 8))

        self.radio_container = tk.Frame(self.lines_frame, bg="#16161c")
        self.radio_container.pack(fill=tk.BOTH, expand=True)

        # Control Row
        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(fill=tk.X, padx=20, pady=(0, 8))

        self.action_btn = tk.Button(
            btn_row,
            text="Inspect & Submit ↵",
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

        # Diagnostic Review Card
        self.feedback_box = tk.Frame(self, bg=BG_CARD, padx=14, pady=12, highlightbackground="#3d3d4d", highlightthickness=1)
        self.feedback_box.pack(fill=tk.X, padx=20, pady=(0, 14))

        self.status_lbl = tk.Label(
            self.feedback_box,
            text="Select the line causing the malfunction and submit.",
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

        self.verify_lbl = tk.Label(
            self.feedback_box,
            text="",
            font=("Consolas", 9),
            fg=ACCENT_CYAN,
            bg=BG_CARD,
            wraplength=760,
            justify=tk.LEFT
        )
        self.verify_lbl.pack(anchor=tk.W)

        # Bind Enter to action
        self.bind("<Return>", lambda e: self.handle_action())

    def handle_action(self):
        if self.is_waiting_for_next:
            self.generate_new_scenario()
        else:
            self.check_answer()

    def generate_new_scenario(self):
        if not self.remaining_scenarios:
            self.remaining_scenarios = list(self.scenario_pool)
            random.shuffle(self.remaining_scenarios)

        self.current_scenario = self.remaining_scenarios.pop()
        self.is_waiting_for_next = False
        self.selected_choice.set(-1)
        self.action_btn.config(text="Inspect & Submit ↵", bg=ACCENT_CYAN)

        # Update labels
        self.scenario_title_lbl.config(text=f"SCENARIO: {self.current_scenario['title']}")
        self.symptom_lbl.config(text=f"Symptom: {self.current_scenario['symptom']}")
        self.status_lbl.config(text="Select the flawed command line from the configuration snippet:", fg="#8b8b9e")
        self.explanation_lbl.config(text="")
        self.verify_lbl.config(text="")

        # Rebuild radio buttons for config lines
        for child in self.radio_container.winfo_children():
            child.destroy()

        self.radio_buttons = []
        for idx, line in enumerate(self.current_scenario["config_lines"]):
            rb = tk.Radiobutton(
                self.radio_container,
                text=f"  {line}",
                variable=self.selected_choice,
                value=idx,
                font=("Consolas", 10),
                bg="#16161c",
                fg=TEXT_COLOR,
                activebackground="#16161c",
                activeforeground=ACCENT_CYAN,
                selectcolor="#2b2b36",
                anchor=tk.W,
                pady=3,
                cursor="hand2"
            )
            rb.pack(fill=tk.X)
            self.radio_buttons.append(rb)

        self.start_time = time.time()

    def check_answer(self):
        choice = self.selected_choice.get()
        if choice == -1:
            self.status_lbl.config(text="Please click on a command line before submitting.", fg=ACCENT_YELLOW)
            return

        elapsed = round(time.time() - self.start_time, 2)
        self.total += 1
        correct_idx = self.current_scenario["bug_index"]

        # Lock radios
        for rb in self.radio_buttons:
            rb.config(state=tk.DISABLED)

        if choice == correct_idx:
            self.score += 1
            self.status_lbl.config(text=f"✔ ROOT CAUSE IDENTIFIED! ({elapsed}s)", fg=ACCENT_GREEN)
            self.radio_buttons[correct_idx].config(fg=ACCENT_GREEN)
            btn_color = ACCENT_GREEN
        else:
            self.status_lbl.config(text=f"✘ INCORRECT LINE SELECTED ({elapsed}s)", fg=ACCENT_RED)
            self.radio_buttons[choice].config(fg=ACCENT_RED)
            self.radio_buttons[correct_idx].config(fg=ACCENT_GREEN)
            btn_color = "#3b3b4f"

        self.explanation_lbl.config(
            text=f"Diagnostic Analysis:\n{self.current_scenario['explanation']}"
        )
        self.verify_lbl.config(
            text=f"Cisco IOS Verification Commands:\n# {self.current_scenario['verify_cmd']}"
        )

        self.is_waiting_for_next = True
        self.action_btn.config(text="Next Scenario ➔", bg=btn_color)

        pct = round((self.score / self.total) * 100, 1)
        self.score_lbl.config(text=f"Score: {self.score}/{self.total} ({pct}%)")


if __name__ == "__main__":
    app = IOSBugHunterApp()
    app.mainloop()