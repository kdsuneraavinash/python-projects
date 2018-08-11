import cv2

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