import math


class Progress:
    def __init__(self, width, percent=0):
        self.width = width
        self.percent = percent

    def set_percent(self, val):
        self.percent = val

    def __str__(self):
        w = self.width - 2
        sh = math.floor((self.percent / 100) * w)
        da = w - sh
        return "[" + "#" * sh + "-" * da + "]"


class Placeholder:
    def __init__(self, size, align="left", value=""):
        self.size = size
        self.value = value
        self.align = align

    def set_value(self, value):
        self.value = value

    def set_size(self, size):
        self.size = size

    def __str__(self):
        if self.align == "left":
            return "{0:{1}}".format(self.value, self.size)
        if self.align == "right":
            return "{0:>{1}}".format(self.value, self.size)


class Line:
    def __init__(self, *args):
        self.line = args

    def set_line(self, *args):
        self.line = args

    def get_line(self):
        return self.line

    def __str__(self):
        return "".join([str(x) for x in self.line])
