# Code base
This is a live document, it should be updated. this document attemps to explain what is happening in the code base. The repo code itself will also have documentation but just in case this is here. I will not cover every little detail but will get the big picture across.

## Genetic Algoritum 
Currently, there are two iteration of the GA in the program. One version utilizes the `search_agent.py` which progressivly gets closer to the target. Another is the version that operates in the `model.py`.

### Search_agent.py
This agent uses its own version of GA to accomplish its goal. It was built on the assumption that the attackers wouldnt know where the targets were. However, it was scrapped after futher conversaion with Prof. Lance as he preferd to optimize the placement of detection units. This GA version while scrapped can still be used as its built into the `model.py`, but some booleans will need switiching. due to it being obsolete, i will not cover the agent itself but the functions used in the `model.py` to avoid confusion between the two differnet GAs. It uses these fucntions in this order inside the `model.py`.
```
def create_initial_agent_pop(self):
def score_ga_agents(self):
def create_next_generation(self, agent_type):
```
For a overview of what is happing look at this [PowerPoint](assets/Genetic_Algorithm_class.pdf)

```
def create_initial_agent_pop(self):
```
This function hanndles will spawn the agents for both normal agents and GA agents. it will spawn the GA agents as long as the agent type is "GA" else it operates and calls the `create_agent` fucntion normally.

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
this is insde the `def step(self)` function. It is very simulure to the model GA as its in the same spot and only activates if `self.ga_model_active` is set to false. If the `finnish_count` equals the len of the agents then the next generation is created after scoreing.
```
def score_ga_agents(self):
```
`score_ga_agents()` scores the list of ga agents and orders them from best to worst. from there the best two are selected and the mating function inside the agent is called and a new generation is created
```
def create_next_generation(self, agent_type):     
```
creates the next generation of GA agents. I have not used in a while so dont know if still operational without errors. Kept inside incase the Prof. want it back.

### Model GA
This is the current version of the genetic algrothum. instead of being a agent, the model keeps a list of chromosomes that act as scenarios with the best two continuing on to breed. it uses these functions in this order.
```
def create_inital_model_pop(self):
def create_model_agent(self):
def create_agent(self, type, pos, **parameters):
def reset_sim(self):
def create_next_model_generation(self):
```
For a more indepth understanding of wants going on read this [PowerPoint](assets/UUV_Genetic_Algorithm_Optimization.pdf)

## model.py

## cell.py
A base component that is used multiple times the program. stores data for the A* algorithum. is used by the [grid.py](#gridpy)

## grid.py
Responisble for the creation of the grid that all the agents and mesa model use. this is also used to get grid position for spawn locations by using the [cell.py](#cellpy).This is created by the gui. This is where you can toggle to visuale the grid positions inside the `draw_test_grid()` function. is used by the [New_gui.py](#new_guipy)

## map.py
Responsible for converting .shp files into graphics to be used by the canvas in tkinter. contains functionallity to return the pologyon you click. will also return data regaruding the depth of a polygon in terms of water depth. is used by the [New_gui.py](#new_guipy)

## New_gui.py
Contains a bulk of the program. This script is in depsterate need of upkeep and to be split into sceperate scripetes as its approching 1000 lines of code that are related to each other. Each part of the script will be discussed. A bulk of the AI generated code resides in this script.😨

### App
Is the main app script and what you will see most of the time when looking at graphics. Contains the main app window. Flattens the given agents list into a more reasonable formate to be used in the graphics. it creates the [Mesa model](#modelpy) that controls the agents. It uses [Menu](#menu), [FileMenu](#filemenu), [AgentMenu](#agentmenu), [CanvasFrame](#canvasframe), [UAVSelectWindow](#uavselectwindow), [ConfigManager](#configpy), [GeneralFrames](#generalframes), [CanvasMap](#canvasmap), [grid.py](#gridpy), and [model.py](#modelpy).

### Menu
### FileMenu
### CanvasFrame
### CanvasMap
### GeneralFrames
### AgentMenu
### AnalysisWindow
### AgentInfoWindow
### UAVSelectWindow

## Config.py