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
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import os
from PIL import Image
from PIL import ImageTk
from pathlib import Path

# Import project modules
from grid import Grid
from map import MapControl
from agents import model
from config import ConfigManager

# Import GUI components
from gui_frames import Menu, FileMenu, CanvasFrame, CanvasMap, GeneralFrames
from agent_menu import AgentMenu
from popup_windows import AnalysisWindow, AgentInfoWindow, UAVSelectWindow

UUV_path = os.path.join(os.getcwd(), "resources", "EnemyUUV.png")
Target_path = os.path.join(os.getcwd(), "resources", "Installation(Target).png")
Detector_path = os.path.join(os.getcwd(), "resources", "Detector.png")
#=========================================================================================================================
#=========================================================================================================================
#Main app class, this encompesses the entire GUI and essentially all front end functionality
class App(tk.Tk):
    def __init__(self, title, size, parent_dir):
    # Main App (parent) init setup, initalizes things like app dimensions, title, attributes like
    # self variables, menus, buttons, etc.
    #=====================================================================================================================
    #=====================================================================================================================
        super().__init__() #parent super init method that will be used by children classes to inherit init conditions
        self.app_height = size[1]
        self.app_width = size[0]
        self.title(title)
        self.geometry(f'{self.app_width}x{self.app_height}')
        self.resizable(False, False)

        # varibles
        self.map_file_path = None
        self.map_grid = None
        self.map_shallow_color = (170, 201, 250)
        self.map_deep_color = (0, 0, 26)
        self.canvas_size = (700, 700)
        self.is_running = False
        self.animation_job = None
        self.can_spawn = False
        # Make sure its devisible by 700 (bc 700x700 was used as canvas size)
        self.cell_count = 100

        # varibles for selection
        self.mouse_start_x = 0
        self.mouse_start_y = 0
        self.can_select = False
        self.step_interval = 20  # ms, default step interval

        # Handle spawn position data
        # dont change this unless you tell me
        # or have good reason
        self.all_agent_types = [
            agent_type
            for types_tuple in model.UUVModel.AGENT_CATEGORIES.values()
            for agent_type in types_tuple
        ]
        self.spawn_data = {
            agent_type : []
            for agent_type in self.all_agent_types
        }


        self.agent_images = []
        # normalized lookup (case-insensitive)
        self._agent_type_colors_norm = self._build_agent_colors_from_model()
        # Agent model
        self.mesa_model = None

        # logo
        self.logo_path = os.path.join(parent_dir, "resources", "umass_logo.ico")
        self.logo_image = Image.open(self.logo_path)
        self.logo_icon = ImageTk.PhotoImage(self.logo_image)
        self.iconphoto(False, self.logo_icon)

        # menus (Agent menu, File menu, etc.)
        self.menu = Menu(parent=self, size=(300, self.app_height),color='')
        self.file_menu = FileMenu(self, (self.app_width, 100), color='')
        self.agent_menu = AgentMenu(parent=self, size=(440, 200))
        self.canvas_frame = CanvasFrame(self, self.canvas_size)
        self.popup_window = None

        # Create ConfigManager instance for saving/loading
        # Put configs in a local configs folder by default
        self.config_manager = ConfigManager(default_dir="configs", allow_overwrite=False)

        # sub-menus(General Frames menus)
        self.file_section = GeneralFrames(parent=self.menu, size=(440, 90), side='top', text='Map Selection')
        self.agent_menu.pack(in_=self.menu, side='top', padx=5, pady=5)
        self.sim_options_section = GeneralFrames(parent=self.menu, size=(440, 150), side='top', text='Simulation Options')
        self.sub_sim_section = tk.Frame(self.sim_options_section)
        self.sub_sim_section.pack(expand=True)
        self.config_menu_section = GeneralFrames(parent=self.menu,size=(440,90),side='top',text="Config Options")
        self.sub_config_section = tk.Frame(self.config_menu_section)
        self.sub_config_section.pack(expand=True)

        #sub-menu buttons
        self.file_button = tk.Button(self.file_section, text="🌐 Select", command=self.select_file, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.start_button = tk.Button(self.sub_sim_section, text="▶ Start", command=self.on_start_click, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.reset_sim_button = tk.Button(self.sub_sim_section, text="🔄 Reset", command= lambda: self.reset_simulation(), bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.exit_sim_button = tk.Button(self.sub_sim_section, text="✕ Exit", command=self.destroy, bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.analysis_button = tk.Button(self.sub_sim_section, text="⛶ Analysis", command=lambda: self.create_popup(2), bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised")
        self.file_button.pack(side='top', pady=4)
        self.start_button.grid(row=0, column=0, padx=10, pady=5)
        self.reset_sim_button.grid(row=0, column=1, padx=10, pady=5)
        self.exit_sim_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.analysis_button.grid(row=1, column=1, padx=10, pady=5)
        self.save_button = tk.Button(self.sub_config_section, text="Save Config", bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised", command=self.save_config_dialog)
        self.load_button = tk.Button(self.sub_config_section, text="Load Config", bg="#333333", fg="white", width=10, height=1, font=("Arial", 12), relief="raised",  command=self.load_config_dialog)
        #Need to make an additional sub frame to stack the slider and the coord label correctly
        self.file_menu_left_frame = tk.Frame(self.file_menu)
        self.file_menu_left_frame.pack(side='left', fill='y', padx=10, pady=2)
        #Pack the coord label into the sub container frame
        self.coord_label = tk.Label(self.file_menu_left_frame, text="Grid Position: (x, y) | [lat, lon]", font=("Arial", 11), anchor="nw")
        self.coord_label.pack(side='top', anchor='nw')
        #Scale slider set up (also packed in sub frame)
        self.step_scale = tk.Scale(
            self.file_menu_left_frame,           # parent is now the left frame
            from_=20,
            to=800,
            orient='horizontal',
            label='Step (ms)',
            resolution=20,
            showvalue=True,
            length=250,
            command=self.set_step_interval
        )
        self.step_scale.set(20)
        self.step_scale.pack(side='top', anchor='sw', pady=(0,6))

        # Grid button on the right of the sub frame
        self.grid_button = tk.Button(self.file_menu, text="Select Grid", font=("Arial", 11), command=lambda: self.select_grid_button())
        self.grid_button.pack(side='right', padx=10, pady=2)
        self.save_button.grid(row=0, column=0, padx=10, pady=5)
        self.load_button.grid(row=0, column=1, padx=10, pady=5)

        # canvas settings
        self.canvas = CanvasMap(self.canvas_frame, (700,700))

        # control bindings
        self.canvas.bind("<Motion>", self.update_hover_info)


        # run
        self.mainloop()

    def select_grid_button(self):
        """updates the boolean values"""
        self.can_select=True
        self.can_spawn=False

    # Select file method, called by map selection button
    def select_file(self):
        '''command for map file selection'''
        self.map_file_path = fd.askopenfilename(title="Selct a shapfile",
                                   initialdir="/",
                                   filetypes=[("Shape files", "*.shp")]
                                    )
        if self.map_file_path:
            print(f"Selcted file: {self.map_file_path}")
            self.create_map()
        else:
            print("no file selected")

    #Method to draw spawn markers when placing agents
    def draw_spawn_marker(self, x, y, color, icon):

            """Draw a small circle marker on the main canvas and return the item id.

            x, y: pixel coordinates (same convention used elsewhere in the code).
            color: fill color string (e.g. '#C60707' or 'green').
            """
            radius = 5
            if icon.lower() == "seeker":
                icon_path = UUV_path
            elif icon.lower() == "target":
                icon_path = Target_path
            elif icon.lower() == "detector":
                icon_path = Detector_path

            # ensure canvas exists
            if not hasattr(self, "canvas") or self.canvas is None:
                raise RuntimeError("Canvas not initialized; cannot draw spawn marker")
            try:
                img = Image.open(icon_path)
                img = img.resize((20, 20), Image.Resampling.LANCZOS)  # change size here
                icon = ImageTk.PhotoImage(img)
                self.agent_images.append(icon)  # <-- This keeps the image alive
            except Exception as e:
                print("Error loading agent icon:", e)
                icon = None

            if icon is not None:
                item_id = self.canvas.create_image(
                x,
                y,
                image=icon,
                tags=("setup_marker",)
            )
            else:
                # fallback: draw oval if icon fails
                item_id = self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=color, tags=("setup_marker",)
            )



            return item_id

    # Method to convert the GUI's spawn data into a spawns dict to then be passed to UUV Model
    def build_spawns_from_gui(self) -> dict:
        """
        Convert the GUI's `self.spawn_data` into the `spawns` dict expected by UUVModel.process_spawn_data.

        Returns:
            dict mapping category -> list of spawn entries, where each entry is at least:
                {"type": <agent_type_str>, "pos": [x, y], ...optional fields...}
        Notes:
            - This is robust to case differences between GUI labels and model keys (e.g. "Seeker" vs "seeker" or "GA").
            - It preserves optional fields like "name" and "group_id" if present.
        """
        # Build mappings from agent type (lowercase) -> (type, category)
        type_to_category = {}
        type_lookup = {}
        for cat, types in model.UUVModel.AGENT_CATEGORIES.items():
            for t in types:
                type_to_category[t.lower()] = cat
                type_lookup[t.lower()] = t  # canonical form (keeps GA uppercase if used)

        # Initialize output categories
        spawns: dict = {cat: [] for cat in model.UUVModel.AGENT_CATEGORIES.keys()}

        # Iterate GUI spawn_data (keys may be canonical or user-facing)
        for key_type, entries in self.spawn_data.items():
            # normalize the key into a candidate agent type (string)
            key_type_str = str(key_type) if key_type is not None else ""
            for item in entries:
                # Extract pos and optional metadata
                if isinstance(item, (list, tuple)):
                    pos = list(item)
                    agent_type_guess = key_type_str
                    extras = {}
                elif isinstance(item, dict):
                    pos = item.get("pos")
                    agent_type_guess = item.get("type") or key_type_str
                    # copy optional extras
                    extras = {k: v for k, v in item.items() if k not in ("type", "pos")}
                else:
                    # unsupported entry type; skip
                    continue

                # Validate/normalize pos to [int, int]
                try:
                    pos_x = int(pos[0])
                    pos_y = int(pos[1])
                    pos = [pos_x, pos_y]
                except Exception:
                    # skip invalid positions
                    continue

                # Normalize agent type (case-insensitive lookup)
                agent_type_norm = str(agent_type_guess).strip()
                agent_type_lower = agent_type_norm.lower()
                canonical_type = type_lookup.get(agent_type_lower, agent_type_norm)

                # Determine category (fallback to 'attacker' if unknown)
                category = type_to_category.get(agent_type_lower, "attacker")

                # Build spawn entry
                spawn_entry = {"type": canonical_type, "pos": pos}
                # attach extras if present (name, group_id, color, etc.)
                for k, v in extras.items():
                    spawn_entry[k] = v

                spawns.setdefault(category, []).append(spawn_entry)

        # Remove empty categories
        spawns = {k: v for k, v in spawns.items() if v}
        return spawns

    # Helper function to validate the map when loading configs, checks to see if placed agents are
    # being placed correctly
    def make_grid_validator(self):
        """
        Return a validate_fn(spawn_entry) -> (bool, Optional[str]) bound to current self.map_grid.

        validate_fn returns:
        - (True, None) if valid
        - (False, "reason") if invalid
        """
        g = getattr(self, "map_grid", None)
        if g is None:
            # No grid loaded: accept nothing
            def _no_grid_validator(entry):
                return False, "No grid loaded"
            return _no_grid_validator

        # Determine grid size robustly (support several Grid shapes)
        cols = rows = None

        # Preferred: Grid object exposes a 2D backing array `grid`
        grid_data = getattr(g, "grid", None)
        if grid_data is not None:
            try:
                rows = len(grid_data)
                cols = len(grid_data[0]) if rows > 0 else 0
            except Exception:
                rows = cols = None

        # Fallback: Grid created with `cells_n` for square grid
        if cols is None or rows is None:
            cells_n = getattr(g, "cells_n", None)
            if cells_n is not None:
                cols = rows = int(cells_n)

        # Last fallback: use width/height and cell_size
        if cols is None or rows is None:
            cell_size = getattr(g, "cell_size", None)
            width = getattr(g, "width", None) or getattr(g, "canvas_width", None)
            height = getattr(g, "height", None) or getattr(g, "canvas_height", None)
            if cell_size and width and height:
                cols = int(width / cell_size)
                rows = int(height / cell_size)

        if cols is None or rows is None:
            # If we still can't figure out bounds, return a validator that warns (fail-safe)
            def _unknown_size_validator(entry):
                return False, "Grid size unknown"
            return _unknown_size_validator

        # create final validator that also optionally checks cell-blocked state
        def _validator(entry):
            # entry expected: {"type": ..., "pos": [x,y], ...}
            pos = entry.get("pos")
            if not isinstance(pos, (list, tuple)) or len(pos) != 2:
                return False, "Invalid position format"
            try:
                x = int(pos[0])
                y = int(pos[1])
            except Exception:
                return False, "Position coordinates must be integers"

            if x < 0 or x >= cols or y < 0 or y >= rows:
                return False, f"Position out of bounds: ({x},{y}) not in [0..{cols-1}], [0..{rows-1}]"

            try:
                backing = getattr(g, "grid", None)
                if backing is not None:
                    cell_obj = backing[y][x]  # row=y, col=x
                    # If your blocked id is 1 like model.is_unblocked uses, check:
                    if hasattr(cell_obj, "id") and cell_obj.id == 1:
                        return False, f"Cell at ({x},{y}) is blocked"
            except Exception:
                # ignore cell-object checks if indexing fails
                pass

            return True, None

        return _validator

    # Method used to prompt the user to save the config i.e where to save it, choose the name, etc.
    # Called by the "load config" button, uses the self.build_spawns_from_gui() helper function to
    # build the payload within the .json which is later used to load agents back
    def save_config_dialog(self):
        """
        Prompt user for a filename and save current GUI spawn config using ConfigManager.
        Uses self.build_spawns_from_gui() to build the payload.
        """
        # Build spawns dict
        spawns = self.build_spawns_from_gui()

        # Choose initial dir (fall back to cwd)
        try:
            initialdir = str(self.config_manager.config_dir)
        except Exception:
            initialdir = "."

        # Ask user where to save
        file_path = fd.asksaveasfilename(
            title="Save spawn config",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=initialdir,
        )
        if not file_path:
            return  # user cancelled

        # Save via ConfigManager
        try:
            saved_path, warnings = self.config_manager.save(spawns, path=Path(file_path))
        except FileExistsError as fe:
            mb.showerror("Save error", str(fe))
            return
        except Exception as e:
            mb.showerror("Save error", f"Failed to save config: {e}")
            return

        # Notify user and show non-fatal warnings if any
        if warnings:
            msg = f"Config saved to {saved_path}\n\nWarnings:\n" + "\n".join(warnings)
            mb.showwarning("Config saved with warnings", msg)
        else:
            mb.showinfo("Config saved", f"Config saved to {saved_path}")

    def load_config_dialog(self):
        file_path = fd.askopenfilename(title="Load spawn config", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not file_path:
            return

        validator = self.make_grid_validator()
        cm = self.config_manager
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

        applied = self.apply_loaded_spawns(spawns, wipe_existing=True)
        if applied:
            mb.showinfo("Load complete", "Configuration applied to map.")
        else:
            mb.showinfo("Load cancelled", "Configuration was not applied.")

    # Function to actually apply the agents to the map and the model from the stored values in the
    # .json file (payload), takes the cleaned spawns dict (from ConfigManager.load) and iterates through
    def apply_loaded_spawns(self, spawns: dict, wipe_existing: bool = True) -> bool:
        """
        Apply a loaded `spawns` dict to the GUI (place markers + update spawn_data and UI).
        """
        # 1) Refuse if simulation is running
        if getattr(self, "is_running", False):
            mb.showerror("Cannot place agents", "Please stop the simulation before applying a config.")
            return False

        # 2) Ensure map/grid present
        if self.map_grid is None:
            mb.showerror("No map/grid", "Please load/create a map before applying a spawn configuration.")
            return False

        # 3) If there are existing placed agents, confirm/clear them
        has_existing = any(len(lst) > 0 for lst in self.spawn_data.values())
        if has_existing and not wipe_existing:
            proceed = mb.askyesno("Overwrite existing agents?",
                                "There are already agents placed. Overwrite with loaded config?")
            if not proceed:
                return False

        if has_existing and wipe_existing:
            self.reset_simulation()

        # 4) Place loaded entries into spawn_data and draw markers
        cell_size = getattr(self.map_grid, "cell_size", None)
        if not cell_size:
            mb.showerror("Grid error", "Grid cell size unknown; cannot draw spawn markers.")
            return False

        def find_type_key(t: str):
            if t in self.spawn_data:
                return t
            t_lower = str(t).lower()
            for key in list(self.spawn_data.keys()):
                if key.lower() == t_lower:
                    return key
            self.spawn_data.setdefault(t, [])
            return t

        for category, entries in spawns.items():
            for entry in entries:
                t = entry.get("type")
                pos = entry.get("pos")
                if t is None or pos is None:
                    continue

                type_key = find_type_key(t)
                placed = dict(entry)

                try:
                    grid_x = int(pos[0])
                    grid_y = int(pos[1])
                    px = grid_x * cell_size
                    py = grid_y * cell_size
                except Exception:
                    continue

                color = placed.get("color")
                if not color:
                    color = self._agent_type_colors_norm.get(str(t).lower())
                if not color:
                    color = "green"



                # draw marker and store marker_id
                try:
                    marker_id = self.draw_spawn_marker(px, py, color, t)
                    placed["marker_id"] = marker_id
                except Exception:
                    placed["marker_id"] = None

                # If this is a detector, draw its dashed detection radius immediately
                if str(t).lower() == "detector":
                    placed["radius_id"] = self.draw_detector_radius(px, py, radius=20, marker_id=placed.get("marker_id"))

                # append to GUI spawn_data
                self.spawn_data.setdefault(type_key, []).append(placed)

        # 5) Rebuild agent_menu counts from spawn_data
        self.agent_menu.agent_display_data.clear()
        for t, entries in self.spawn_data.items():
            for e in entries:
                name = e.get("name") or t
                key = (name, t)
                self.agent_menu.agent_display_data[key] = self.agent_menu.agent_display_data.get(key, 0) + 1

        self.agent_menu.update_agent_listbox()
        return True

    #Method for creating the map
    def create_map(self):
        '''command for map/grid creation'''

        self.current_map = MapControl(
            shape_path=self.map_file_path,
            canvas=self.canvas,
            shallow_color=self.map_shallow_color,
            deep_color=self.map_deep_color
        )
        self.map_grid = Grid(width=self.canvas_size[0], height=self.canvas_size[1], cells_n=self.cell_count, canvas=self.canvas)
        self.canvas.config(background="#0A7005")
        # self.canvas.unbind("<Button-1>")

    # Method to start and pause the simulation, used by the start button
    def on_start_click(self):
        """Start / pause the simulation and create the mesa_model safely."""
        self.can_spawn = False
        self.can_select = False
        if not self.is_running:
            # Ensure canvas not bound to spawning
            # self.canvas.unbind("<Button-1>")
            # Provide immediate UI feedback
            self.start_button.config(state="disabled", bg="#333333", text="⏳ Starting...")

            # If model already exists, just resume it (do not clear/recreate)
            if self.mesa_model is None:
                # Validate map/
                # grid preconditions
                if self.map_grid is None:
                    tk.messagebox.showerror("Error", "Please load a map before starting the simulation.")
                    self.start_button.config(state="normal", bg="#333333", text="▶ Start", command=self.on_start_click)
                    return

                # Create the model
                try:
                    viable_spawn_area = self.viable_spawn_select()
                    self.mesa_model = model.UUVModel(
                        spawns=self.spawn_data,
                        map=self.current_map,
                        grid=self.map_grid,
                        canvas=self.canvas,
                        viable_spawn=viable_spawn_area,
                        animator=self
                    )
                except Exception as e:
                    tk.messagebox.showerror("Error creating model", f"Failed to create simulation model:\n{e}")
                    # restore button state
                    self.mesa_model = None
                    self.start_button.config(state="normal", bg="#333333", text="▶ Start", command=self.on_start_click)
                    return
            else:
                # Model exists - add any new agents that were spawned while paused
                self.add_new_agents_to_model()

            #Clear spawn markers and detector radius rings after model is created
            self.agent_images.clear()
            self.canvas.delete("setup_marker")
            self.is_running = True
            # Switch Start button to a Pause / Running state
            self.start_button.config(state="normal", bg="#333333", text="⏸ Running...", command=self.on_start_click)
            self.animate()

        else:
            # We are running -> pause/stop
            if self.animation_job:
                try:
                    self.after_cancel(self.animation_job)
                except Exception:
                    pass
                self.animation_job = None
            self.start_button.config(state="normal", bg="#333333", text="▶ Start", command=self.on_start_click)
            self.canvas_frame.config(bg="#333333")
            self.is_running = False

    # Helper function used by on_start_click, this method checks if any new agents were added
    # since we paused the sim and then appends them to the model (only the newly added agents)
    def add_new_agents_to_model(self):
        """Add agents spawned during pause to the existing model."""
        if self.mesa_model is None:
            return

        # Track which spawn positions already have agents in the model
        # We'll check the actual agent positions, not the tracking dict
        existing_spawn_positions = set()

        # Get all agents and their spawn positions
        for agent in self.mesa_model.agents:
            if hasattr(agent, 'spawn'):
                # spawn is stored as [x, y] so convert to tuple for set
                existing_spawn_positions.add(tuple(agent.spawn))

        # Find new agents in spawn_data that aren't in the model yet
        for agent_type, spawn_list in self.spawn_data.items():
            for spawn_entry in spawn_list:
                pos = tuple(spawn_entry['pos'])

                # Check if this spawn position already has an agent
                if pos not in existing_spawn_positions:
                    # This is a new agent - create it
                    print(f"Creating new {agent_type} at {pos}")

                    if agent_type == "GA":
                        # GA agents create multiple instances per position
                        group_id = len([a for a in self.mesa_model.agents
                                    if hasattr(a, 'spawn') and tuple(a.spawn) == pos])
                        for _ in range(self.mesa_model.POP_SIZE):
                            self.mesa_model.create_agent(type=agent_type, pos=list(pos), group_id=group_id)
                    else:
                        self.mesa_model.create_agent(type=agent_type, pos=list(pos))

                    # Mark this position as having an agent now
                    existing_spawn_positions.add(pos)

    # Method to reset the simulation, comprehensive multiple layer checks and clears including
    # the agent spawn data, lists, data collector, and canvas items like drawn ovals. Called by reset button.
    def reset_simulation(self):
        """Fully stop and clear the running simulation and UI state."""
        # 1) Stop animation
        if self.animation_job:
            try:
                self.after_cancel(self.animation_job)
            except Exception:
                pass
            self.animation_job = None
        self.is_running = False

        # 2) If model exists, try to clear it
        if self.mesa_model is not None:
            if hasattr(self.mesa_model, "clear_agents"):
                try:
                    self.mesa_model.clear_agents()
                except Exception as e:
                    print("Warning: error while clearing model:", e)
            # drop reference so nothing calls it again
            self.mesa_model = None

        # 3) Clear related canvas items
        for item in self.canvas.find_all():
            tags = self.canvas.gettags(item)
            if "agent" in tags or "target" in tags or "setup_marker" in tags or "hover_rect" in tags or "detector" in tags or "search" in tags:
                self.canvas.delete(item)

        # 4) Clear GUI lists and spawn instructions
        self.agent_menu.agent_listbox.delete(0, tk.END)
        self.agent_menu.agent_display_data.clear()
        for agent_type in self.spawn_data:
            self.spawn_data[agent_type] = []

        # 5) Reset labels / buttons

        self.coord_label.config(text="Grid Position: (x, y) | [lat, lon]")
        self.start_button.config(state="normal", bg="#333333", text="▶ Start", fg="white", command=self.on_start_click)
        self.canvas_frame.config(bg="#333333")

        # 6) delete selection rect
        self.canvas.delete("spawn_sel")

    def animate(self):
        '''animate the screen'''
        if self.is_running and self.mesa_model is not None:
            self.mesa_model.step()
            # step through the model
            self.animation_job = self.after(self.step_interval, self.animate)
        else:
            self.animation_job = None

    # Helper function to change the current step interval (argument taken by the animation job)
    # in order to more easily set the current step speed of the program i.e how fast the sim moves
    def set_step_interval(self, ms):
        """Set animation interval in ms. If running, reschedule next tick immediately."""
        try:
            ms = int(ms)
        except Exception:
            return
        # clamp to a reasonable minimum
        ms = max(10, ms)
        self.step_interval = ms

        if self.is_running:
            # cancel pending after and schedule a new one with updated interval
            if self.animation_job:
                try:
                    self.after_cancel(self.animation_job)
                except Exception:
                    pass
                self.animation_job = None
            # schedule next tick with new interval
            self.animation_job = self.after(self.step_interval, self.animate)

    # Method used to create popup windows, currently takes argument "choice" and will either open
    # UAV select window or the analysis window
    def create_popup(self,choice):
        '''create the popup window'''
        if self.popup_window is None and choice == 1:
            self.popup_window = UAVSelectWindow(self,"Select UAV", (400,300), self.canvas)
            self.can_select=False
            self.can_spawn=True
        elif self.popup_window is None and choice == 2:
            self.popup_window = AnalysisWindow(self,"Analysis",(1100,600), self.canvas)
            self.can_select=False
            self.can_spawn=True

    # Helper method to snap the mouse to the grid (because the grid uses cells)
    def snap_to_grid(self, x, y):
        '''Snaps the mouse to the grid'''
        if self.map_grid is not None:
            grid_size = self.map_grid.cell_size
            snapped_x = round(x / grid_size) * grid_size
            snapped_y = round(y / grid_size) * grid_size
            grid_x = int(round(snapped_x / grid_size))
            grid_y = int(round(snapped_y / grid_size))
        else:
            snapped_x, snapped_y = x, y
            grid_x, grid_y = int(x), int(y)
        return snapped_x, snapped_y, grid_x, grid_y

    # Helper method to determine if there are overlapping items on the lpaded map
    # in this case, checks to see if the item overlaps the map itself, if so it returns true
    # because that means the item is within the map
    def is_inside_map(self, x, y):
        '''checks if inside the canvas bounds'''
        overlapping_items = self.canvas.find_overlapping(x, y, x, y)
        for item_id in overlapping_items:
            tags = self.canvas.gettags(item_id)
            if "map" in tags:
                return True
        return False

    # Method to take find current cursor locaiton on map, highlights current grid and also updates
    # the coord label with the current location of the cursor
    def update_hover_info(self, event):
        '''updates the hover info and shows the current selected grid'''
        if self.map_grid is None:
            return

        grid_size = self.map_grid.cell_size

        snapped_x = round(event.x / grid_size)
        snapped_y = round(event.y / grid_size)

        max_index = self.map_grid.cells_n - 1
        snapped_x = max(0, min(snapped_x, max_index))
        snapped_y = max(0, min(snapped_y, max_index))

        pixel_x = snapped_x * grid_size
        pixel_y = snapped_y * grid_size

        if self.current_map is not None and hasattr(self.current_map, "canvas_to_latlon"):
            lat, lon = self.current_map.canvas_to_latlon(pixel_y, pixel_x)
            self.coord_label.config(text=f"Grid Position: ({snapped_x}, {snapped_y}) | [{lat:.3f}, {lon:.3f}]")
        else:
            self.coord_label.config(text="Grid Position: (x, y) | [lat, lon]")

        self.canvas.delete("hover_rect")
        x1 = snapped_x * grid_size - grid_size / 2
        y1 = snapped_y * grid_size - grid_size / 2
        x2 = x1 + grid_size
        y2 = y1 + grid_size
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=2, tags="hover_rect")

    def viable_spawn_select(self):
        """Selects the viable spawn areas for the detectors"""
        rect_ids = self.canvas.viable_spawn_pos()
        #if len(rect_ids) == 0:
        #    raise Exception("Create a grid spawn locations")

        # print(f"rects: {rect_ids}")
        viable_spawns = list()
        for id in rect_ids:
            # get the top and bottom coords
            # print(f"rect id: {id}")
            coords = self.canvas.coords(id)
            x1, y1, x2, y2 = coords
            top_left = self.snap_to_grid(x1, y1)
            bottom_right = self.snap_to_grid(x2, y2)
            top_left = top_left[-2:]
            bottom_right = bottom_right[-2:]
            # print(f"top_left {top_left}, bottom_right {bottom_right}")

            for j in range(top_left[1], bottom_right[1]+1):
                for i in range(top_left[0], bottom_right[0]+1):
                    if self.map_grid.grid[j][i].id == 0:
                        spawn_point = (i, j)
                        if spawn_point not in viable_spawns:
                            viable_spawns.append(spawn_point)
                            # print(f"({i}, {j})")
            # print(f"length {len(viable_spawns)}")
        if len(viable_spawns) == 0:
            viable_spawns = None
        else:
            return viable_spawns
             # Helper function used when spawning detectors to ensure their radius is created too

    def draw_detector_radius(self, px, py, radius=20, marker_id=None):
        """
        Draw a dashed detection-radius ring at pixel coords (px,py).
        Returns the canvas item id of the ring or None on failure.

        - `radius` in pixels (default matches DetectorAgent.radius = 20).
        - if `marker_id` is provided the method will attempt to keep the marker above the ring.
        """
        if not hasattr(self, "canvas") or self.canvas is None:
            return None
        try:
            radius_id = self.canvas.create_oval(
                px - radius, py - radius,
                px + radius, py + radius,
                outline='white', dash=(3, 3), tags=('detector',)
            )
            # Ensure ring exists and keep marker visible above it if provided
            try:
                self.canvas.lift(radius_id)
                if marker_id is not None:
                    self.canvas.lift(marker_id)
            except Exception:
                pass
            return radius_id
        except Exception:
            return None

    #Helper function to grab agent colors from their class and use them on the sim
    def _build_agent_colors_from_model(self) -> dict:
        """
        Extract agent colors from the actual agent classes in the model.
        Returns a normalized dict {agent_type_lower: color_hex}
        """
        colors = {}

        # Access the AGENT_MAP from the model
        agent_map = model.UUVModel.AGENT_MAP

        for agent_type, agent_class in agent_map.items():
            # Get the DEFAULT_COLOR class attribute if it exists
            color = getattr(agent_class, 'DEFAULT_COLOR', None)
            if color:
                colors[agent_type.lower()] = color
        return colors

    def _build_agent_sprite_from_model(self) -> dict: #Same format for default color above, for sprites instead of ovals
        """
        Extract agent sprite paths from the actual agent classes in the model.
        Returns a normalized dict {agent_type_lower: sprite_path}
        """
        sprites = {}

        # Access the AGENT_MAP from the model
        agent_map = model.UUVModel.AGENT_MAP

        for agent_type, agent_class in agent_map.items():
            # Get the SPRITE_PATH class attribute if it exists
            sprite = getattr(agent_class, 'SPRITE_PATH', None)
            if sprite:
                sprites[agent_type.lower()] = sprite
        return sprites
#End of App (parent) methods
#=============================================================================================================================================
#=============================================================================================================================================
