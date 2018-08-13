import robot
import scripts
import utils


def main():
    # Open Image File as a coloured image
    img = utils.open_image(scripts.settingsImagePath)
    # Retrieve filtered image
    walls = utils.apply_vision_filter(img)
    ground = utils.apply_ground_filter(img)
    # Initialize Bot with startup settings
    bot = robot.Robot(x=scripts.settingsStartX, y=scripts.settingsStartY,
                      direction=scripts.settingsFaceDirection, wall_map=walls,
                      ground_map=ground, side=len(img) // scripts.settingsGridSideSquares)

    # Initialize user bot scripts
    src = scripts.settingsSrcClass(bot)

    # Run setup
    src.setup()
    while True:
        # Refresh Screen
        utils.refresh_screen(img, bot)
        # Loop
        ret = src.loop(img)
        if ret == scripts.STOP_SIMULATION:
            # If stop simulation signal, Exit
            break


if __name__ == '__main__':
    main()
