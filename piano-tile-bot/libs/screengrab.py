import win32api
import win32gui
import win32ui

import cv2
import numpy as np
import win32con
from PIL import ImageGrab


class ScreenGrab:
    def __init__(self, window, frame_process=None):
        """
        Initialize Screen Grab instance
        :param window:Window instance to grab
        :param frame_process:function to use for calculations
        """
        self.window = window
        self.rect = window.rect

        if not frame_process:
            self.frame_process = lambda x: x
        else:
            self.frame_process = frame_process

    def get_next_frame(self, show=False, can_exit=True, exit_key=ord('q'), debug_displays=1, grab_function="default"):
        """
        Get the next frame. Use in a while loop. This will internally call specified frame_process
        :param show:boolean; whether to show result of frame_process. Can cause significant fps drops.
        :param can_exit:boolean; whether user can exit by a key press
        :param exit_key:Key to press for exit (only useful iff can_exit is true)
        :param debug_displays:no of debug displays. must be less than or equal to returns of frame_process.
        :param grab_function:grab function to use. 'default' is fast. ImageGrab is also an option
        :return: unprocessed frames
        """
        # Grab Frames by specified function
        if grab_function == "ImageGrab":
            frame = ImageGrab.grab(bbox=self.rect)
        else:
            frame = self.grab()

        # Use given frame processing function to process frame
        frames = self.frame_process(frame)

        # If should show debug windows, show them
        if show:
            for i in range(debug_displays):
                cv2.imshow('Display %d' % i, frames[i])

            # If can exit, exit when pressed exit_key(ASCII)
            if can_exit and (cv2.waitKey(25) & 0xFF == exit_key):
                cv2.destroyAllWindows()
                raise SystemExit()

        return frames

    def grab(self):
        """
        Fast grab function - sentdex method
        :return:image
        """
        hwin = win32gui.GetDesktopWindow()
        if self.rect:
            left, top, x2, y2 = self.rect
            width = x2 - left + 1
            height = y2 - top + 1
        else:
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

        hwindc = win32gui.GetWindowDC(hwin)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)
        memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

        signed_ints_array = bmp.GetBitmapBits(True)
        img = np.fromstring(signed_ints_array, dtype='uint8')
        img.shape = (height, width, 4)

        srcdc.DeleteDC()
        memdc.DeleteDC()
        win32gui.ReleaseDC(hwin, hwindc)
        win32gui.DeleteObject(bmp.GetHandle())
        return img
