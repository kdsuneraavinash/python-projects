import signal
import os
import time
import progressbar
import struct

DEBUG = True
TERMINAL_WIDTH = 140
TERMINAL_HEIGHT = 55

def center(s):
    if type(s) is str:
        s = s.split('\n')
    s = [i.strip().center(TERMINAL_WIDTH) for i in s]
    s = "\n".join(s) + '\n'
    return s

#=======================================================
def handler(signum, frame):
    pass

def set_handler(h):
    signal.signal(signal.SIGINT, h)
    signal.signal(signal.SIGTSTP, h)

set_handler(handler)

#=======================================================

def clear_terminal():
    os.system('tput reset')

#=======================================================

def show_progress(wait, progress):
    for i in progressbar.progressbar(range(100)):
        if i > progress:
            print()
            break
        time.sleep(wait)

