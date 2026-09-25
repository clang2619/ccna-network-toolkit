#!/usr/bin/env python3
"""
CCNA OSPF & Routing Table Logic Trainer GUI
Drills Router ID selection, DR/BDR election, path cost math, and adjacency states.
Requires Python 3 standard library only (tkinter + ipaddress).
"""

import ipaddress
import random
import time
import tkinter as tk
from tkinter import ttk

# --- Dark Terminal Styling ---
BG_DARK = "#1e1e24"
BG_CARD = "#2b2b36"
TEXT_COLOR = "#f0f0f5"
ACCENT_CYAN = "#00d4ff"
ACCENT_GREEN = "#2ecc71"
ACCENT_RED = "#e74c3c"
ACCENT_YELLOW = "#f39c12"
FONT_FAMILY = "Segoe UI"


class OSPFTrainerApp(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title("CCNA OSPF & Metric Logic Trainer")
    self.geometry("760x730")
    self.minsize(680, 660)
    self.configure(bg=BG_DARK)

    self.score = 0
    self.total = 0
    self.start_time = 0
    self.current_scenario = None
    self.is_waiting_for_next = False

    self.build_ui()
    self.generate_new_drill()

  def build_ui(self):
    # Header Banner
    header = tk.Frame(self, bg=BG_DARK, pady=12)
    header.pack(fill=tk.X, padx=20)

    title_lbl = tk.Label(
        header,
        text="🌐 CCNA OSPF LOGIC & METRIC TRAINER",
        font=(FONT_FAMILY, 15, "bold"),
        fg=ACCENT_CYAN,
        bg=BG_DARK,
    )
    title_lbl.pack(side=tk.LEFT)

    self.score_lbl = tk.Label(
        header,
        text="Score: 0/0 (0%)",
        font=(FONT_FAMILY, 11, "bold"),
        fg=TEXT_COLOR,
        bg=BG_DARK,
    )
    self.score_lbl.pack(side=tk.RIGHT)

    # Topology & Scenario Card
    self.card = tk.Frame(
        self,
        bg=BG_CARD,
        padx=18,
        pady=16,
        highlightbackground="#3d3d4d",
        highlightthickness=1,
    )
    self.card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))

    self.category_lbl = tk.Label(
        self.card,
        text="CATEGORY: ROUTER ID ELECTION",
        font=(FONT_FAMILY, 9, "bold"),
        fg="#8b8b9e",
        bg=BG_CARD,
    )
    self.category_lbl.pack(anchor=tk.W)

    self.scenario_text = tk.Label(
        self.card,
        text="Loading topology...",
        font=("Consolas", 10),
        fg=ACCENT_YELLOW,
        bg="#181820",
        justify=tk.LEFT,
        padx=12,
        pady=10,
    )
    self.scenario_text.pack(fill=tk.BOTH, expand=True, pady=10)

    # Interactive Input Row
    input_box = tk.Frame(self, bg=BG_DARK, pady=10)
    input_box.pack(fill=tk.X, padx=20)

    self.prompt_lbl = tk.Label(
        input_box,
        text="What will become the active Router ID?",
        font=(FONT_FAMILY, 11, "bold"),
        fg=TEXT_COLOR,
        bg=BG_DARK,
    )
    self.prompt_lbl.pack(anchor=tk.W, pady=(0, 6))

    entry_row = tk.Frame(input_box, bg=BG_DARK)
    entry_row.pack(fill=tk.X)

    self.entry_var = tk.StringVar()
    self.answer_entry = tk.Entry(
        entry_row,
        textvariable=self.entry_var,
        font=("Consolas", 13),
        bg="#121217",
        fg="#ffffff",
        insertbackground="#ffffff",
        bd=0,
        highlightthickness=1,
        highlightbackground="#444455",
        highlightcolor=ACCENT_CYAN,
    )
    self.answer_entry.pack(
        side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10)
    )
    self.answer_entry.bind("<Return>", lambda e: self.handle_action())
    self.answer_entry.focus_set()

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

    # Feedback Area
    self.feedback_box = tk.Frame(
        self,
        bg="#22222b",
        padx=14,
        pady=12,
        highlightbackground="#3d3d4d",
        highlightthickness=1,
    )
    self.feedback_box.pack(fill=tk.X, padx=20, pady=(5, 15))

    self.status_lbl = tk.Label(
        self.feedback_box,
        text="Ready for scenario...",
        font=(FONT_FAMILY, 11, "bold"),
        fg="#8b8b9e",
        bg="#22222b",
    )
    self.status_lbl.pack(anchor=tk.W)

    self.expected_lbl = tk.Label(
        self.feedback_box,
        text="",
        font=("Consolas", 10),
        fg=TEXT_COLOR,
        bg="#22222b",
    )
    self.expected_lbl.pack(anchor=tk.W, pady=(2, 4))

    self.hint_lbl = tk.Label(
        self.feedback_box,
        text="",
        font=(FONT_FAMILY, 9),
        fg="#a0a0b2",
        bg="#22222b",
        wraplength=680,
        justify=tk.LEFT,
    )
    self.hint_lbl.pack(anchor=tk.W)

    # Skip / Next row
    bottom_row = tk.Frame(self, bg=BG_DARK)
    bottom_row.pack(fill=tk.X, padx=20, pady=(0, 14))

    self.skip_btn = tk.Button(
        bottom_row,
        text="Skip Scenario ➔",
        font=(FONT_FAMILY, 9),
        bg="#3b3b4f",
        fg=TEXT_COLOR,
        relief=tk.FLAT,
        padx=12,
        pady=4,
        cursor="hand2",
        command=self.generate_new_drill,
    )
    self.skip_btn.pack(side=tk.RIGHT)

  def handle_action(self):
    if self.is_waiting_for_next:
      self.generate_new_drill()
    else:
      self.check_answer()

  # --- Scenario Generators ---
  def gen_rid_drill(self):
    has_manual = random.choice([True, False])
    manual_ip = f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

    lo1 = f"192.168.{random.randint(1,20)}.{random.randint(1,254)}"
    lo2 = f"192.168.{random.randint(21,40)}.{random.randint(1,254)}"

    phys1 = f"172.16.{random.randint(1,10)}.{random.randint(1,254)}"
    phys2 = f"172.16.{random.randint(11,20)}.{random.randint(1,254)}"

    config_lines = ["Router OSPF Configuration & Active Interfaces:"]
    if has_manual:
      config_lines.append(f"  • router ospf 1 -> router-id {manual_ip}")
    else:
      config_lines.append("  • router ospf 1 (No manual router-id configured)")

    config_lines.append(f"  • Loopback0: {lo1} (Up/Up)")
    config_lines.append(f"  • Loopback1: {lo2} (Up/Up)")
    config_lines.append(f"  • GigabitEthernet0/0: {phys1} (Up/Up)")
    config_lines.append(f"  • GigabitEthernet0/1: {phys2} (Up/Up)")

    if has_manual:
      expected = manual_ip
      rule = "Rule: Manual 'router-id' always takes highest priority."
    else:
      # Compare loopbacks numerically
      expected = str(
          max(ipaddress.ip_address(lo1), ipaddress.ip_address(lo2))
      )
      rule = (
          "Rule: Without manual RID, highest numeric IP among active Loopbacks"
          " wins."
      )

    return {
        "cat": "ROUTER ID (RID) ELECTION",
        "display": "\n".join(config_lines),
        "prompt": "Enter the Router ID that OSPF will choose:",
        "expected": expected,
        "aliases": [expected],
        "hint": rule,
    }

  def gen_dr_bdr_drill(self):
    # DR / BDR on multi-access broadcast network
    r1_prio = random.choice([1, 1, 0, 100])
    r2_prio = random.choice([1, 1, 50, 200])
    r3_prio = random.choice([1, 1, 2, 255])

    r1_rid = "1.1.1.1"
    r2_rid = "2.2.2.2"
    r3_rid = "3.3.3.3"

    routers = [
        {"name": "R1", "prio": r1_prio, "rid": r1_rid},
        {"name": "R2", "prio": r2_prio, "rid": r2_rid},
        {"name": "R3", "prio": r3_prio, "rid": r3_rid},
    ]

    display = (
        "Multi-Access Ethernet Segment (Broadcast Network):\n"
        f"  • R1: Priority {r1_prio} | RID {r1_rid}\n"
        f"  • R2: Priority {r2_prio} | RID {r2_rid}\n"
        f"  • R3: Priority {r3_prio} | RID {r3_rid}\n\n"
        "All three routers boot simultaneously (no existing DR)."
    )

    # Sort key: priority desc, then RID IP desc. Note priority 0 can NEVER be DR.
    eligible = [r for r in routers if r["prio"] > 0]
    if not eligible:
      # Edge fallback
      routers[0]["prio"] = 1
      eligible = [routers[0]]

    eligible.sort(
        key=lambda r: (r["prio"], ipaddress.ip_address(r["rid"])), reverse=True
    )
    dr_router = eligible[0]["name"]

    return {
        "cat": "DR / BDR ELECTION",
        "display": display,
        "prompt": "Which router is elected as the Designated Router (DR)? (R1/R2/R3):",
        "expected": dr_router,
        "aliases": [dr_router, dr_router.lower()],
        "hint": (
            "DR Election: 1) Highest OSPF Priority (0 = DROTHER, never DR); 2)"
            " Highest RID breaks ties."
        ),
    }

  def gen_cost_drill(self):
    # Reference BW = 100 Mbps (default) or 1000 Mbps
    ref_mbps = random.choice([100, 1000])
    # Interfaces: 10M, 100M, 1000M (1G), 10000M (10G)
    interfaces = [
        ("FastEthernet (100 Mbps)", 100),
        ("GigabitEthernet (1 Gbps / 1000 Mbps)", 1000),
        ("TenGigabitEthernet (10 Gbps / 10000 Mbps)", 10000),
        ("Ethernet (10 Mbps)", 10),
    ]
    intf_name, intf_speed = random.choice(interfaces)

    # OSPF Cost formula: ceil(ref_bw / if_bw) with min cost of 1
    raw_cost = ref_mbps / intf_speed
    cost = max(1, int(raw_cost))

    display = (
        f"OSPF Cost Metric Calculation:\n"
        f"  • Interface Type: {intf_name}\n"
        f"  • Reference Bandwidth: {ref_mbps} Mbps "
        f"({'Default (10^8 bps)' if ref_mbps == 100 else 'auto-cost reference-bandwidth 1000'})\n"
        f"  • Formula: Cost = Reference Bandwidth / Interface Bandwidth"
    )

    return {
        "cat": "OSPF COST & METRIC CALCULATION",
        "display": display,
        "prompt": "What is the resulting OSPF interface cost (metric)?",
        "expected": str(cost),
        "aliases": [str(cost)],
        "hint": (
            f"Cost = {ref_mbps} / {intf_speed} = {raw_cost}. Costs are integer"
            " values with a minimum of 1."
        ),
    }

  def gen_state_drill(self):
    scenarios = [
        {
            "problem": (
                "R1 and R2 are connected. 'show ip ospf neighbor' shows R2"
                " stuck in '2-WAY/DROTHER'."
            ),
            "cause": "Normal behavior on a multi-access network between two DROTHERs",
            "aliases": [
                "normal",
                "drother",
                "normal behavior",
                "expected",
                "both drother",
            ],
            "hint": (
                "On broadcast segments, DROTHERs only form FULL adjacencies"
                " with DR and BDR. Between each other, 2-WAY is normal!"
            ),
        },
        {
            "problem": (
                "Two routers are directly connected via GigabitEthernet0/0.\n"
                "R1 has MTU 1500; R2 has MTU 9000 (Jumbo frames enabled).\n"
                "In which OSPF neighbor state will they get stuck?"
            ),
            "cause": "EXSTART",
            "aliases": ["exstart", "exstart/exchange", "exchange"],
            "hint": (
                "MTU mismatches get stuck in EXSTART because DBD (Database"
                " Description) packets are dropped."
            ),
        },
        {
            "problem": (
                "R1 sends Hellos, but R2's Hello packet lists Hello interval 10s"
                " and Dead interval 40s,\n"
                "while R1 is configured with Hello 5s and Dead 20s.\n"
                "Will they form an adjacency? (yes/no)"
            ),
            "cause": "no",
            "aliases": ["no", "n"],
            "hint": (
                "Hello and Dead timers must match exactly on both ends to form"
                " an adjacency."
            ),
        },
    ]
    pick = random.choice(scenarios)
    return {
        "cat": "OSPF ADJACENCY TROUBLESHOOTING",
        "display": pick["problem"],
        "prompt": "Enter the state or answer:",
        "expected": pick["cause"],
        "aliases": pick["aliases"],
        "hint": pick["hint"],
    }

  def generate_new_drill(self):
    self.is_waiting_for_next = False
    self.action_btn.config(text="Submit ↵", bg=ACCENT_CYAN)

    generators = [
        self.gen_rid_drill,
        self.gen_dr_bdr_drill,
        self.gen_cost_drill,
        self.gen_state_drill,
    ]
    self.current_scenario = random.choice(generators)()

    self.category_lbl.config(text=f"CATEGORY: {self.current_scenario['cat']}")
    self.scenario_text.config(text=self.current_scenario["display"])
    self.prompt_lbl.config(text=self.current_scenario["prompt"])

    self.entry_var.set("")
    self.answer_entry.config(state=tk.NORMAL)
    self.answer_entry.focus_set()
    self.status_lbl.config(text="Awaiting response...", fg="#8b8b9e")
    self.expected_lbl.config(text="")
    self.hint_lbl.config(text="")
    self.start_time = time.time()

  def check_answer(self):
    user_input = self.entry_var.get().strip().lower()
    if not user_input:
      return

    elapsed = round(time.time() - self.start_time, 2)
    self.total += 1

    valid_answers = [a.lower() for a in self.current_scenario["aliases"]]

    if user_input in valid_answers:
      self.score += 1
      self.status_lbl.config(text=f"✔ CORRECT! ({elapsed}s)", fg=ACCENT_GREEN)
      self.expected_lbl.config(
          text=f"Answer: {self.current_scenario['expected']}", fg=ACCENT_GREEN
      )
      self.hint_lbl.config(
          text="Press Enter or click 'Next ➔' to continue.", fg="#a0a0b2"
      )
      btn_color = ACCENT_GREEN
    else:
      self.status_lbl.config(text=f"✘ INCORRECT ({elapsed}s)", fg=ACCENT_RED)
      self.expected_lbl.config(
          text=(
              f"Expected: {self.current_scenario['expected']}  |  You entered:"
              f" {self.entry_var.get()}"
          ),
          fg=TEXT_COLOR,
      )
      self.hint_lbl.config(
          text=f"CCNA Concept: {self.current_scenario['hint']}",
          fg=ACCENT_YELLOW,
      )
      btn_color = "#3b3b4f"

    self.is_waiting_for_next = True
    self.action_btn.config(text="Next ➔", bg=btn_color)

    pct = round((self.score / self.total) * 100, 1)
    self.score_lbl.config(text=f"Score: {self.score}/{self.total} ({pct}%)")


if __name__ == "__main__":
  app = OSPFTrainerApp()
  app.mainloop()