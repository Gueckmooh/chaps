import os
import math


class StatusException(Exception):
    pass


class Element:
    AUTO = 0
    MAXIMIZED = 1
    FIXED = 2

    def __init__(self, value=None, *, width=0, fit=AUTO, name=None):
        self._fit = fit
        self._value = value
        if self._fit == Element.AUTO:
            self._width = len(str(self._value))
        else:
            self._width = width
        self._callbacks = []
        self._name = name

    def set_width(self, width):
        self._width = width

    def get_width(self):
        return self._width

    def set_value(self, value):
        self._value = value
        if self._fit == Element.AUTO:
            self._width = len(str(self._value))

    def get_value(self):
        return self._value

    def set_fit(self, fit):
        self._fit = fit

    def get_fit(self):
        return self._fit

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def __str__(self):
        return "{0:{1}s}".format(str(self._value), self._width)


class Progress(Element):
    def __init__(self, value=0, *, width=0, fit=Element.MAXIMIZED, name=None):
        super().__init__(value, width=width, fit=fit, name=name)

    def set_value(self, value):
        if value > 1:
            value = 1
        elif value < 0:
            value = 0
        self._value = value

    def __str__(self):
        w = self._width - 2
        sh = math.floor(self._value * w)
        da = w - sh
        return "[" + "#" * sh + "-" * da + "]"


class Piecewise_Progress(Element):
    def __init__(
        self,
        nb_pieces=0,
        value=[],
        *,
        width=0,
        fit=Element.MAXIMIZED,
        name=None
    ):
        super().__init__(value, width=width, fit=fit, name=name)
        print(nb_pieces)
        self._nb_pieces = nb_pieces
        self._value = [False for i in range(nb_pieces)]

    def set_value(self, id, value):
        if not isinstance(value, bool):
            raise StatusException("Value must be boolean")
        self._value[id] = value

    def set_all_values(self, value):
        for i in range(len(self._value)):
            self._value[i - 1] = value

    def __str__(self):
        w = self._width - 2
        r = w
        s = "["
        for i, v in enumerate(self._value, start=1):
            c = math.ceil if i % 2 == 0 else math.floor
            if i == self._nb_pieces:
                c = lambda _: r
            n = c(w / self._nb_pieces)
            r -= n
            if v:
                s += "#" * n
            else:
                s += "-" * n
        s += "]"
        return s


class Text(Element):
    LEFT = 0
    RIGHT = 1

    def __init__(
        self, value="", *, width=0, fit=Element.AUTO, name=None, align=LEFT
    ):
        super().__init__(value, width=width, fit=fit, name=name)
        self._align = align
        self._fmt = None
        self._fmt_args = []
        self._fmt_kwargs = []

    def get_width(self):
        if self._fit == Element.AUTO:
            args = [getattr(self, name) for name in self._fmt_args]
            kwargs = {}
            for name in self._fmt_kwargs:
                value = getattr(self, name)
                kwargs[name] = value
            self._width = len(self._fmt.format(*args, **kwargs))
        return self._width

    def set_fmt(self, fmt, *args, **kwargs):
        self._fmt = fmt
        for i, val in enumerate(args):
            name = "v{}".format(i)
            setattr(self, name, val)
            self._fmt_args += [name]
        for name in kwargs:
            setattr(self, name, kwargs[name])
            self._fmt_kwargs += [name]

    def __call__(self, *args, **kwargs):
        if self._fmt is None:
            raise StatusException(
                "You must give a format before giving values"
            )
        for i, val in enumerate(args):
            name = "v{}".format(i)
            setattr(self, name, val)
            self._fmt_args += [name]
        for name in kwargs:
            setattr(self, name, kwargs[name])
            self._fmt_kwargs += [name]

    def __str__(self):
        if self._fmt is None:
            return "{0:{1}s}".format(str(self._value), self._width)
        else:
            args = [getattr(self, name) for name in self._fmt_args]
            kwargs = {}
            for name in self._fmt_kwargs:
                value = getattr(self, name)
                kwargs[name] = value
            s = self._fmt.format(*args, **kwargs)
            return "{0:{1}s}".format(s, self._width)


class Status:
    def __init__(self, width=None, separator="", dynamic_width=False):
        self._elements = []
        self._elements_id = {}
        if not isinstance(separator, str):
            raise StatusException("Separator must be string")
        self._separator = separator
        if width is not None:
            self._width = width
        else:
            self._width, _ = os.get_terminal_size()
        self._line = ""
        self._dynamic_width = dynamic_width

    def add_element(self, element, name=None):
        if not isinstance(element, Element):
            raise StatusException("Only 'Element's can be added to Status")
        self._elements += [element]
        if name is not None:
            self._elements_id[name] = element
            setattr(self, name, element)

    def __add__(self, other: Element):
        self.add_element(other, name=other.get_name())
        return self

    def __iadd__(self, other):
        self.add_element(other, name=other.get_name())
        return self

    def get_elements(self):
        return self._elements

    def _update_width(self):
        if self._dynamic_width:
            self._width, _ = os.get_terminal_size()

    def build_line(self):
        self._update_width()
        available_space = self._width
        for elt in self._elements:
            if elt.get_fit() in [Element.AUTO, Element.FIXED]:
                available_space -= elt.get_width()
        available_space -= len(self._separator) * (len(self._elements) - 1)
        if available_space < 0:
            raise StatusException("There is not enough place to print line")
        m = [
            elt for elt in self._elements if elt.get_fit() == Element.MAXIMIZED
        ]
        for elt in m[:-1]:
            elt.set_width(math.floor(available_space / len(m)))
        for elt in m[-1:]:
            elt.set_width(math.ceil(available_space / len(m)))
        self._line = self._separator.join([str(elt) for elt in self._elements])

    def __str__(self):
        self.build_line()
        return self._line
