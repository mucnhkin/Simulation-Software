# Operation Manual 

## GIS Data
This section covers where and how to get the mapping data for your simulations. The data used comes free from the U.S. Office of Coast Survey.
1. Go to the [U.S. Office of Coast Survey](https://nauticalcharts.noaa.gov/data/gis-data-and-services.html)
2. Click the ENC Direct to GIS drop down or use this [ENC Direct to GIS](https://encdirect.noaa.gov/)

![Image of the office of coast survey](resources/us_office.png)

3. Navigate towards a region, i choose Narragansett Bay

![narragansett bay](resources/bay.png)

4. open data extract drop down menu

![layer menu](resources/layer_menu.png)

5. Choose any of the categories, i need Harbor

6. Select DepthsA\Harbour_Depth_area.
>[!NOTE]
>The program can only handle .shp data. However, that data is versatile and comes in lots of options 

>[!TIP]
> Try to use only data that ends in area ie. Harbour_Dredge_Area

7. Select the region to collect by using Area of Interest.

![area of interest](resources/area_of_interest.png)

8. Extract the data as a .shp file

![extract data](resources/extract_data.png)

9. A download will appear and unzip the folder

## Simulation Software
This section covers how to use simulation software.
>[!NOTE]
>This covers how to run in VS Code. Other code editors may be different
1. go to the main.py and start
2. This will open the simulation window

![image of a simulation window](resources/startup.png)

3. Navigate to the Map Selection and click "Select". This will open your file explorer.
4. Choose your GIS data which should be a shape file .shp. 
5. The map you selected will be rendered in the canvas
> [!NOTE] 
>The grid dots can be toggled in the code

![image of a simulation window with a rendered map](resources/map_loaded.png)

6. Navigate to the Agent Selection and click "+ Add Agent". This will open a pop up.

![image of a simulation window](resources/agent.png)

7. Navigate to the Select UUV window.
8. With "Attacker" selected, choose seeker from dropdown, and click "Spawn". This will allow you to click on the map to set the spawn location of the attacking uuv agent.
9. Select "Defender" and choose "target" from the dropdown and spawn similarly.
10. Close the pop-up window.
11. Select "Choose Grid" next to Config Options to select the viable spawn locations for the detecting UUV agents used by the genetic algorithm.
12. Navigate to the Simulation Options and click "Start" to begin.
