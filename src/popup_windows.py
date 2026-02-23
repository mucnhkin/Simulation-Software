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
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from agents import model

# Analysis Window class, this window is used by the analysis button to call the open_popup() method
# and then open this window, this is its own class because it's functionality and implementation will
# be tailored specifically for analysis of the sim, which will require many self contained methods
class AnalysisWindow(tk.Toplevel):
    """Analysis popup window"""
    def __init__(self, parent, title, size, canvas):
        super().__init__(parent)
        #Initialize window
        self.parent = parent
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-topmost', True)
        self.resizable(False,False)
        self.canvas = canvas
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Create a bordered container for the notebook so it has the same solid outline as GeneralFrames
        notebook_container = tk.Frame(self, bd=2, relief='solid', bg='black')
        notebook_container.pack(side='right', fill='both', expand=True, padx=(4,8), pady=8)
        notebook_container.pack_propagate(False)  # keep border/size stable

        # Add the small black top bar inside the container to match GeneralFrames' file_bar
        file_bar = tk.Frame(notebook_container, bg='black', height=4)
        file_bar.pack(side='top', fill='x')

        # Create a child frame inside the container to hold the Notebook itself (keeps the black border visible)
        notebook_inner = tk.Frame(notebook_container, bg=self.cget('bg'))
        notebook_inner.pack(fill='both', expand=True, padx=2, pady=(4,2))

        # Style the notebook tabs
        style = ttk.Style(self)
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        # Configure a custom style for this notebook and its tabs
        style_name = 'Analysis.TNotebook'
        tab_style = 'Analysis.TNotebook.Tab'
        style.configure(style_name,
                        background='#1c1c1c',     # notebook background
                        borderwidth=0)
        style.configure(tab_style,
                        background='#222222',     # tab background (unselected)
                        foreground='white',
                        padding=(10, 6),
                        font=('Arial', 10, 'bold'))
        # Set color for selected/active states
        style.map(tab_style,
                background=[('selected', '#000000'), ('active', '#333333')],
                foreground=[('selected', 'white')])

        #Set up left hand "Scenario Selection" menu
        notebook_body = '#DCDAD5'  # same color used for notebook body

        # Outer black container so we get a solid black outline like GeneralFrames
        scenario_container = tk.Frame(self, bg='black', width=200, height=size[1])
        scenario_container.pack(side='left', padx=(8,4), pady=8)
        scenario_container.pack_propagate(False)

        # Inner panel that holds the actual content and uses the notebook body color
        self.scenario_select = tk.Frame(scenario_container, bg=notebook_body, width=194, height=size[1] - 20)
        self.scenario_select.pack(padx=2, pady=4, fill='y')
        self.scenario_select.pack_propagate(False)

        # Title and small black top bar (matches GeneralFrames)
        title = tk.Label(self.scenario_select, text="Scenario Selection", font=("Arial", 13, "bold"),
                         bg=notebook_body, fg='black')
        title.pack(side='top', pady=(8, 2))
        file_bar2 = tk.Frame(self.scenario_select, bg='black', height=2)
        file_bar2.pack(side='top', fill='x', pady=(0, 8))

        # Load Scenario button
        self.load_scenario_button = tk.Button(self.scenario_select, text="Load Scenario", 
                                              bg="#333333", fg="white", width=15, height=1, 
                                              font=("Arial", 11), relief="raised", 
                                              command=self.load_scenario_dialog)
        self.load_scenario_button.pack(side='top', pady=(8, 8))

        # Create the Notebook with the custom style and pack it inside the inner frame
        self.notebook = ttk.Notebook(notebook_inner, style=style_name)
        self.notebook.pack(fill='both', expand=True)

        # --- Tab frames ---
        self.tab_overview = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_overview, text='Overview')

    # Load scenario dialog - identical functionality to load config button on main screen
    def load_scenario_dialog(self):
        """Load a scenario configuration file"""
        file_path = fd.askopenfilename(title="Load scenario config", 
                                      defaultextension=".json", 
                                      filetypes=[("JSON", "*.json")])
        if not file_path:
            return

        validator = self.parent.make_grid_validator()
        cm = self.parent.config_manager
        try:
            spawns, warnings, meta = cm.load(file_path, validate_fn=validator, remove_invalid=True)
        except Exception as e:
            mb.showerror("Load error", f"Failed to load config: {e}")
            return

        # present warnings and proceed
        if warnings:
            proceed = mb.askyesno("Load warnings", "Some entries were invalid or changed:\n\n" + "\n".join(warnings) + "\n\nProceed and import valid entries?")
            if not proceed:
                return

        applied = self.parent.apply_loaded_spawns(spawns, wipe_existing=True)
        if applied:
            mb.showinfo("Load complete", "Configuration applied to map.")
        else:
            mb.showinfo("Load cancelled", "Configuration was not applied.")

    # Helper close window function
    def close_window(self):
      self.parent.popup_window = None
      self.destroy()

# Window that appears when doubleclicking an agent on the map used for setting
# variables such as target and cost
class AgentInfoWindow(tk.Toplevel):
    """ Window that appears when doubleclicking an agent on the map
        used for setting variables such as target and cost"""
    def __init__(self, parent, title, size, canvas):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-topmost', True)
        self.resizable(False, False)
        self.canvas = canvas
        self.protocol("WM_DELETE_WINDOW", self.close_popup)

    def close_popup(self):
        '''Close the popup'''
        self.parent.popup_window = None
        self.destroy()


# UAV Select Window, window that pops up when adding agents (via open_popup() method), implemented
# as its own class for easier implementation of specific functionality
class UAVSelectWindow(tk.Toplevel):
    '''UAV selecting popup window'''
    # Keep in the mind the grid pos and the way agents navigate is flipped
    def __init__(self, parent, title, size, canvas):
        super().__init__(parent)
        # setup the window
        self.parent = parent
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.attributes('-topmost', True)
        self.resizable(False, False)
        self.canvas = canvas
        self.protocol("WM_DELETE_WINDOW", self.close_popup)

        # gather agent data
        # dont change this unless you tell me
        # or have good reason
        self.agent_type_attacker = model.UUVModel.AGENT_CATEGORIES['attacker']
        _exclude = {"cuuv"}
        self.agent_type_defender = [
            t for t in model.UUVModel.AGENT_CATEGORIES.get("defender", [])
            if t.lower() not in _exclude
            ]

        # Setup button controles
        self.mode_var = tk.StringVar(self)
        self.mode_var.set("Attacker")
        self.name_label = tk.Label(self, text="Name:", font=("Arial", 11))
        self.name_label.pack(anchor="w", padx=20, pady=(20, 2))
        self.name_entry = tk.Entry(self, font=("Arial", 11), width=25)
        self.name_entry.pack(anchor="w", padx=20, pady=(0, 10))
        self.type_label = tk.Label(self, text="Type:", font=("Arial", 11))
        self.type_label.pack(anchor="w", padx=20, pady=(0, 2))
        self.type_row = tk.Frame(self)
        self.type_row.pack(anchor="w", padx=20, pady=(0, 10), fill="x")
        self.selected_agent_type = tk.StringVar(self)
        self.type_dropdown = tk.OptionMenu(self.type_row, self.selected_agent_type, "Seeker")
        self.type_dropdown.config(font=("Arial", 11), width=18)
        self.type_dropdown.pack(side="left")

        self.btn_left = tk.Frame(self)
        self.btn_left.pack(side="left", anchor="sw", padx=20, pady=15)
        self.btn_right = tk.Frame(self)
        self.btn_right.pack(side="right", anchor="se", padx=20, pady=15)
        self.spawn_btn = tk.Button(self.btn_left,text="Spawn",bg="#333333",fg="white",width=12,height=1,font=("Arial", 12),relief="raised",command=self.start_spawning)
        self.spawn_btn.pack(fill="x")
        self.stop_btn = tk.Button(self.btn_left,text="Stop Spawning",bg="#333333",fg="white",width=12,height=1,font=("Arial", 12),relief="raised",command=self.stop_spawning,state="disabled")
        self.stop_btn.pack(fill="x", pady=(8, 0))
        self.close_btn = tk.Button(self.btn_right,text="Close",bg="#333333",fg="white",width=10,height=1,font=("Arial", 12),relief="raised",command=self.close_popup)
        self.close_btn.pack(anchor="e")

        self.toggle_btn = tk.Button(self.type_row, textvariable=self.mode_var, font=("Arial", 12), width=10, relief="raised", command=self.toggle_mode)
        self.toggle_btn.pack(side="left", padx=(12, 0), pady=(0, 2))

        # Spawing varibles
        self.current_target_pos = None


        #Set agent menu reference
        self.agent_menu = self.parent.agent_menu

        # run an update
        self.update_dropdown()
        self.spawning_state = tk.BooleanVar(self)
        self.spawning_state.set(False)

    # Method to update the dropdown dynamically
    def update_dropdown(self):
        '''Update the dropdown menu'''
        self.menu = self.type_dropdown["menu"]
        self.menu.delete(0, "end")
        if self.mode_var.get() == "Attacker":
            self.options = self.agent_type_attacker
        else:
            self.options = self.agent_type_defender

        for opt in self.options:
            self.menu.add_command(label=opt, command=lambda value=opt: self.selected_agent_type.set(value))

        if self.mode_var.get() == "Attacker":
            self.toggle_btn.config(bg="#8B0000", fg="white")
        else:
            self.toggle_btn.config(bg="#00008B", fg="white")

        self.selected_agent_type.set(self.options[0])

    # Method to toggle the attacker / defender button, then calls update dropdown to set accordingly
    def toggle_mode(self):
        '''Toggle between the Attacker and Defender UAVs'''
        if self.mode_var.get() == "Attacker":
            self.mode_var.set("Defender")
        else:
            self.mode_var.set("Attacker")
        self.update_dropdown()

    # Function used to enable / disable spawning, functionality tied to the
    # "spawn" button
    def start_spawning(self):
        '''Enable spawning'''
        self.spawning_state.set(True)
        self.spawn_btn.config(text="Spawning", state="disabled")
        self.stop_btn.config(state="normal")
        # Only allow spawning of the selected type from the dropdown
        self.canvas.bind("<Button-1>", self.place_agent, add='+')
        self.parent.can_spawn = True

    # Method to actually place agents on the canvas and store their data
    def place_agent(self, event):
        '''Place agents on the canvas and store instructions'''
        # Checks if we are not in the spawning state, if not, we cant spawn
        if not self.spawning_state.get():
            print("NOT IN SPAWNING STATE-debug")
            return
        # Snap our cursor to the grid first
        snap_x, snap_y, grid_x, grid_y = self.parent.snap_to_grid(event.x, event.y)

        # Check if inside map (basic canvas check)
        if self.parent.is_inside_map(event.x, event.y) is False:
            print("DEBUG- ADD CHECK TO DETERMINE IF CAN SPAWN ON LAND FOR CERTAIN AGENTS")
            return

        # Check the actual grid cell — the grid uses 5-point majority voting,
        # so this is the authoritative land/water classification
        if self.parent.map_grid is not None:
            try:
                cell = self.parent.map_grid.grid[grid_y][grid_x]
                if cell.id == 1:  # 1 = land, 0 = water
                    print(f"Cannot spawn on land cell ({grid_x}, {grid_y})")
                    return
            except IndexError:
                print(f"Spawn position ({grid_x}, {grid_y}) out of grid bounds")
                return
        grid_pos = (grid_x, grid_y)

        # Grab the agent type from the selected agent type (from the dropdown)
        agent_type = self.selected_agent_type.get()

        #Obtain the agent name from the selcted entry name (what was entered in the type field)
        # if no name was provided, default to the agent type i.e "seeker", "detector", etc.
        agent_name = self.name_entry.get() if self.name_entry.get() else agent_type

        #Obtain colors for agent from parent (which are initialized in the App(parent) init)
        parent_colors = getattr(self.parent, "_agent_type_colors_norm", {})
        # Try and obtain the color associated with the agent, if there is none, default to green
        color_for_type = parent_colors.get(str(agent_type).lower(), "green")

        # Setup our new agents data, this is a dict that holds various data for our agents and is
        # used by our ConfigManager when loading and saving .jsons, the "type" and "pos" are important
        # data points, the rest are considered optional metadata
        new_agent_data = {
            'type': agent_type,
            'pos': grid_pos,
            'name': agent_name,
            'color': color_for_type
            }

        if agent_type in self.parent.spawn_data:
            # if this agent type is valid, append the agents data to the parents parents spawn
            # data at the agent_type index
            self.parent.spawn_data[agent_type].append(new_agent_data)
            # Update the agent display when a new agent is added
            self.agent_menu.add_agent_to_display(agent_name, agent_type)
        else:
            print(f"ERROR: placed unknown agent type {agent_type}")
            return

        # Set up a market id to be stored by each new agent, this will be unique to each placed agent
        # and will serve as a good way to distinguish agents in the future
        marker_id = self.parent.draw_spawn_marker(snap_x, snap_y, color_for_type, agent_type)
        # Add this marker id to the new agent data dict, will be taken as optional metadata in the .json
        new_agent_data['marker_id'] = marker_id


        # If this is a detector, draw its detection radius ring immediately so user sees it when placed.
        if str(agent_type).lower() == "detector":
         new_agent_data['radius_id'] = self.parent.draw_detector_radius(snap_x, snap_y, radius=20, marker_id=marker_id)

    # Function to disbale the spawning state
    def stop_spawning(self):
        '''disable spawning'''
        self.spawning_state.set(False)
        self.spawn_btn.config(text="Spawn", state="normal")
        self.stop_btn.config(state="disabled")
        # self.canvas.unbind("<Button-1>")
        self.parent.can_spawn = False

    # Method to close the popup
    def close_popup(self):
        '''Close the popup with rules'''
        self.stop_spawning()
        self.parent.popup_window = None
        self.destroy()
