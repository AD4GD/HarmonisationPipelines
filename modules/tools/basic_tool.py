import platform


class Tool(object):
    """
    Parent class for every single mapper introduced in the service.
    """
    def __init__(self):
        self.system = platform.system()
        self.windows = None
        self.unix = None
        self.directory = None

    def detect_system(self):
        """
        Function that detects operating system and sets class attributes respectively.
        """
        if self.system == 'Windows':
            self.windows = True
            self.unix = False
        elif self.system == 'Linux' or self.system == 'Darwin':
            self.windows = False
            self.unix = True
