import os
import sys
from os import path
from bear import version

LIB_PATH = path.split(__file__)[0]       # /xxx/xxx/bear/bear

PY_COMMAND = 1
EXE_COMMAND = 2

# 将vender文件夹 加入环境变量
ld_path = os.getenv('LD_LIBRARY_PATH')
if ld_path:
    ld_path = ':'.join([path.join(LIB_PATH, 'vendor'), ld_path])
else:
    ld_path = path.join(LIB_PATH, 'vendor')
os.putenv('LD_LIBRARY_PATH', ld_path)


# 形参加*表示接受一个tuple(元组)
def resource(*paths):
    return path.join(LIB_PATH, *paths)


def join_command(*cmds):
    return '-'.join(cmds)


# bear-xxx 优先检查py
def find_command(cmd):
    exefile = resource('core', join_command('bear', cmd))
    pyfile = exefile + '.py'

    if path.exists(pyfile):
        return PY_COMMAND, pyfile
    elif os.access(exefile, os.X_OK):
        return EXE_COMMAND, exefile
    else:
        return None, None


def exec_command(command, args):
    _type, _path = find_command(command)
    if _type == PY_COMMAND:
        # print('A={A}'.format(A=sys.executable))
        # print('B={B}'.format(B=_path))
        # print('C={C}'.format(C=args))
        os.execl(sys.executable, sys.executable, _path, *args)
        return True
    elif _type == EXE_COMMAND:
        os.execl(_path, _path, *args)
        return True
    else:
        return False


def main(argv=None):
    argv = argv or sys.argv

    def usage():
        print('see README.md')

    def exec_cmd(command, args):
        if not exec_command(command, args):
            print(command + ' command not found!')

    command = len(argv) > 1 and argv[1] or None

    if command == '--help' or command is None:
        usage()
    elif command == 'help':
        if len(argv) > 2:
            exec_cmd(argv[2], ['--help'])
        else:
            usage()
    elif command in ['version', '--version', '-v']:
        print(version.V)
    elif command == 'list':
        print(sys.executable, argv)
    else:
        exec_cmd(command, argv[2:])


if __name__ == '__main__':
    main()
