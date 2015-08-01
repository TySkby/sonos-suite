"""Author credit: http://blog.taz.net.au/2012/04/09/getting-the-terminal-size-in-python/
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os


def get_terminal_size(fd=1):
    """
    Returns height and width of current terminal. First tries to get
    size via termios.TIOCGWINSZ, then from environment. Defaults to 25
    lines x 80 columns if both methods fail.

    :param fd: file descriptor (default: 1=stdout)
    """
    try:
        import fcntl, termios, struct
        hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    except:
        try:
            hw = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            hw = (25, 80)

    return hw


def get_terminal_height(fd=1):
    """
    Returns height of terminal if it is a tty, 999 otherwise

    :param fd: file descriptor (default: 1=stdout)
    """
    if os.isatty(fd):
        height = get_terminal_size(fd)[0]
    else:
        height = 999

    return height


def get_terminal_width(fd=1):
    """
    Returns width of terminal if it is a tty, 999 otherwise

    :param fd: file descriptor (default: 1=stdout)
    """
    if os.isatty(fd):
        width = get_terminal_size(fd)[1]
    else:
        width = 999

    return width


def fit_text_to_terminal(text, column_padding=2):
    cols = get_terminal_width() - column_padding
    lines = []
    while len(text) > 0:
        text_to_limit, remainder = text[:cols], text[cols:]
        if not remainder:
            lines.append(text_to_limit)
            break
        else:
            head, sep, tail = text_to_limit.rpartition(' ')
            if head:
                lines.append(head)
                text = tail + remainder
            else:
                break
    return '\n'.join(lines)
