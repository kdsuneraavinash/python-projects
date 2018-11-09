import ctypes
import win32api

import pyautogui

SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dxExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dxExtraInfo", PUL)]


class InputI(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", InputI)]


def direct_x_press_key(hex_key_code):
    """
    Press a directX key. Important for games that use directX
    :param hex_key_code: Enter key code
    :return: None
    """
    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.ki = KeyBdInput(0, hex_key_code, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def direct_x_release_key(hex_key_code):
    """
    Release a directX key. Important for games that use directX
    :param hex_key_code: Enter key code
    :return: None
    """
    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.ki = KeyBdInput(0, hex_key_code, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def key_check():
    """
    Method to get pressed keys by user.
    Author: https://github.com/Box-Of-Hats
    :return: pressed keys list
    """
    keys = []
    key_list = ["\b"] + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789,.'£$/\\")
    for key in key_list:
        if win32api.GetAsyncKeyState(ord(key)):
            keys.append(key)
    return keys


def click(position=None, interval=0.0):
    """
    Click on  a position on screen.
    :param position:position to click, if None will click where the mouse is.
    :param interval:interval between click and release
    :return:None
    """
    if position:
        x, y = position
    else:
        x = y = None

    pyautogui.click(x, y, interval=interval)


if __name__ == '__main__':
    while True:
        print(key_check())
