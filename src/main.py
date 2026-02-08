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

from agents.model import UUVModel
import map
import os
from New_gui import App

def main():
    # setup globals
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_PATH)
    app = App('simulation', (1100,800), PARENT_DIR)
     
if __name__ == "__main__":
    main()