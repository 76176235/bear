import os
import argparse
from bear import base

AUDIO = argparse.ArgumentParser(conflict_handler='resolve', add_help=False)
AUDIO.add_argument('-r', '--rate', nargs='?', default=base.SAMPLE_RATE, type=int)
AUDIO.add_argument('-b', '--bits', nargs='?', default=base.BITS, type=int)
AUDIO.add_argument(
    '-c',
    '--channels',
    nargs='?',
    default=base.CHANNELS,
    type=int)
AUDIO.add_argument('-t', '--type', nargs='?', default='wav', choices=['pcm', 'wav'])
AUDIO.add_argument('-B', '--big-endian', action='store_true')
AUDIO.add_argument('-e', '--encoding', nargs='?', default=base.ENCODING,
                   choices=base.SUPPORTED_ENCODINGS)
AUDIO.add_argument('--ext', nargs='?', const='.wav', default='.wav')

IO = argparse.ArgumentParser(conflict_handler='resolve', add_help=False)
IO.add_argument('-i',
                '--infile',
                nargs='?',
                default='-',
                help='input file, must is list')
IO.add_argument('-o',
                '--outdir',
                nargs='?',
                # default='-',
                default='outdir',
                help='output dir, default is outdir')

IO.add_argument('-a',
                '--add',
                nargs='?',
                # default='-',
                default='',
                help='output file name add string, default is checked')

# AUDIO.add_argument('-fle', '--fl-encoding', nargs='?', default='utf-8')

MIO = argparse.ArgumentParser(
    conflict_handler='resolve',
    add_help=False,
    parents=[IO])
MIO.add_argument('-g', '--globs', nargs='*')
# MIO.add_argument('--as-list', action='store_true') # 已经全部改为list形式输入

CONC = argparse.ArgumentParser(conflict_handler='resolve', add_help=False)
CONC.add_argument('-j', '--jobs', nargs='?', const=os.cpu_count(), default=1, type=int)
CONC.add_argument('-d', '--debug-level', nargs='?', const=0, default=1, type=int)
# CONC.add_argument('--log')


def parse_inherit(program=None, parents=[AUDIO, MIO, CONC]):
    # 1.创建解析对象并选择继承参数
    _ArgumentParser = argparse.ArgumentParser(prog=program, parents=parents)
    return _ArgumentParser
