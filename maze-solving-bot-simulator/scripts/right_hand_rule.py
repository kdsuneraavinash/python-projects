import numpy

import robot
from datatypes import SimulationRunStatus
from scripts import base_script


class RightHandRule(base_script.UserScript):
    def __init__(self, bot: robot.Robot):
        """Initialize"""
        super().__init__(bot)

    # --------------------------------------------------------------
    # RUNNING ENTRY POINTS -----------------------------------------
    # --------------------------------------------------------------

    def setup(self):
        """Setup function"""
        super().setup()

    def loop(self, img: numpy.array) -> int:
        """Loop Function"""
        super().loop(img)

        # Refresh screen with img (to be passed to movement functions)
        while not self.is_ground_center():
            if not self.is_wall_in_right():
                self.go_to_right()
            elif not self.is_wall_in_front():
                self.go_forward()
            elif not self.is_wall_in_left():
                self.go_to_left()
            else:
                self.go_backward()

        return SimulationRunStatus.STOP_SIMULATION
