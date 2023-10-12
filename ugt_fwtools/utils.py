import datetime
import glob
import logging
import shutil
import stat
import pwd
import socket
import subprocess
import os
import re
from typing import Dict, Optional


def build_t(value: str) -> str:
    """Custom build type validator for argparse. Argument value must be of
    format 0x1234, else an exception of type ValueError is raised.
    >>> parser.add_argument('-b', type=built_t)
    """
    try:
        return "{0:04x}".format(int(value, 16))
    except ValueError:
        raise TypeError("Invalid build version: `{0}'".format(value))


def menuname_t(name: str) -> str:
    """XML name file name with distribution."""
    if not re.match(r'^L1Menu_\w+\-{1}d[0-9]{1,2}$', name):
        raise ValueError("not a valid menu name: '{name}'".format(**locals()))
    return name


def xmlname_t(name: str) -> str:
    """L1menu XML name tag."""
    if not re.match(r'^L1Menu_\w+', name):
        raise ValueError("not a valid menu name: '{name}'".format(**locals()))
    return name


def vivado_t(version: str) -> str:
    """Validates Xilinx Vivado version number."""
    if not re.match(r'^\d{4}\.\d{1}$', version):
        raise ValueError("not a xilinx vivado version: '{version}'".format(**locals()))
    return version


def ipbb_version_t(version: str) -> str:
    """Validates IPBB version number."""
    if not re.match(r'^\d\.\d\.\d+$', version):
        raise ValueError("not a valid IPBB version: '{version}'".format(**locals()))
    return version


def build_str_t(version: str) -> str:
    """Validates build number."""
    if not re.match(r'^0x[A-Fa-f0-9]{4}$', version):
        raise ValueError("not a valid build version: '{version}'".format(**locals()))
    return version


def year_str_t(year: str) -> str:
    """Validates build number."""
    if not re.match(r'^[0-9]{4}$', year):
        raise ValueError("not a valid year: '{year}'".format(**locals()))
    return year


def questasim_t(version: str) -> str:
    """Validates Questasim version."""
    if not re.match(r'^\d+\.\d{1}[a-z0-9_]{0,3}$', version):
        raise ValueError("not a valid Questasim version: '{version}'".format(**locals()))
    return version


def remove(filename: str) -> None:
    """Savely remove a directory, file or a symbolic link."""
    if os.path.isfile(filename):
        os.remove(filename)
    elif os.path.islink(filename):
        os.remove(filename)
    elif os.path.isdir(filename):
        shutil.rmtree(filename)


def read_file(filename: str) -> str:
    """Returns contents of a file.
    >>> read_file('spanish_inquisition.txt')
    'NO-body expects the Spanish Inquisition!\n'
    """
    with open(filename, "rt") as fp:
        return fp.read()


def template_replace(template: str, replace_map: dict, result: str) -> None:
    """Load template by replacing keys from dictionary and writing to result
    file. The function ignores VHDL escaped lines.

    Example:
    >>> template_replace('sample.tpl.vhd', {'name': "title"}, 'sample.vhd')

    """
    # Read content of source file.
    with open(template, "rt") as fp:
        lines = fp.readlines()
    # Replace placeholders.
    for key, value in list(replace_map.items()):
        for i, line in enumerate(lines):
            # Ignore VHDL comments
            if not line.strip().startswith('--'):
                lines[i] = line.replace(key, value)
    # Write content to destination file.
    with open(result, "wt") as fp:
        fp.write(''.join(lines))


def count_modules(menu: str) -> int:
    """Returns count of modules of menu. *menu* is the path to the menu directory."""
    pattern = os.path.join(menu, 'vhdl', 'module_*')
    return len(glob.glob(pattern))


def timestamp() -> str:
    """Returns ISO timestamp of curretn tiem and date."""
    return datetime.datetime.now().strftime("%Y-%m-%d-T%H-%M-%S")


def hostname() -> str:
    """Returns UNIX machine hostname."""
    return socket.gethostname()


def username():
    """Returns UNIX login name."""
    login = 0
    return pwd.getpwuid(os.getuid())[login]


def vivado_batch(source: str) -> None:
    subprocess.run(["vivado", "-mode", "batch", "-source", source, "-nojournal", "-nolog"]).check_returncode()


def colored(text: str, color: Optional[str] = None, on_color: Optional[str] = None, attrs: Optional[str] = None) -> str:
    """Colorize text using ANSI escape sequences."""
    COLORS = {
        'grey': '30', 'red': '31', 'green': '32', 'yellow': '33',
        'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37',
    }

    BACKGROUND_COLORS = {
        'on_grey': '40', 'on_red': '41', 'on_green': '42', 'on_yellow': '43',
        'on_blue': '44', 'on_magenta': '45', 'on_cyan': '46', 'on_white': '47',
    }

    ATTRIBUTES = {
        'bold': '1', 'dark': '2', 'underline': '4', 'blink': '5',
        'reverse': '7', 'concealed': '8',
    }

    if color is None and on_color is None and attrs is None:
        return text

    code_list = []

    if color:
        code_list.append(COLORS[color])
    if on_color:
        code_list.append(BACKGROUND_COLORS[on_color])
    if attrs:
        for attr in attrs:
            code_list.append(ATTRIBUTES[attr])

    codes = ";".join(code_list)
    return f"\033[{codes}m{text}\033[0m"


class ColoredFormatter(logging.Formatter):
    """Formatter to add colors to logging based on log levels."""
    COLORS = {
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
    }

    def format(self, record):
        log_message = super(ColoredFormatter, self).format(record)
        return colored(log_message, color=self.COLORS.get(record.levelname))


def get_colored_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Creates a default logger with colored output."""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():  # Prevent adding multiple handlers to the same logger
        ch = logging.StreamHandler()
        ch.setLevel(level)

        formatter = ColoredFormatter('%(levelname)s: %(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger