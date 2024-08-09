import os
import array
import fnmatch
import numpy as np
from bear import log, runtime, pathutil

DTYPE_LIMIT = {
    np.int16: (-(1 << 15), (1 << 15) - 1),
    np.int32: (-(1 << 31), (1 << 31) - 1),
    np.float32: (-1.0, 1.0),
}

TYPE = 'raw'
SAMPLE_RATE = 16000
BITS = 16
ENCODING = 'signed-integer'
ENDIAN = 'little-endian'
CHANNELS = 1

SUPPORTED_ENCODINGS = ['signed-integer', 'unsigned-integer', 'floating-point',
                       'a-law', 'u-law', 'mu-law', 'oki-adpcm', 'ima-adpcm',
                       'ms-adpcm', 'gsm-full-rate']


def sec2time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return int(h), int(m), s


# file read
def read_binary(file_path, data_type='f'):

    file = open(file_path, 'rb')
    # floatArray = array.array('f')  # float
    # floatArray = array.array('h')  # int16
    array_ = array.array(data_type)
    element_size = array_.itemsize
    array_len = int(os.path.getsize(file_path) / element_size)
    array_.fromfile(file, array_len)  # faster than struct.unpack
    np_array = None
    if data_type == 'f':
        np_array = np.empty(shape=array_len, dtype=np.float32)
    elif data_type == 'h':
        np_array = np.empty(shape=array_len, dtype=np.int16)
    for i in range(array_len):
        np_array[i] = array_[i]
    file.close()
    return np_array


# def write_binary(_array, file_path):
#     res_array = np.reshape(_array, [-1])


def file_to_list(file_path, mode='r', encoding='utf-8'):
    file_list = []
    with open(file_path, mode=mode, encoding=encoding) as f:
        for line in f:
            line = line.strip('\n')
            file_list.append(line)
    return file_list


def file_to_set(file_path, mode='r', encoding='utf-8'):
    file_set = set()
    with open(file_path, mode=mode, encoding=encoding) as f:
        for line in f:
            line = line.strip('\n')
            if len(line) > 0:
                file_set.add(line)
    return file_set


def file2set(file_path, mode='r', encoding='utf-8'):
    return file_to_set(file_path, mode, encoding)


def file2list(file_path, mode='r', encoding='utf-8'):
    return file_to_list(file_path, mode, encoding)


def file_to_dict(file_path, mode='r', encoding='utf-8', separator='\t'):
    file_dict = {}
    with open(file_path, mode, encoding=encoding) as fh:
        for line in fh:
            line = line.strip('\n')
            line_array = line.split(separator)
            if len(line_array) == 2:
                file_dict[line_array[0]] = line_array[1]
            elif len(line_array) == 1:
                file_dict[line_array] = 1
            else:
                log.e('line_array = 1.', 'line:', line)
    return file_dict


def file2dict(file_path, read_type='r', separator='\t'):
    return file_to_dict(file_path, read_type, separator)


def file_to_dict_id(file_path, read_type='r', separator='\t', replace_src=None, replace_des=None):
    file_dict = {}
    with open(file_path, read_type) as f:
        for li in f:
            line = li.strip('\n')
            line_array = line.split(separator)
            if len(line_array) == 2:
                if replace_src and replace_src:
                    file_dict[line_array[0].split('/')[-1].replace(replace_src, replace_des)] = line_array[1]
                else:
                    file_dict[line_array[0].split('/')[-1]] = line_array[1]
            else:
                log.e('line_array = 1.', 'li:', li, 'line:', line)
    return file_dict


def file_to_dict_index(file_path, read_type='r', separator='\t'):
    file_dict = {}
    with open(file_path, read_type) as f:
        index = 0
        for li in f:
            line = li.strip('\n')
            line_array = line.split(separator)
            if len(line_array) >= 1:
                file_dict[line_array[0]] = index
            else:
                log.e('line_array = 1.', 'li:', li, 'line:', line)
            index += 1
    return file_dict


# symbol_table_list = file_to_list(runtime.resource('res', 'symbol_table.txt'))
# symbol_table_list = [i for i in output_class.output_class_436_dict.keys()]


def first_index(data, func):
    """
    返回首个满足条件的index
    eg: first_index(head.data, lambda x: x == 32767)
    """
    for i in range(len(data)):
        if func(data[i]):
            return i
    return None


def mat_y_scale(mat, y_scale):

    if y_scale == 1:
        return mat
    else:
        tmp_mat = np.empty(shape=(mat.shape[0], mat.shape[1]*y_scale), dtype=mat.dtype)
        for i in range(mat.shape[1]):
            for j in range(y_scale):
                tmp_mat[:, i*y_scale+j] = mat[:, i]
        return tmp_mat


# check

def save_str_to_txt(_str, _file_path, _mode='a+', _encoding='utf-8'):
    fp = open(_file_path, mode=_mode, encoding=_encoding)
    fp.write(_str)
    fp.close()


def str2list(labels):
    res = []
    for la in list(labels):
        res.append(int(la))
    return res


# sort
def get_key(item):
    return item[1]


def sort(input_tuple):
    res = []
    for item in sorted(input_tuple, key=get_key):
        res.append(item)
    return res


def mk_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def wc_l(file_path):
    f = open(file_path)
    line_num = len(f.readlines())
    f.close()
    return line_num


#####################################

def gen_list(file_or_dir, glob=None):
    if not os.path.exists(file_or_dir):
        log.e(file_or_dir, 'not exists')
        return None
    if os.path.isdir(file_or_dir):
        iter = pathutil.all_files_in_dir(file_or_dir)
        if not glob:
            return list(iter)
        else:
            return [x for x in iter
                    if fnmatch.fnmatch(os.path.basename(x), glob)]
    if os.path.isfile(file_or_dir):
        return [file_or_dir]

    log.e(file_or_dir, 'is unsupported')


def split_key(line):
    if '\t' in line:
        return line.split('\t')
    else:
        _array = line.split(' ')
        key = _array[0]
        return [key, ' '.join(_array[1:])]


def path2utt(fp, postfix='wav'):
    utt = fp.split('/')[-1].split(f'.{postfix}')[0]
    return utt


def load_vocab(vocab_file):
    id2vocab = {}
    with open(vocab_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            char, idx = line.split()
            id2vocab[int(idx)] = char
    vocab = [0] * len(id2vocab)
    for idx, char in id2vocab.items():
        vocab[idx] = char
    return id2vocab, vocab


