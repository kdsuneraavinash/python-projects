import robot
import settings
import utils
from datatypes import SimulationRunStatus


def main():
    # Open Image File as a coloured image
    img = utils.open_image(settings.settingsImagePath)
    # Retrieve filtered image
    walls = utils.apply_vision_filter(img)
    ground = utils.apply_ground_filter(img)
    # Initialize Bot with startup settings
    bot = robot.Robot(x=settings.settingsStartX, y=settings.settingsStartY,
                      direction=settings.settingsFaceDirection, wall_map=walls,
                      ground_map=ground, side=len(img) // settings.settingsGridSideSquares)

    # Initialize user bot scripts
    src = settings.settingsSrcClass(bot)

    # Run setup
    src.setup()
    while True:
        # Refresh Screen
        utils.refresh_screen(img, bot)
        # Loop
        ret = src.loop(img)
        if ret == SimulationRunStatus.STOP_SIMULATION:
            # If stop simulation signal, Exit
            break


if __name__ == '__main__':
    main()
