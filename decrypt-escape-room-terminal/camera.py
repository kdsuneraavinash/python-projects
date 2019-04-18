import cv2
import numpy as np
import math
import ascii
import os
import imageprocess
import terminal
import shutil
from termcolor import colored, cprint

cap = None
def getCameraFrame(source=0):
    '''Returns camera video frame from video source'''

    global cap

    if cap is None:
        cap = cv2.VideoCapture(source)

    ret = False
    stuck_counter = 0
    while not ret:
        ret, frame = cap.read()
        stuck_counter += 1

        if stuck_counter > 300:
            # Stuck for 300 frames
            return None

    return frame


def getPhotoFrame(file='snapshot.jpeg'):
    '''Returns a photo from file'''

    return cv2.imread(file, 1)

exit_pressed = False
def signal_handler(signum, frame):
    global exit_pressed
    exit_pressed = True


def run_image_processor():
    '''Main Entry Point'''
    global exit_pressed
    exit_pressed = False

    terminal.set_handler(signal_handler)

    with open('cameraclue.txt', encoding="utf-8") as f:
        camera_clue = f.read()

    width = terminal.TERMINAL_WIDTH
    height = terminal.TERMINAL_HEIGHT - 10
    img_width = int(width*0.75)
    aspect_ratio = height/width
    
    while not exit_pressed:
        frame = getCameraFrame()

        if frame is None:
            # Frame lag - stop
            break

        frame, threshed, angle = imageprocess.process(frame)
        frame = cv2.rotate(threshed, cv2.ROTATE_90_COUNTERCLOCKWISE)

        if abs(angle - 45) < 8:
            art = camera_clue
            frame_color = 'white'
            color = 'green'
            attrs = ['bold', 'underline']
            art = art.split('\n')
        else:
            frame = np.pad(frame, pad_width=1, mode='constant', constant_values=0)
            art = ascii.frame_to_ascii_art(frame, img_width, aspect_ratio, ascii.gscale3)

            if angle == float("inf"):
                frame_color = 'yellow'
                color = 'white'
                attrs = ['bold', 'blink']
            else:
                frame_color = 'green'
                color = 'green'
                attrs = ['bold']
        
        art = terminal.center(art)
        text = "="*width + '\n'
        text += "Press CTRL+C to exit..\n"
        text += "="*width + '\n\n'
        text = terminal.center(text)
        text += "Output[]: " + colored(imageprocess.message_from_image_processor, color, attrs=attrs)
        text += "\n\n\n"
        art = text + colored(art, frame_color, attrs=['bold'])
        terminal.clear_terminal()
        print(art)

    try:
        cap.release()
        terminal.set_handler(terminal.handler)
    except:
        pass


if __name__ == '__main__':
    run_image_processor()
