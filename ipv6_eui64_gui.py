#!/usr/bin/env python3
"""
CCNA IPv6 Addressing & Modified EUI-64 Workshop GUI
Drills IPv6 compression rules, EUI-64 MAC conversions, and special address scopes.
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
ACCENT_MAGENTA = "#c678dd"
FONT_FAMILY = "Segoe UI"


class IPv6WorkshopApp(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title("CCNA IPv6 & Modified EUI-64 Workshop")
    self.geometry("820x750")
    self.minsize(740, 680)
    self.configure(bg=BG_DARK)

    self.score = 0
    self.total = 0
    self.start_time = 0
    self.current_scenario = None
    self.is_waiting_for_next = False

    self.build_ui()
    self.generate_new_scenario()

  def build_ui(self):
    header = tk.Frame(self, bg=BG_DARK, pady=12)
    header.pack(fill=tk.X, padx=20)

    title_lbl = tk.Label(
        header,
        text="🌐 CCNA IPv6 & EUI-64 WORKSHOP",
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

    # Challenge Card
    self.card = tk.Frame(
        self,
        bg=BG_CARD,
        padx=18,
        pady=16,
        highlightbackground="#3d3d4d",
        highlightthickness=1,
    )
    self.card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))

    self.mode_lbl = tk.Label(
        self.card,
        text="CATEGORY: EUI-64 CALCULATION",
        font=(FONT_FAMILY, 9, "bold"),
        fg="#8b8b9e",
        bg=BG_CARD,
    )
    self.mode_lbl.pack(anchor=tk.W)

    self.scenario_text = tk.Label(
        self.card,
        text="Loading challenge...",
        font=("Consolas", 11),
        fg=ACCENT_YELLOW,
        bg="#181820",
        justify=tk.LEFT,
        padx=14,
        pady=12,
    )
    self.scenario_text.pack(fill=tk.BOTH, expand=True, pady=10)

    # Input Section
    input_box = tk.Frame(self, bg=BG_DARK, pady=8)
    input_box.pack(fill=tk.X, padx=20)

    self.prompt_lbl = tk.Label(
        input_box,
        text="Enter calculated value:",
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

    # Diagnostic / Feedback
    self.feedback_box = tk.Frame(
        self,
        bg="#22222b",
        padx=14,
        pady=12,
        highlightbackground="#3d3d4d",
        highlightthickness=1,
    )
    self.feedback_box.pack(fill=tk.X, padx=20, pady=(5, 14))

    self.status_lbl = tk.Label(
        self.feedback_box,
        text="Awaiting response...",
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
        wraplength=760,
        justify=tk.LEFT,
    )
    self.hint_lbl.pack(anchor=tk.W)

    # Bottom Skip row
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
        command=self.generate_new_scenario,
    )
    self.skip_btn.pack(side=tk.RIGHT)

  def handle_action(self):
    if self.is_waiting_for_next:
      self.generate_new_scenario()
    else:
      self.check_answer()

  # --- Drill Generators ---
  def gen_eui64_drill(self):
    # Generates a random MAC and calculates Modified EUI-64 Interface ID
    first_byte = random.choice([0x00, 0x02, 0x08, 0x12, 0x34, 0xAA, 0xBC])
    b2, b3, b4, b5, b6 = [random.randint(0, 255) for _ in range(5)]

    mac_hex = f"{first_byte:02x}:{b2:02x}:{b3:02x}:{b4:02x}:{b5:02x}:{b6:02x}"
    cisco_mac = f"{first_byte:02x}{b2:02x}.{b3:02x}{b4:02x}.{b5:02x}{b6:02x}"

    # Flip 7th bit (XOR with 0x02 on first byte)
    modified_b1 = first_byte ^ 0x02

    # Insert FFFE in middle: (b1, b2, b3) + (FF, FE) + (b4, b5, b6)
    # Form 4 hextets:
    h1 = f"{modified_b1:02x}{b2:02x}"
    h2 = f"{b3:02x}ff"
    h3 = f"fe{b4:02x}"
    h4 = f"{b5:02x}{b6:02x}"

    eui64_iid = f"{h1}:{h2}:{h3}:{h4}"

    display = (
        f"Modified EUI-64 Conversion Challenge:\n"
        f"  • Interface Hardware MAC: {cisco_mac} (Standard format: {mac_hex})\n"
        f"  • Task: Calculate the 64-bit Interface Identifier (IID).\n\n"
        f"Steps Reminder:\n"
        f"  1. Split the 48-bit MAC in half (24 bits each).\n"
        f"  2. Insert 16-bit hex 'ff:fe' directly in the middle.\n"
        f"  3. Invert the 7th bit (Universal/Local) of the first byte."
    )

    return {
        "cat": "MODIFIED EUI-64 INTERFACE ID",
        "display": display,
        "prompt": "Enter the 64-bit EUI-64 Interface ID (e.g., xxxx:xxff:fexx:xxxx):",
        "expected": eui64_iid,
        "aliases": [
            eui64_iid,
            eui64_iid.lower(),
            eui64_iid.replace(":", ""),
            eui64_iid.replace(":", "."),
        ],
        "hint": (
            f"First byte {first_byte:02x} in binary has bit 7 flipped to"
            f" {modified_b1:02x}. With FFFE inserted, the 64-bit ID is"
            f" {eui64_iid}."
        ),
    }

  def gen_compression_drill(self):
    full_blocks = [
        "2001:0db8:0000:0000:0000:0000:1428:57ab",
        "fe80:0000:0000:0000:02a0:c9ff:feab:12cd",
        "2001:0db8:0001:0000:0000:0ab0:0000:0012",
        "fd00:0000:0000:0001:0000:0000:0000:0001",
    ]
    raw_ip = random.choice(full_blocks)
    standard_compressed = str(ipaddress.IPv6Address(raw_ip))

    display = (
        f"RFC 5952 IPv6 Compression Drill:\n"
        f"  • Uncompressed 128-bit Address: {raw_ip}\n"
        f"  • Apply strict RFC 5952 rules:\n"
        f"      1. Omit all leading zeros in each 16-bit hextet.\n"
        f"      2. Replace the single longest contiguous run of consecutive zero hextets with '::'.\n"
        f"      3. If zero runs are equal in length, collapse the leftmost one."
    )

    return {
        "cat": "RFC 5952 ADDRESS COMPRESSION",
        "display": display,
        "prompt": "Enter the fully compressed IPv6 address format:",
        "expected": standard_compressed,
        "aliases": [standard_compressed, standard_compressed.lower()],
        "hint": (
            f"Leading zeroes drop first, and the longest contiguous zero hextet"
            f" block becomes '::'. Result: {standard_compressed}"
        ),
    }

  def gen_scope_drill(self):
    scenarios = [
        {
            "q": (
                "What is the IPv6 link-local prefix and prefix length"
                " assigned automatically to every IPv6 interface?"
            ),
            "expected": "fe80::/10",
            "aliases": ["fe80::/10", "fe80::"],
            "hint": (
                "Link-Local addresses always fall within the fe80::/10 block"
                " (FE80 through FEBF)."
            ),
        },
        {
            "q": (
                "What is the IPv6 all-nodes multicast address (equivalent to"
                " IPv4 255.255.255.255 on a local link)?"
            ),
            "expected": "ff02::1",
            "aliases": ["ff02::1"],
            "hint": "ff02::1 targets all IPv6 hosts on the local link segment.",
        },
        {
            "q": (
                "What is the IPv6 all-routers multicast address listened to by"
                " all active routing interfaces?"
            ),
            "expected": "ff02::2",
            "aliases": ["ff02::2"],
            "hint": (
                "ff02::2 targets all IPv6 routers on the link (hosts send"
                " Router Solicitations here)."
            ),
        },
        {
            "q": (
                "Which IPv6 multicast address is used by OSPFv3 to reach all"
                " OSPF routers (AllSPFRouters)?"
            ),
            "expected": "ff02::5",
            "aliases": ["ff02::5"],
            "hint": (
                "OSPFv2 uses 224.0.0.5; OSPFv3 uses link-local multicast"
                " ff02::5."
            ),
        },
        {
            "q": (
                "What is the standard Unique Local Address (ULA) prefix"
                " reserved for private IPv6 routing?"
            ),
            "expected": "fc00::/7",
            "aliases": ["fc00::/7", "fd00::/8", "fc00::", "fd00::"],
            "hint": (
                "Unique Local addresses use the fc00::/7 prefix (with fd00::/8"
                " commonly assigned with locally generated global IDs)."
            ),
        },
    ]
    pick = random.choice(scenarios)
    return {
        "cat": "SPECIAL IPv6 SCOPES & MULTICAST IDENTIFICATION",
        "display": f"Address Scope Challenge:\n  {pick['q']}",
        "prompt": "Enter the exact IPv6 address or prefix:",
        "expected": pick["expected"],
        "aliases": pick["aliases"],
        "hint": pick["hint"],
    }

  def generate_new_scenario(self):
    generators = [
        self.gen_eui64_drill,
        self.gen_compression_drill,
        self.gen_scope_drill,
    ]
    self.current_scenario = random.choice(generators)()
    self.is_waiting_for_next = False
    self.action_btn.config(text="Submit ↵", bg=ACCENT_CYAN)

    self.mode_lbl.config(text=f"CATEGORY: {self.current_scenario['cat']}")
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

    clean_aliases = [a.lower().strip() for a in self.current_scenario["aliases"]]

    if user_input in clean_aliases:
      self.score += 1
      self.status_lbl.config(text=f"✔ CORRECT! ({elapsed}s)", fg=ACCENT_GREEN)
      self.expected_lbl.config(
          text=f"Value: {self.current_scenario['expected']}", fg=ACCENT_GREEN
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
          text=f"Review Hint: {self.current_scenario['hint']}",
          fg=ACCENT_YELLOW,
      )
      btn_color = "#3b3b4f"

    self.is_waiting_for_next = True
    self.action_btn.config(text="Next ➔", bg=btn_color)

    pct = round((self.score / self.total) * 100, 1)
    self.score_lbl.config(text=f"Score: {self.score}/{self.total} ({pct}%)")


if __name__ == "__main__":
  app = IPv6WorkshopApp()
  app.mainloop()