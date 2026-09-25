#!/usr/bin/env python3
"""
CCNA Network Revision Toolkit - Master Dashboard Launcher
Central command hub to launch and manage all CCNA study modules.
Requires Python 3 standard library only (tkinter + subprocess).
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

# --- Dark Terminal Styling ---
BG_DARK = "#16161c"
BG_CARD = "#23232e"
BG_INNER = "#1b1b24"
TEXT_COLOR = "#f0f0f5"
TEXT_MUTED = "#8b8b9e"
ACCENT_CYAN = "#00d4ff"
ACCENT_GREEN = "#2ecc71"
ACCENT_YELLOW = "#f39c12"
FONT_FAMILY = "Segoe UI"


class MasterDashboardApp(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title("CCNA Network Revision Toolkit - Command Hub")
    self.geometry("860x780")
    self.minsize(800, 720)
    self.configure(bg=BG_DARK)

    # Resolve toolkit base directory
    self.base_dir = os.path.dirname(os.path.abspath(__file__))

    self.modules = [
        {
            "id": "subnet",
            "name": "Subnet Speed-Drill",
            "tag": "IPv4 & WILDCARDS",
            "desc": (
                "Rapid-fire CIDR math: Network ID, Broadcast, usable host"
                " ranges, and inverse wildcard masks."
            ),
            "script": "subnet_drill_gui.py",
            "color": ACCENT_CYAN,
        },
        {
            "id": "header",
            "name": "Frame & Header Inspector",
            "tag": "L2-L4 ENCAPSULATION",
            "desc": (
                "Visual ASCII layout & field quiz: Ethernet II, 802.1Q tags,"
                " IPv4/IPv6, and TCP 3-way handshakes."
            ),
            "script": "header_inspector_gui.py",
            "color": "#c678dd",
        },
        {
            "id": "ospf",
            "name": "OSPF & Metric Logic Trainer",
            "tag": "ROUTING PROTOCOLS",
            "desc": (
                "Router ID election hierarchy, DR/BDR priorities, cumulative"
                " path cost math, and neighbor state machine."
            ),
            "script": "ospf_trainer_gui.py",
            "color": ACCENT_YELLOW,
        },
        {
            "id": "bughunter",
            "name": "Cisco IOS Config Bug Hunter",
            "tag": "TROUBLESHOOTING",
            "desc": (
                "Simulated running-config inspection: locate native VLAN"
                " mismatches, bad wildcards, and passive peer links."
            ),
            "script": "ios_bug_hunter_gui.py",
            "color": "#e06c75",
        },
        {
            "id": "routesel",
            "name": "Route Selection & AD Duel",
            "tag": "ROUTING TABLE LOGIC",
            "desc": (
                "Master packet forwarding logic: Longest Prefix Match vs"
                " Administrative Distance vs Cost comparison."
            ),
            "script": "route_selection_gui.py",
            "color": "#61afef",
        },
        {
            "id": "ipv6",
            "name": "IPv6 & Modified EUI-64 Workshop",
            "tag": "NEXT-GEN ADDRESSING",
            "desc": (
                "RFC 5952 address compression, 48-to-64-bit MAC conversion"
                " (bit 7 inversion), and link-local multicast scopes."
            ),
            "script": "ipv6_eui64_gui.py",
            "color": ACCENT_GREEN,
        },
    ]

    self.build_ui()

  def build_ui(self):
    # Top Header Banner
    header = tk.Frame(self, bg=BG_DARK, pady=16)
    header.pack(fill=tk.X, padx=25)

    title_frame = tk.Frame(header, bg=BG_DARK)
    title_frame.pack(side=tk.LEFT)

    tk.Label(
        title_frame,
        text="⚡ CCNA NETWORK TOOLKIT",
        font=(FONT_FAMILY, 17, "bold"),
        fg=ACCENT_CYAN,
        bg=BG_DARK,
    ).pack(anchor=tk.W)

    tk.Label(
        title_frame,
        text=(
            "Modular desktop drills for Cisco 200-301 certification revision"
        ),
        font=(FONT_FAMILY, 9),
        fg=TEXT_MUTED,
        bg=BG_DARK,
    ).pack(anchor=tk.W, pady=(2, 0))

    env_lbl = tk.Label(
        header,
        text=f"Python {sys.version_info.major}.{sys.version_info.minor} | Standard Library",
        font=("Consolas", 9),
        fg=TEXT_MUTED,
        bg=BG_DARK,
    )
    env_lbl.pack(side=tk.RIGHT, pady=6)

    # Scrollable / Container Body
    body_frame = tk.Frame(self, bg=BG_DARK)
    body_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 15))

    # Grid of Modules (2 Columns x 3 Rows)
    for index, mod in enumerate(self.modules):
      row = index // 2
      col = index % 2

      # Check script presence
      script_path = os.path.join(self.base_dir, mod["script"])
      is_available = os.path.isfile(script_path)

      card = tk.Frame(
          body_frame,
          bg=BG_CARD,
          bd=0,
          padx=16,
          pady=14,
          highlightbackground="#353545",
          highlightthickness=1,
      )
      card.grid(
          row=row,
          column=col,
          sticky="nsew",
          padx=8 if col == 1 else (0, 8),
          pady=8,
      )
      body_frame.grid_columnconfigure(col, weight=1)
      body_frame.grid_rowconfigure(row, weight=1)

      # Card Header
      top_meta = tk.Frame(card, bg=BG_CARD)
      top_meta.pack(fill=tk.X)

      tk.Label(
          top_meta,
          text=f"MODULE 0{index + 1}",
          font=("Consolas", 8, "bold"),
          fg=mod["color"],
          bg=BG_CARD,
      ).pack(side=tk.LEFT)

      status_text = "READY" if is_available else "MISSING"
      status_color = ACCENT_GREEN if is_available else "#e74c3c"
      tk.Label(
          top_meta,
          text=status_text,
          font=("Consolas", 8, "bold"),
          fg=status_color,
          bg=BG_CARD,
      ).pack(side=tk.RIGHT)

      # Title
      tk.Label(
          card,
          text=mod["name"],
          font=(FONT_FAMILY, 12, "bold"),
          fg=TEXT_COLOR,
          bg=BG_CARD,
      ).pack(anchor=tk.W, pady=(6, 2))

      # Subtitle Tag
      tk.Label(
          card,
          text=f"[{mod['tag']}]",
          font=("Consolas", 8),
          fg=mod["color"],
          bg=BG_CARD,
      ).pack(anchor=tk.W, pady=(0, 6))

      # Description
      tk.Label(
          card,
          text=mod["desc"],
          font=(FONT_FAMILY, 9),
          fg="#a5a5b5",
          bg=BG_CARD,
          wraplength=330,
          justify=tk.LEFT,
      ).pack(anchor=tk.W, fill=tk.BOTH, expand=True)

      # Launch Button
      btn = tk.Button(
          card,
          text=f"Launch Module ➔",
          font=(FONT_FAMILY, 9, "bold"),
          bg="#2f3142" if is_available else "#1e1e24",
          fg=TEXT_COLOR if is_available else "#555566",
          activebackground=mod["color"],
          activeforeground="#16161c",
          relief=tk.FLAT,
          cursor="hand2" if is_available else "arrow",
          pady=5,
          command=lambda p=script_path, n=mod["name"]: self.launch_script(p, n),
      )
      btn.pack(fill=tk.X, pady=(10, 0))

    # Bottom Status Bar
    footer = tk.Frame(self, bg="#111116", padx=20, pady=10)
    footer.pack(fill=tk.X)

    tk.Label(
        footer,
        text=(
            "Tip: You can launch multiple modules simultaneously to practice"
            " different exam objectives."
        ),
        font=(FONT_FAMILY, 9),
        fg=TEXT_MUTED,
        bg="#111116",
    ).pack(side=tk.LEFT)

  def launch_script(self, script_path, tool_name):
    if not os.path.isfile(script_path):
      messagebox.showerror(
          "Script Not Found",
          f"Could not locate '{os.path.basename(script_path)}'.\nPlease verify"
          " the file exists in the repository folder.",
      )
      return

    try:
      # Spawn as a detached subprocess so launcher remains responsive
      subprocess.Popen([sys.executable, script_path], cwd=self.base_dir)
    except Exception as e:
      messagebox.showerror(
          "Launch Error", f"Failed to execute {tool_name}:\n{e}"
      )


if __name__ == "__main__":
  app = MasterDashboardApp()
  app.mainloop()