import os
import sys
import logging
from datetime import datetime

_outfile = sys.stdout


class BColors:
    # https://stackoverflow.com/a/287944
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NONE = ''


_TAGS = ('[V]', '[I]', '[N]', '[W]', '[E]')
_COLORS = (
    BColors.NONE,
    BColors.NONE,
    BColors.OKGREEN,
    BColors.WARNING,
    BColors.FAIL)
_level = 1


def _log(level, *args, end, tag):
    if level < _level:
        return
    if tag:
        tag_str = _TAGS[level]
        tag_str += ' [%d]' % os.getpid()
        tag_str += datetime.now().strftime(' [%m-%d %X.%f] | ')
    else:
        tag_str = ''
    color = _COLORS[level]

    args = args[0]
    output = None
    if len(args) == 0:
        output = tag_str
    elif len(args) == 1:
        output = ' '.join([tag_str, str(args[0])])
    else:
        args = list(map(str, args))
        args.insert(0, tag_str)
        output = ' '.join(args)
    if color != BColors.NONE and sys.stdout.isatty():
        _outfile.write(color + output + BColors.ENDC + end)
    else:
        _outfile.write(output + end)
    return output


def set_outfile(file):
    global _outfile
    _outfile = file or sys.stdout


def set_level(level):
    global _level
    _level = level
    _log(0, ('set log level', level), end='end\n', tag=True)


env_level = os.getenv('BEAR_LOG_LEVEL')
if env_level is not None:
    set_level(int(env_level))


def v(*args, end=' end\n', tag=True):
    return _log(0, args, end=end, tag=tag)


def i(*args, end=' end\n', tag=True):
    return _log(1, args, end=end, tag=tag)


def n(*args, end=' end\n', tag=True):
    return _log(2, args, end=end, tag=tag)


def w(*args, end=' end\n', tag=True):
    return _log(3, args, end=end, tag=tag)


def e(*args, end=' end\n', tag=True):
    output = _log(4, args, end=end, tag=tag)
    raise Exception(output or ' '.join(args))
