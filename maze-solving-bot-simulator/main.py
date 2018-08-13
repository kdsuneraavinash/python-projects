import bot_scripts
import robot
import utils


def main():
    # Open Image File as a coloured image
    img = utils.open_image(bot_scripts.settingsImagePath)
    # Retrieve filtered image
    walls = utils.apply_vision_filter(img)
    ground = utils.apply_ground_filter(img)
    # Initialize Bot with startup settings
    bot = robot.Robot(x=bot_scripts.settingsStartX, y=bot_scripts.settingsStartY,
                      direction=bot_scripts.settingsFaceDirection, wall_map=walls,
                      ground_map=ground, side=len(img) // bot_scripts.settingsGridSideSquares)

    # Initialize user bot scripts
    src = bot_scripts.settingsSrcClass(bot)

    # Run setup
    src.setup()
    while True:
        # Refresh Screen
        utils.refresh_screen(img, bot)
        # Loop
        ret = src.loop(img)
        if ret == bot_scripts.STOP_SIMULATION:
            # If stop simulation signal, Exit
            break


if __name__ == '__main__':
    main()
