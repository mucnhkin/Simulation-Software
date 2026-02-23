# --- Project Information ---
# Project: UUV Simulation Framework
# Version: 1.0.0
# Date: November 2025
#
# --- Authors and Contributors ---
# Primary:
# - Gunner Cook-Dumas (SCRUM Manager, Backend, Agent, Model, and GA Stucture)
# - Justin Mosman (developer)
# - Michael Cardinal (developer)
#
# Secondary:
# - Lauren Milne (SCRUM Product Owner)
#
# --- Reviewers/Bosses ---
# - Prof. Lance Fiondella, ECE, University of Massachusetts Dartmouth
# - Prof. Hang Dinh, CIS, Indiana University South Bend

import tkinter as tk

# Agent Menu, a more specialized menu sued for the agent section, holds the "add agent" button and
# the agent listbox, implemented this way because it allows for more complex implementations and methods
class AgentMenu(tk.Frame):
    def __init__(self, parent, size,color=None):
        super().__init__(parent, width=size[0], height=size[1], bg=color, border=5,bd=2, relief='solid')
        self.pack(side='top', padx=5, pady=5)
        self.pack_propagate(False)

        # Title Label
        self.title = tk.Label(self, text="Agent Selection", font=("Arial", 13, "bold"))
        self.title.pack(side='top', pady=(0, 2))

        # Separator bar (like GeneralFrames)
        self.file_bar = tk.Frame(self, bg="black", height=2)
        self.file_bar.pack(side="top", fill="x", pady=(0, 8))

        #Agent Button
        self.agent_menu_button = tk.Button(self, text="+ Add Agent", command=lambda: self.create_popup(1), bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.agent_menu_button.pack(side='top',anchor='nw', pady=(0, 5))

        # Scrollbar, Listbox, and label setup
        self.agent_display_data = {}  # {(name, type): count}
        name_width = 10
        type_width = 8
        count_width = 4
        label_text = f"{'Name:':<{name_width}} {'Type:':<{type_width}} {'Count:':>{count_width}}"
        self.scrollbar_label = tk.Label(self, text=label_text, font=("Consolas", 12))
        self.scrollbar_label.pack(side='top', fill='y', anchor='nw', padx=(5,0), pady=(5,0))

        self.scrollbar = tk.Scrollbar(self)
        self.agent_listbox = tk.Listbox(self, font=("Consolas", 11), width=30, height=8)
        self.scrollbar.config(command=self.agent_listbox.yview)
        self.agent_listbox.config(yscrollcommand=self.scrollbar.set)
        self.agent_listbox.pack(side='left', fill='y', padx=(0, 2))
        self.scrollbar.pack(side='right', fill='y')

        #Scroll Bar Double click functionality
        self.agent_listbox_keys = [] #map listbox indices to keys for easier parsing
        self.agent_listbox.bind('<Double-3>',self._on_listbox_rdouble_click)
        self.agent_listbox.bind('<Double-1>',self._on_listbox_double_click)

        # Store reference to parent for callbacks
        self.parent = parent

    def create_popup(self,choice):
        # Call parent's popup creation method
        self.parent.create_popup(choice)

    # Method to update the agent listbox when new agents are spawned or removed
    def update_agent_listbox(self):
        """Refresh the agent Listbox with current agent data."""
        self.agent_listbox.delete(0, tk.END)
        self.agent_listbox_keys = []
        # Set fixed widths for each column
        name_width = 12
        type_width = 10
        count_width = 4
        for (name, agent_type), count in self.agent_display_data.items():
            # Format each entry with fixed width columns
            entry = f"{name:<{name_width}} {agent_type:<{type_width}} {count:>{count_width}}"
            self.agent_listbox.insert(tk.END, entry)
            self.agent_listbox_keys.append((name, agent_type))

    # Method to add an agent to the display dictonary, then calls the update listbox method to display it
    # within the listbox
    def add_agent_to_display(self, name, agent_type):
        """Add or update agent in the display dictionary."""
        key = (name, agent_type)
        if key in self.agent_display_data:
            self.agent_display_data[key] += 1
        else:
            self.agent_display_data[key] = 1
        self.update_agent_listbox()

    # Currently unused method that will be used later
    def _on_listbox_double_click(self, event):
        """Left button double click handler. Used to wipe selected agent via listbox"""
        try:
            idx = self.agent_listbox.nearest(event.y)
        except Exception:
            idx = None
        if idx is None:
            return
        # Ensure the index is valid
        if idx < 0 or idx >= len(self.agent_listbox_keys):
            return
        self.agent_listbox.selection_clear(0, tk.END)
        self.agent_listbox.selection_set(idx)
        name, agent_type = self.agent_listbox_keys[idx]

    # Method called when listbox entry is double right clicked, opens the agent detail popup
    # (a window that displays the selected agents positions), via the method  self._open_agent_detail_popup
    def _on_listbox_rdouble_click(self, event):
        """Right-button double-click handler. Determine clicked index from event and open popup."""
        try:
            idx = self.agent_listbox.nearest(event.y)
        except Exception:
            idx = None
        if idx is None:
            return
        # Ensure the index is valid
        if idx < 0 or idx >= len(self.agent_listbox_keys):
            return
        # Make the clicked item the active/selected one (so UI shows selection)
        self.agent_listbox.selection_clear(0, tk.END)
        self.agent_listbox.selection_set(idx)
        name, agent_type = self.agent_listbox_keys[idx]
        count = self.agent_display_data.get((name, agent_type), 0)
        self._open_agent_detail_popup(name, agent_type, count)

    # Method used to open the agent detail popup, called by the double right click handler function
    def _open_agent_detail_popup(self, name, agent_type, count):
        """Opens a popup window showing agent details (positions)."""
        popup = tk.Toplevel(self)
        popup.transient(self)
        popup.title(f"Agent Details")
        popup.resizable(False, False)
        popup.attributes('-topmost', True)

        header = tk.Label(popup, text=f"{name} — {agent_type.title()} (count: {count})", font=("Consolas", 12, "bold"))
        header.pack(fill='x', padx=8, pady=(8,4))

        frame = tk.Frame(popup)
        frame.pack(fill='both', expand=True, padx=8, pady=(0,8))

        positions = self._get_positions_from_spawn_data(name, agent_type)
        if not positions:
            msg = tk.Label(frame, text="No positions found.", font=("Consolas", 11))
            msg.pack(anchor='w')
        else:
            for i, pos in enumerate(positions, start=1):
                pos_label = tk.Label(frame, text=f"{i}. {pos}", font=("Consolas", 11), anchor='w', justify='left')
                pos_label.pack(anchor='w')
        btn = tk.Button(popup, text="Close", command=popup.destroy, bg="#333333", fg="white", width=10, height=1, font=("Consolas", 12), relief="raised")
        btn.pack(pady=(0,8), padx=(0,8), anchor="se")

    # Helper function used by the agent detail popup window, grabs all the position data of a
    # selected agent from the listbox, specifically all agents with the same name and type
    def _get_positions_from_spawn_data(self, name, agent_type):
        positions = []
        spawn_dict = getattr(self.parent, "spawn_data", {})
        key_type = agent_type
        for t, spawn_list in spawn_dict.items():
            if str(t).lower() != str(key_type).lower():
                continue
            for spawn in spawn_list:
                spawn_name = spawn.get("name") or ""
                if spawn_name == name:
                    positions.append(spawn.get("pos"))
        return positions
