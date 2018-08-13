import numpy

import base_script
import robot


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

        # Refresh screen with img (to be passed to movement functions)
        def refresh():
            self.refresh_screen(img)

        if not self.is_wall_in_right():
            self.go_to_right(refresh)
        elif not self.is_wall_in_front():
            self.go_forward(refresh)
        elif not self.is_wall_in_left():
            self.go_to_left(refresh)
        else:
            self.go_backward(refresh)

        return self.user_pressed_exit(100)
