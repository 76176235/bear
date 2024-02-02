import os
import shutil
import fnmatch
import itertools
import sys
from bear import log

_cached_dirs = set()


class Node:

    @staticmethod
    def from_list_file(list_file, dir='.', check_exist=True):
        root = Node(dir=dir, auto_detect=False)

        with open(list_file) as f:
            for line in f:
                # log.v('line', line)
                segs = line.strip().split(os.path.sep)
                cur = root
                for s in segs:
                    if s in cur._nodedict:
                        cur = cur._nodedict[s]
                    else:
                        cur = cur._add(s, auto_detect=False)
                        if check_exist and not os.path.exists(cur.path):
                            raise Exception('%s not exists' % cur.path)
        return root

    def __init__(self, dir='.', name=None, auto_detect=True):
        # log.v('Node', dir, name)
        self.dir = dir
        self.name = name
        self.path = os.path.join(dir, name) if name else self.dir
        self.isdir = os.path.isdir(self.path)
        self.subnodes = []
        self._nodedict = {}
        self._mark = None
        if auto_detect and self.isdir:
            for n in os.listdir(self.path):
                self._add(n)

    def _add(self, name, auto_detect=True):
        sub = Node(self.path, name, auto_detect=auto_detect)
        self.subnodes.append(sub)
        self._nodedict[name] = sub
        return sub

    def iter_all(self):
        for sub in self:
            if sub.isdir:
                yield from sub.all()
            else:
                yield sub

    def mark(self, mark=True):
        self._mark = mark

    def marked(self, mark=True):
        return self._mark == mark

    def iter_marked(self, mark=True):
        for sub in self:
            if sub.isdir:
                yield from sub.iter_marked(mark)
            elif sub.marked(mark):
                yield sub

    def iter_unmarked(self, mark=True):
        for sub in self:
            if sub.isdir:
                yield from sub.iter_unmarked(mark)
            elif sub._mark != mark:
                yield sub

    def at(self, subpath):
        if os.path.sep not in subpath:
            return self._nodedict[subpath]
        else:
            return self._rgetitem(subpath.split(os.path.sep))

    def _rgetitem(self, keys):
        ns = [self]
        for k in keys:
            if k == '' or k == '.':
                continue
            elif k == '..':
                ns.pop()
            else:
                ns.append(ns[-1][k])
        return ns[-1]

    def __eq__(self, other):
        return self.path == other.path or \
            (os.path.exists(self.path) and
             os.path.exists(other.path) and
             os.path.samefile(self.path, other.path))

    def __len__(self):
        return len(self.subnodes)

    def __getitem__(self, key):
        if itertools.islice(key):
            return self.subnodes[key]
        if isinstance(key, tuple):
            return self._rgetitem(key)
        if isinstance(key, str):
            return self._nodedict[key]
        elif isinstance(key, int):
            return self.subnodes[key]
        else:
            raise TypeError('Node indices must be slices, tuples, '
                            'strings or integers')

    def __iter__(self):
        return self.subnodes.__iter__()


def idof(path):
    return os.path.splitext(os.path.basename(path))[0]


def valid_name(dir_path, name):
    full_path = os.path.join(dir_path, name)
    if not os.path.exists(full_path):
        return full_path
    i = 1
    while True:
        p1 = '%s%d' % (full_path, i)
        if not os.path.exists(p1):
            return p1
        i += 1


def open_at(path, mode='wb', check_dir=True):
    global _cached_dirs

    if not os.path.exists(path):
        head, _ = os.path.split(path)
        if len(head) > 0 and (check_dir or head not in _cached_dirs):
            _cached_dirs.add(head)
            os.makedirs(head, exist_ok=True)
    elif os.path.isdir(path):
        log.e(path, 'exists and is a directory')
    elif 'w' in mode:
        log.w(path, 'exists')

    return open(path, mode)


def strip(path, n):
    if not n:
        return path
    i, start = 0, -1
    while i < n:
        if start >= len(path):
            return ''
        idx = path.find(os.path.sep, start + 1)
        if idx != start + 1:
            i += 1
        start = idx

    return path[start + 1:]


def write_to(data, file, mode='wb', return_file=False, check_dir=True):
    if isinstance(file, str):
        file = open_at(file, mode=mode, check_dir=check_dir)
    ret = file.write(data)
    file.flush()
    if ret != len(data):
        log.e(
            'wrote %d bytes to %s, expect %d bytes' %
            (ret, file.name, len(data)))
    if return_file:
        file.seek(0)
        return file, ret
    else:
        file.close()
        return ret


def move(src, dest, ignore=None):
    subpath = src[len(ignore):]
    while subpath.startswith(os.path.sep):
        subpath = subpath[1:]
    dest_path = os.path.join(dest, subpath)
    os.makedirs(os.path.split(dest_path)[0], exist_ok=True)
    shutil.move(src, dest_path)
    return subpath


def basename(path):
    while path.endswith(os.path.sep):
        path = path[:-1]
    bn = os.path.split(path)[1]
    return bn if len(bn) > 0 else None


def path_id(path):
    return os.path.splitext(basename(path))[0]


def match(globs, path):
    if not globs or len(globs) == 0:
        return True
    for glob in globs:
        if fnmatch.fnmatch(os.path.basename(path), glob):
            return True

    return False


def all_files_in_dir(path='.', recursively=True,
                     execlude_dir_prefixes=['.', '\\']):
    # https://docs.python.org/3/whatsnew/3.3.html#pep-380
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isdir(file_path) and recursively:
            if execlude_dir_prefixes is not None:
                if any(map(lambda x: file_name.startswith(x),
                           execlude_dir_prefixes)):
                    continue
            yield from all_files_in_dir(file_path, True)
        else:
            yield file_path


def input_files_iter(file):
    # for line in input_files_iter_sub(file):
    #     yield line
    for line in file:
        yield line.strip()
    file.close()


def guess_ext(dir_path, hints=None, strong=False):
    first = None
    for file_path in all_files_in_dir(dir_path):
        _, ext = os.path.splitext(file_path)
        if len(ext) == 0:
            continue
        if hints is None or len(hints) == 0:
            return ext
        if first is None:
            first = ext
        if ext in hints:
            return ext

    if strong:
        raise Exception(
            'there is no file has extension %s at %s' %
            (hints, dir_path))
    return first


def target_file_path(cmd, infile_path, effect_name):
    """
    target = outdir/effect_name/infile_path
    """

    dest = os.path.join(cmd.args.outdir, effect_name)
    target = os.path.join(dest, infile_path)
    return target


def file_to_list(file_path, read_type='r'):
    '''
    Read the files in the form of list.
    :param file_path:
    :param read_type:
    :return:
    '''
    file_list = []
    with open(file_path, read_type) as f:
        for line in f:
            line = line.strip()
            file_list.append(line)
    return file_list


def filelist_to_dict(file_path, read_type='r'):
    file_dict = {}
    with open(file_path, read_type) as f:
        for line in f:
            line = line.strip()
            file_dict[os.path.basename(line)] = line
    return file_dict


###############################################################

def _is_std(path):
    return path == '-' or path == ''


def _is_dir(path):
    # should be only used to check infile
    return not _is_std(path) and os.path.isdir(path)


def _std_in(mode):
    return sys.stdin.buffer if mode == 'b' else sys.stdin


def _std_out(mode):
    return sys.stdout.buffer if mode == 'b' else sys.stdout


def try_guess_globs(io_args, hints=None):
    args = io_args._args
    assert args.globs is None

    if hints is None or len(hints) == 0:
        return
    if isinstance(hints, str):
        hints = [hints]
    if not _is_dir(args.infile):
        return

    ext = guess_ext(args.infile, hints, True)
    log.v('guessed glob is \'*%s\'' % ext)
    args.globs = ['*' + ext]


def all_files_read_from(file):
    for line in file:
        yield line.strip()
