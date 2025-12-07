# Code base
This is a live document; it should be updated. This document attempts to explain what is happening in the code base. The repo code itself will also have documentation but just in case this is here. I will not cover every little detail but will get the big picture across.

## Genetic Algorithm 
Currently, there are two iterations of the GA in the program. One version utilizes the `search_agent.py` which progressively gets closer to the target. Another is the version that operates in the `model.py`.

### Search_agent.py
This agent uses its own version of GA to accomplish its goal. It was built on the assumption that the attackers wouldn’t know where the targets were. However, it was scrapped after further conversation with Prof. Lance as he preferred to optimize the placement of detection units. This GA version while scrapped can still be used as its built into the `model.py`, but some Booleans will need switching. due to it being obsolete, i will not cover the agent itself but the functions used in the `model.py` to avoid confusion between the two different GAs. It uses these functions in this order inside the `model.py`.
```
def create_initial_agent_pop(self):
def score_ga_agents(self):
def create_next_generation(self, agent_type):
```
For a overview of what is happening look at this [PowerPoint](assets/Genetic_Algorithm_class.pdf)

```
def create_initial_agent_pop(self):
```
This function handles will spawn the agents for both normal agents and GA agents. it will spawn the GA agents as long as the agent type is "GA" else it operates and calls the `create_agent` function normally.

```
if self.ga_model_active is False: # for the GA agents
    if not raw_agent_data.empty and not raw_model_data.empty:
        # get agent data
        current_step = raw_agent_data.index.get_level_values('Step').max() # get the max of the Step
        is_finnsihed_step = raw_agent_data.xs(current_step, level="Step")['Finnished_agent_count'] # get the cross section of the newest step and Step
        finished_count = is_finnsihed_step.sum() #return a sum of how many agents have finnished
        print(f"Finished agents at step {current_step}: {finished_count}")

    if finished_count == len(self.agents):
        # add the losers to a kill list to remove later
        self.current_generation+=1
        print(f"Current Generation: {self.current_generation}")
        self.score_ga_agents()
        self.create_next_generation(agent_type="GA")
```
this is inside the `def step(self)` function. It is very similar to the model GA as its in the same spot and only activates if `self.ga_model_active` is set to false. If the `finnish_count` equals the length of the agents, then the next generation is created after scoring.
```
def score_ga_agents(self):
```
`score_ga_agents()` scores the list of ga agents and orders them from best to worst. From there the best two are selected and the mating function inside the agent is called and a new generation is created
```
def create_next_generation(self, agent_type):     
```
creates the next generation of GA agents. I have not used it in a while so don’t know if still operational without errors. Kept inside incase the Prof. wants it back.

### Model GA
This is the current version of the genetic algorithm. Instead of being a agent, the model keeps a list of chromosomes that act as scenarios with the best two continuing on to breed. it uses these functions in this order.
```
def create_inital_model_pop(self):
def create_model_agent(self):
def create_agent(self, type, pos, **parameters):
def reset_sim(self):
def create_next_model_generation(self):
```
For a more in depth understanding of wants going on read this [PowerPoint](assets/UUV_Genetic_Algorithm_Optimization.pdf)

## model.py
This is the Mesa model that controls and calls the step function to iterate through the simulation. it is also responsible for the [GA](#genetic-algoritum). Additionally, it collects the data of each step from the `mesa.DataCollecor`. it will process all the spawn data passed from the [App](#app) when its created in there to run its simulation. it is obviously responsible for the creating the actual agent objects. The speed of the step is also controlled in the [App](#app). Adding new agents is simple, just add it to the `AGENT_MAP` and `AGENT_CATEGORIES`.
```
    # needs to be manually set here so spell correctly
    AGENT_MAP = {
        "seeker" : agent.UUVAgent,
        "detector" : detector_agent.DetectorAgent,
        "GA" : search_agent.SearchAgent,
        "CUUV" : CounterUUVAgent.CUUVAgent,
        "target" : target_agent.TargetAgent
    }
    # Universal agent types
    # if add new element must add a comma to end
    # ie ('target', 'test', ) <-see how there is a comma after the new 'test' agent
    AGENT_CATEGORIES = {
        "attacker" : ("seeker", "GA"),
        "defender" : ('target',"detector", "CUUV",)
    }
```

## agent.py
This is the main attacking UUV used in simulations. It is supposed to use A* to navigate towards its targets via their grid position. However, someone used AI on the code and now its a buggy mess that navigates towards its targets via a unit vector towards the targets screen position which is horrifically incorrect. The A* is still there just needs to be re-implemented.

## CounterUUVAgnet.py
Is the counter UUV agent that is spawned by the [detector_agent.py](#detector_agentpy). It will be spawned then seek out the target that was assigned to it by the [detector_agent.py](#detector_agentpy) and destroy it.

## detector_agent.py
This is the detector agent that is that is used by the [model.py](#modelpy) and its [GA](#model-ga). it will detect when an [agent.py](#agentpy) is within radius and release a [CounterUUVAgent.py](#counteruuvagnetpy) to detsroty it.

## search_agent.py
This is an obsolete agent that used an older version of [GA](#search_agentpy) and is discussed there

## target_agent.py
This a half finished agent that is supposed to replace the target position with a agent target.

## cell.py
A base component that is used multiple times the program. stores data for the A* algorithm. is used by the [grid.py](#gridpy)

## grid.py
Responsible for the creation of the grid that all the agents and mesa model use. this is also used to get grid position for spawn locations by using the [cell.py](#cellpy).This is created by the gui. This is where you can toggle to visualize the grid positions inside the `draw_test_grid()` function. is used by the [New_gui.py](#new_guipy)

## map.py
Responsible for converting .shp files into graphics to be used by the canvas in tkinter. contains functionality to return the polygon you click. will also return data regarding the depth of a polygon in terms of water depth. is used by the [New_gui.py](#new_guipy)

## New_gui.py
Contains a bulk of the program. This script is in desperate need of upkeep and to be split into separate scripts as its approaching 1000 lines of code that are related to each other. Each part of the script will be discussed. A bulk of the AI generated code resides in this script.😨

### App
Is the main app script and what you will see most of the time when looking at graphics. Contains the main app window. Flattens the given agents list into a more reasonable formate to be used in the graphics. it creates the [Mesa model](#modelpy) that controls the agents. It uses [Menu](#menu), [FileMenu](#filemenu), [AgentMenu](#agentmenu), [CanvasFrame](#canvasframe), [UAVSelectWindow](#uavselectwindow), [ConfigManager](#configpy), [GeneralFrames](#generalframes), [CanvasMap](#canvasmap), [grid.py](#gridpy), and [model.py](#modelpy).

### Menu
Creates the menu that is used by other sub menus. Doesn’t do to much but was made incase of adding more functionality. used by [App](#app).

### FileMenu
This is the menu at the bottom of the app. in the rectangle area that hold strings of the mouse grid location and such. used by [App](#app).

### CanvasFrame
The Frame that holds the tkinter canvas. used by [App](#app).

### CanvasMap
this is where the actual graphics for the map and simulation take place. It setup the canvas that the [map.py](#mappy) uses and the agents. Also gets the grid position for viable spawns. used by [App](#app).

### GeneralFrames
A general frames for quickly prototype and use. used by [App](#app).

### AgentMenu
Agent Menu, a more specialized menu used for the agent section, holds the "add agent" button and the agent list box, implemented this way because it allows for more complex implementations and methods. responsible for the agent window popup. used by [App](#app).

### AnalysisWindow
Analysis Window class, this window is used by the analysis button to call the `open_popup()` method and then open this window, this is its own class because it's functionality and implementation will be tailored specifically for analysis of the sim, which will require many self-contained methods. used by [App](#app).

### AgentInfoWindow
This doesn’t do anything. someone added it and it just doesn’t do anything. its supposed to be a window that appears when double clicking an agent on the map used for setting variables such as target and cost

### UAVSelectWindow
This is the popup menu. it is where you select which UUVs or agents you want to include in the simulation. used by [App](#app).

## Config.py
This is the configuration manager script. it is where you can save a simulation and rerun at another time. I cant really comment on this, nearly all of this is AI generated.