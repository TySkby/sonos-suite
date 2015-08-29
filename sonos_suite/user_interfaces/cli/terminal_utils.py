"""Author credit: http://blog.taz.net.au/2012/04/09/getting-the-terminal-size-in-python/
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os


def get_terminal_size(default_height=25, default_width=80):
    """Get the current terminal height and width.

    Terminal dimensions will be determined in the following order,
    based on first successful determination:
        1. Try to get size via `termios.TIOCGWINSZ`
        2. Try to get size from environment
        3. Fall back to provided defaults

    :param default_height: The fallback height to return if all attempts to determine size fail
    :type default_height: int
    :param default_width: The fallback width to return if all attempts to determine size fail
    :type default_width: 25

    :return A two-tuple of integers in the form of (height, width)
    :rtype: (int, int)
    """

    # First try to get size via `termios.TICOCGWINSZ`
    try:
        import fcntl, termios, struct
        height, width = struct.unpack('hh', fcntl.ioctl(1, termios.TIOCGWINSZ, '1234'))
        return height, width
    except Exception as e:
        # TODO: Log based on config preferences
        logging.debug('Terminal size from termios.TIOCGWINSZ failed due to %s: %s', e.__class__.__name__, e)

    # Fall back to environment
    try:
        height, width = os.environ['LINES'], os.environ['COLUMNS']
        return height, width
    except Exception as e:
        # TODO: Log based on config preferences
        logging.debug('Terminal size from environment failed due to %s: %s', e.__class__.__name__, e)

    # Fall back to returning defaults
    return default_height, default_width


def fit_text_to_terminal(text, column_padding=2):
    """Given text, adds newline separators where necessary to preserve
    word boundaries so that no line of text contains more characters than
    the current terminal width with a negative `column_padding` offset.

    :param text: A single line of text which should be formatted into multiple lines as necessary
    :type text: str | unicode
    :param column_padding: Offset value for the column size.  Useful for adding a margin width to the column
        so that formatted lines of text do not completely fill the terminal width.
    :type column_padding: int

    :return: The given text, formatted with properly-placed line breaks
    :rtype: str | unicode
    """
    # Set the target maximum width of the text to return based on terminal size and requested margin width
    terminal_height, terminal_width = get_terminal_size()
    max_width = terminal_width - column_padding

    # Create an empty list, where each member will be one line of text with length less than or equal to max_width
    lines = []
    while len(text) > 0:
        # Of the remaining text, split into two parts:
        #   1. From the beginning of the string to max_width characters,
        #   2. The remainder of the text after max_width characters
        text_to_limit, remainder = text[:max_width], text[max_width:]
        if not remainder:
            # No remainder is present, so we are at the last line to format
            lines.append(text_to_limit)
            break
        else:
            # Split the text_to_limit at the rightmost space to prevent splitting words
            # Keep the tail of the partition to prepend back to the remainder of the original text split
            head, sep, tail = text_to_limit.rpartition(' ')
            if head:
                # Add the head of the word-bounded partition as a new line to our list of lines of text
                lines.append(head)
                # Prepend the tail back to the remainder as the tull remaining set of text to fit
                text = tail + remainder
            else:
                # No text remains to be formatted because we are left with an empty string
                break
    return '\n'.join(lines)
