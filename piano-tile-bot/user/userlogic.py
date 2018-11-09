from libs.imageprocess import colorfilters, basic, draw, detection


def filter_black(original):
    img = basic.convert_image(original, "RGB", "HSV")
    mask = colorfilters.get_mask(img, (255, 255, 20), (0, 0, 0))
    return mask


def filter_custom(original):
    img = basic.convert_image(original, "RGB", "HSV")
    mask_black = colorfilters.get_mask(img, (255, 255, 20), (0, 0, 0))
    mask_light_blue = colorfilters.get_mask(img, (30, 190, 255), (20, 185, 0))
    yellow_mask = colorfilters.get_mask(img, (100, 255, 255), (50, 0, 200))
    mask_blue = colorfilters.get_mask(img, (20, 255, 500),  (10, 150, 0))
    mask = mask_blue | mask_light_blue | mask_black | yellow_mask
    return mask


def detect_line(img, y_axis, min_len=50, max_gap=15):
    arr = img[y_axis]
    current_gap = 0
    line_start = None
    lines = []

    px = 0
    for px in range(len(arr)):
        if line_start:  # line started
            if not arr[px]:  # but pixel is black
                current_gap += 1  # gap is increased
                if current_gap > max_gap:  # gap is huge
                    if px - line_start > min_len:  # line is bigger than min_len
                        lines.append([[line_start, y_axis, px - max_gap, y_axis]])  # line is over
                    line_start = None  # no line again
        else:
            if arr[px]:  # pixel is white
                line_start = px  # a line is starting
    else:
        if line_start and px - line_start > min_len:  # last line is a big one
            lines.append([[line_start, y_axis, px, y_axis]])  # line is over

    mid = [[None, None] for _ in range(len(lines))]
    for i in range(len(lines)):
        mid[i] = [int((lines[i][0][0] + lines[i][0][2]) / 2), y_axis]
    return lines, mid


def draw_lines_and_dots(img, lines, dots, line_c, dot_c, dot_size=10):
    for line in lines:
        draw.lines(img, line, color=line_c)
    for dot in dots:
        draw.circle(img, dot, dot_size, color=dot_c, thickness=-1)


def load_templates():
    template0 = basic.load_image(r"templates\template0.jpg", 0)
    template1 = basic.load_image(r"templates\template1.jpg", 0)
    return [template0, template1]


def detect_buttons(img, templates):
    """
    Next play button detecting algorithm.
    Working.
    Abandoned because bored.
    """
    t_empty, t_play = templates
    img_bw = basic.convert_image(img, "RGB", "GRAY")
    p_empty = detection.template_matching(img_bw, [t_empty], 0.95, True)
    p_play = detection.template_matching(img_bw, [t_play], 0.95)
    
    p_buttons = {}
    for p0 in p_empty:
        for p1 in p_buttons:
            if abs(p0[1] - p1[1]) < 20:
                break
        else:
            p_buttons[p0] = None
    
    for p0 in p_play:
        for p1 in p_buttons:
            if abs(p0[1] - p1[1]) < 20:
                if p_buttons[p1] is None:
                    p_buttons[p1] = p0
                break

    inf_button = (9999, 9999)
    p_top_button = inf_button
    if len(p_buttons) > 0:
        for p_e in p_buttons:
            p_p = p_buttons[p_e]
            if p_p is None:
                continue
            if p_p[1] < p_top_button[1]:
                p_top_button = p_p
    
    if p_top_button != inf_button:
        p_top_button = p_top_button[0] + 75, p_top_button[1] + 38
        draw.circle(img, p_top_button, 10, (0, 0, 0), 5)
