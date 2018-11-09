import time

import numpy as np

from libs import window, keycontrol, screengrab
from libs.imageprocess import draw
from user import userlogic

# Initially 60fps Image grab
# Drawing will cause fps loss 40fps
# Playing will cause fps loss 5fps
is_draw = False
is_play = True


def calc():
    print("Avg. fps :", s / c)


def decision_taker_0(img):
    """
    Line algorithm. Basically detects black line in a
    masked image along a given y axis and click on middle
    of every line.
    Since it can't click 2 places at once, this is not ideal.
    
    *Score by this algorithm 1500+
    *Hard to reach reach 2000s
    """
    fil = userlogic.filter_black(img)
    y_axis1 = 500
    lines1, all_points = userlogic.detect_line(fil, y_axis1)

    if is_draw:
        userlogic.draw_lines_and_dots(img, lines1, all_points, (0, 255, 0), (0, 0, 255))
        for point in all_points:
            draw.circle(img, point, 20, color=(255, 255, 255))

    if is_play:
        for point in all_points:
            keycontrol.click(point)

    return [img]


def decision_taker_1(img):
    """
    Sensor Algorithm. Places 8 Sensors on the screen and picks up
    image parts and mask them (thus increasing performance) and
    calculate mean and use it to identify whether on not to touch
    that lane. If can touch, use WASD key map (set in virtual player)
    to give input. (Thus enabling multi-touch.
    
    *Score by this algorithm 5000+
    *Can reach hugh scores
    *Recorded max 6678
    """
    h, _ = img.shape[:2]

    area = [[0] * 2 for _ in range(4)]
    final = [0] * 4
    key_codes = [0x11, 0x1E, 0x1F, 0x20]
    key_threshold = 100

    xs = [140 * i + 15 for i in range(4)]
    ys = [100 * j + 300 for j in range(2)]

    for i in range(4):
        x1 = xs[i]
        x2 = x1 + 20
        for j in range(2):
            y1 = ys[j]
            y2 = y1 + 20

            area[i][j] = userlogic.filter_custom(img[y1:y2, x1:x2])
            area[i][j] = int(np.mean(area[i][j]))

            if is_draw:
                color = (0, 255, 0) if area[i][j] > key_threshold else (0, 0, 255)
                draw.rectangle(img, (x1, y1), (x2, y2), color, -1)
                pos = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                draw.text(img, str(area[i][j]), pos, 1, (100, 100, 100))

        if area[i][1] > key_threshold and area[i][0] > key_threshold:
            final[i] = 1

    if is_draw:
        draw.text(img, str(dict(zip(list("WASD"), final))), (50, 100), 1, (50, 50, 50), 5)

    if is_play:
        for i in range(4):
            if final[i]:
                keycontrol.direct_x_press_key(key_codes[i])
            else:
                keycontrol.direct_x_release_key(key_codes[i])
    return [img]


def process(img):
    return decision_taker_1(img)


if __name__ == '__main__':
    try:
        game_window = window.Window("NoxPlayer", 40)
        game = screengrab.ScreenGrab(game_window, process)
        print("PIANO TILES BOT")
        print()
        print("Drawing:", is_draw, "\tPlaying:", is_play)
        print()
        print("Bot caught the window")
        c = s = 0
        for t in range(3):
            print("Bot starting in {} seconds".format(2 - t))
            time.sleep(1)
        print("Bot Started... Press Ctrl+C to exit")
        while True:
            t = time.time()
            game.get_next_frame(True, debug_displays=is_draw)
            s += 1 / (time.time() - t)
            c += 1
    except Exception as e:
        print("Oopsie...", e, sep="\n")
