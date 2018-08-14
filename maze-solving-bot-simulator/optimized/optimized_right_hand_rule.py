from optimized import optimized_base_script


class OptimizedRightHandRule(optimized_base_script.OptimizedUserScript):
    def __init__(self, bot):
        """Initializing"""
        super().__init__(bot)

    def setup(self):
        """Setup"""
        super().setup()

    def loop(self, img):
        """Loop"""
        super().loop(img)

        # Always go to the first path when looking clockwise from right hand side
        while not self.is_ground_center():
            if not self.is_wall_in_right():
                self.go_to_right()
            elif not self.is_wall_in_front():
                self.go_forward()
            elif not self.is_wall_in_left():
                self.go_to_left()
            else:
                self.go_backward()
