# python-projects

## maze-solving-bot-simulator

Small bot to simulate and test maze solving algorithms before designing the robot.

### Prerequisites

- python 3
- open-cv
- numpy

### How to run

Run `run.py` using python 3. Exit by continuously pressing `Esc` several times. In default `FloodFill` algorithm, press any key to switch to next mode when bot is waiting for a input.

### Changing map and other settings

You can change map by changing `maze.png` image. Add a thick black line to denote a wall. Use deep yellow color to denote floor color changes. All light colors and thin black lines will be ignored.

Furthermore you can change basic settings to change bot position, facing direction,... by changing settings variable values. These can be found in `bot_scripts.py` at the end of file.

| Variable Name             | Default Value    | Description                                                  |
| ------------------------- | ---------------- | ------------------------------------------------------------ |
| `settingsImagePath`       | `"Maze.png"`     | Image map to load.                                           |
| `settingsStartX`          | `1`              | Starting X coordinate(column) of the bot. Can be a value between 1 and `settingsFaceDirection` (inclusive). |
| `settingsStartY`          | `1`              | Starting Y coordinate(row) of the bot. Can be a value between 1 and `settingsFaceDirection` (inclusive). |
| `settingsFaceDirection`   | `Direction.EAST` | Direction that bot is facing in the beginning. Can be one of `Direction.EAST`, `Direction.WEST`, `Direction.SOUTH` and `Direction.NORTH`. |
| `settingsGridSideSquares` | `14`             | Number of squares per one side in the grid. If `settingsGridSideSquares` is 14, grid has to be a 14x14  grid. |
| `settingsSrcClass`       | `OptimizedFloodFill` | Class Name to load to the bot                                |

However note that when checking default Flood Fill Algorithm, do not use `settingsStartX` and `settingsStartY` values that do not represent a corner cell. For example  `settingsGridSideSquares` is `14`, only values you can use for `settingsStartX` and `settingsStartY` are `1` and `14`.

`settingsSrcClass`s available:

| Class Name           | Import Statement                                             | Description                                                  |
| -------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `RightHandRule`      | `from scripts.right_hand_rule import RightHandRule`          | Always go to right hand side. Does not work in many mazes.   |
| `DepthFirstSearch`   | `from scripts.depth_first_search import DepthFirstSearch`    | Depth First Search to identify all cells and then Breadth First Search to find shortest path. |
| `FloodFill`          | `from scripts.flood_fill import FloodFill`                   | Flood fill normal algorithm. Has debug output.*              |
| `OptimizedFloodFill` | `from optimized.optimized_flood_fill import OptimizedFloodFill` | Same as `RightHandRule`.**                                   |
| `OptimizedFloodFill` | `from optimized.optimized_flood_fill import OptimizedFloodFill` | Same as `FloodFill`                                          |

*To enable debug output,  change`DEBUG`  value and `DEBUG_ROTATE` value in`scripts/depth_first_search.py`.

| Variable       | Value   | Effect                                                       |
| -------------- | ------- | ------------------------------------------------------------ |
| `DEBUG`        | `True`  | Enable debug window.                                         |
| `DEBUG`        | `False` | Disable debug window.                                        |
| `DEBUG_ROTATE` | `0`     | Set if starting position is in Top Left. Has any effect if and only if debug window is enabled. |
| `DEBUG_ROTATE` | `1`     | Set if starting position is in Bottom Left. Has any effect if and only if debug window is enabled. |
| `DEBUG_ROTATE` | `2`     | Set if starting position is in Bottom Right. Has any effect if and only if debug window is enabled. |
| `DEBUG_ROTATE` | `3`     | Set if starting position is in Top Right. Has any effect if and only if debug window is enabled. |

**Optimized version is same as normal one, bus tries to use simple data-types only.

### Add a custom class

All **normal** `userscripts` should be defined in separate files in `scripts` folder. They have to be subclasses of `base_script.UserScript`.

Sample custom class,

```python
import robot
from scripts import base_script

class CustomClassName(base_script.UserScript):
    def __init__(self, bot: robot.Robot):
        """Initialize"""
        super().__init__(bot)
        # initialize all your 'global' variables here to None
        # eg:
        # self.center: tuple = None
        # self.grid: list = None

    def setup(self):
        super().setup()
        # Add all variable initialization and startup code
        # eg:
        # self.center = (7, 7)
        # self.grid = [[0]*14 for _ in range(14)]

    def loop(self, img):
        super().loop(img)
        # Add loop code (handling robot)
        # Use below statements to allow users to exit by pressing 'Esc'
        self.user_pressed_exit(self.waitDuration)
```

If your custom class overrides `__init__()`, `setup()` or `loop()`, call super class method as the first statement in each method.

Super class will allow you to use some functions. Use only these bot values and functions. When implementing the algorithm in `Arduino` or some equivalent, these are the variables/function you have to implement. Implementing rest will be fairly easy.

| Variable/Function                       | Description                                                  |
| --------------------------------------- | ------------------------------------------------------------ |
| `self.bot`                              | Bot instance. Do not use movement methods or position variables not mentioned in this table. Use this to pass to some functions. |
| `self.img`                              | `numpy.array` containing current image. Any change made to this array (in-place) will be affected to the image drawn in the screen. |
| `self.bot.set_ball_color(color)`        | Sets ball color of the bot. `[blue, green, red]`             |
| `self.bot.no_of_squares_per_side`       | No of side squares in grid.                                  |
| `self.bot.cell_side_length`             | Length of one cell.                                          |
| `self.bot.groundSensor()`               | Get whether ground color is different. Currently tuned to yellow color. |
| `self.x`                                | X position of the bot*                                       |
| `self.y`                                | Y position of the bot*                                       |
| `self.direction`                        | Direction bot is facing*                                     |
| `self.start`                            | Start position*                                              |
| `self.waitDuration`                     | Standard milliseconds base class uses as timeout.            |
| `self.turnRight()`                      | Turns bot 90' right.                                         |
| `self.turnLeft()`                       | Turns bot 90' left.                                          |
| `self.goForward()`                      | Goes one cell forward.                                       |
| `self.go_to_right()`                    | Goes to right cell.                                          |
| `self.go_to_left()`                     | Goes to left cell.                                           |
| `self.go_backward()`                    | Goes to cell in the backward.                                |
| `self.is_wall_in_front()`               | Whether there is a wall in front.                            |
| `self.is_wall_in_right()`               | Whether there is a wall in right.                            |
| `self.is_wall_in_left()`                | Whether there is a wall in left.                             |
| `self.tile_in_the_direction(direction)` | The coordinate of the tile in the specified direction.       |
| `self.refresh_screen(img)`              | Refreshes screen                                             |
| `self.wait_for_user_key(timeout)`       | Waits timeout milliseconds and return the key pressed by user. |
| `self.sleep(timeout)`                   | Do nothing for timeout milliseconds.                         |
| `self.user_pressed_exit(timeout)`       | Exit if user pressed Esc in the timeout milliseconds.        |

*These values are not correct ones and are just integers which change when moving in directions. Correct positional variables are `bot._x` , `bot._y` and `bot._direction` but they are not know to the bot in a real life scenario, so avoid using them.

Furthermore,

- `setup` will run only once at the simulation initialization
- `loop` will run each time screen is updated(by default)
- You can force screen refresh by `self.refresh_screen(img)`, however note that additional `loop()` functions will not run at these forced refreshes
- If `loop()` returns `STOP_SIMULATION` value, simulation will stop. If it returns `RESUME_SIMULATION` or any other value(or `None`), loop will continue.
- Call `cv2.destroyAllWindows()` to close current window. However if not `STOP_SIMULATION` is issued, new refresh will cause a new window to load.

Since bot has no way of knowing some values in real world,

- Try not to use bot functions rather than basic movement and sensor
- Try not to use bot position variables such as `self.bot._x`, `self.bot._direction`
- It is OK to access `self.bot.cell_side_length` because it is known in most situations
- Try not to use settings values

### Optimized Custom Classes

All **optimized**`userscripts` should be defined in separate files in `optimized` folder. They have to be subclasses of `optimized_base_script.OptimizedUserScript`.

Optimized Classes have to use simple data structures as much as possible. First implement in normal Class and then switch to optimized one.

Sample custom class,

```python
import robot
from optimized import optimized_base_script

class OptimizedRightHandRule(optimized_base_script.OptimizedUserScript):
    def __init__(self, bot: robot.Robot):
        """Initialize"""
        super().__init__(bot)
        # initialize all your 'global' variables here to None
        # Try to use simple data types
        # eg:
        # self.center: int = None
        # self.grid: list = None

    def setup(self):
        super().setup()
        # Add all variable initialization and startup code
        # eg:
        # self.center = 54
        # self.grid = [0]*196

    def loop(self, img):
        super().loop(img)
        # Add loop code (handling robot)
        # Use below statements to allow users to exit by pressing 'Esc'
        self.user_pressed_exit(optimized_base_script.WAIT_DURATION)
```

There are few changes from normal classes. Other methods, variables are same.

| Variable/Function                       | Description                                                  |
| --------------------------------------- | ------------------------------------------------------------ |
| `self.SIDE_SQUARES`                     | No of side squares in grid. Do not use `self.bot.no_of_squares_per_side` |
| `self.pos`                              | Position of bot. This is an integer calculated using `X*SIDE_SQUARES + Y`. No `self.x`, `self.y` values. |
| `self.START`                            | Start position*. No `self.start` value.                      |
| `optimized_base_script.WAIT_DURATION`   | Standard milliseconds base class uses as timeout. No `self.waitDuration` value. |
| `self.tile_in_the_direction(direction)` | The position(instead of coordinates) of the tile in the specified direction. This will also be calculated using `X*SIDE_SQUARES + Y` |
| `self.sleep(timeout)`                   | Removed implementation.                                      |
| `self.get_x_coord(position)`            | Retrieve X coordinate from position. New implementation.     |
| `self.get_y_coord(position)`            | Retrieve Y coordinate from position. New implementation.     |
| `self.get_pos(x, y)`                    | Convert X, Y to a integer by `X*SIDE_SQUARES + Y`. New implementation. |

### Screenshots

![maze-solving-bot-simulator](readme/maze-solving-bot-simulator.png)

### Current Implementation

Uses `Flood Fill Algorithm` to find shortest path.
