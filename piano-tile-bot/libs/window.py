import win32gui


class Window:
    def __init__(self, window_title, title_bar=None, resolution=None):
        """
        Initializer for Window instances. Used for ScreenGrab
        :param window_title:title of the window to grab
        :param title_bar:title bar size (will cut it out)
        :param resolution:resolution of window(crop it to that size)
        """
        self.window_title = window_title
        self.hwnd = win32gui.FindWindow(None, window_title)
        self.rect = self.get_rect()

        # Get correct window size, cut title bar and use resolution to cut unnecessary parts
        if title_bar:
            self.rect[1] += title_bar
        if resolution:
            self.rect[2] = self.rect[0] + resolution[0]
            self.rect[3] = self.rect[1] + resolution[1]

    def bring_forward(self):
        """
        Bring the window to forward
        :return:None
        """
        win32gui.SetForegroundWindow(self.hwnd)

    def get_rect(self):
        """
        Get rectangle the window contains
        :return:None
        """
        rect = list(win32gui.GetWindowRect(self.hwnd))
        return rect
