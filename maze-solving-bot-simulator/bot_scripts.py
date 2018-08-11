"""
Define user script here.
All userscripts must,
    - include a setup() and loop() function
    - include a __init__() method which takes 'bot' parameter
    - Should NOT include any methods which affects the value of bot in __init__()
    
- Setup will run only once at the simulation initialization
- Loop will run each time screen is updated(by default)
- You can force screen refresh by util.refreshScreen(), however note that additional loop() functions will not run at these forced refreshes
- If loop() returns STOP_SIMULATION value, simulation will stop.
- Call cv2.destroyAllWindows() to close current window. However if not STOP_SIMULATION is issued, new refresh will cause a new window to load.
- Use cv2.waitKey(0) to wait for a KeyPress

Set these global varible values to set bot settings. Place settings at the end of file.
    - settingsImagePath : Image path of maze
    - settingsStartX, settingsStartY : Start position of bot
    - settingsFaceDirection : Direction bot is facing
    - settingsGridSideSquares : Squares per each side in maze grid
    - settingsSrcClass : Default class to load as Src
"""
import cv2
from datatypes import Direction

STOP_SIMULATION = 0x435


class UserKeyRobot:
    def __init__(self, bot):
        self.bot = bot

    def setup(self):
        pass

    def loop(self):
        pressedKey = cv2.waitKey(0)
        if pressedKey == 27:
            cv2.destroyAllWindows()
            return STOP_SIMULATION
        elif pressedKey == ord('w'):
            self.bot.goForward()
        elif pressedKey == ord('a'):
            self.bot.turnCounterClockwise()
        elif pressedKey == ord('d'):
            self.bot.turnClockwise()


settingsImagePath = "Maze.png"
settingsStartX = 1
settingsStartY = 1
settingsFaceDirection = Direction.EAST
settingsGridSideSquares = 14
settingsSrcClass = UserKeyRobot
