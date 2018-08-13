"""
Define user script in scripts folder.
All 'userscripts must,
    - include a setup() and loop(img) function
    - call super().setup() inside setup method
    - include a __init__() method and initialize instance attributes
    - call super().__init__(bot) inside __init__() method
    - loop must accept one variable as img, but try not to change img value. If you change it change it in-place. Can
    use img to tasks such as refreshing window

- Setup will run only once at the simulation initialization
- Loop will run each time screen is updated(by default)
- You can force screen refresh by util.refreshScreen(), however note that additional loop() functions will not run at
these forced refreshes
- If loop() returns STOP_SIMULATION value, simulation will stop.

Set these global variable values to set bot settings. Place settings at the end of file.
    - settingsImagePath : Image path of maze
    - settingsStartX, settingsStartY : Start position of bot
    - settingsFaceDirection : Direction bot is facing
    - settingsGridSideSquares : Squares per each side in maze grid
    - settingsSrcClass : Default class to load as Src

Since bot has no way of knowing some values in real world,
    - Try not to use bot functions rather than basic movement and sensor
    - Try not to use bot position variables such as bot.x, bot.direction
    - It is OK to access bot.side because it is known in most situations
    - Try not to use settings values

Use UserScript variables/methods,
    - turn_right, turn_left, go_forward, go_to_right, go_to_left, go_backward: Movement
    - is_wall_in_front, is_wall_in_left, is_wall_in_right: Sensor data
    - tile_in_the_direction, refresh_screen, wait_for_user_key, sleep, user_pressed_exit: Helpers
    - self.start, self.x, self.y, self.direction, self.wait_duration
"""

from datatypes import Direction
from scripts.depth_first_search import DepthFirstSearch

# from scripts.right_hand_rule import RightHandRule

settingsImagePath = "Maze.png"
settingsStartX = 1
settingsStartY = 1
settingsFaceDirection = Direction.EAST
settingsGridSideSquares = 14
settingsSrcClass = DepthFirstSearch
