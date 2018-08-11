import utils
import robot
import bot_scripts


def main():
    # Open Image File as a coloured image
    img = utils.openImage(bot_scripts.settingsImagePath)
    # Retrieve threshholded and filtered image
    threshholded = utils.applyVisionFilter(img)
    # Initialize Bot with startup settings
    bot = robot.Robot(x=bot_scripts.settingsStartX, y=bot_scripts.settingsStartY, direction=bot_scripts.settingsFaceDirection,
                    mazeMap=threshholded, side=len(img)//bot_scripts.settingsGridSideSquares)

    # Initialize user bot scripts
    src = bot_scripts.settingsSrcClass(bot)

    # Run setup
    src.setup()
    while True:
        # Refresh Screen
        utils.refreshScreen(img, bot)
        # Loop
        ret = src.loop(img)
        if ret == bot_scripts.STOP_SIMULATION:
            # If stop simulatio signal, Exit
            break


if __name__ == '__main__':
    main()
