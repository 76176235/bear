import os
import sys
from multiprocessing import Pool


class MultiIO:
    def __init__(self, infile, jobs=10):
        self.jobs = jobs
        self.infile = infile
        self._processor = None

    def input_files_iter(self):
        self._in = open(self.infile, 'rt')
        for line in self._in:
            yield line.strip()

        self._in.close()
        self._in = None

    def _processor_wrapper(self, infile):
        return self._processor(self, infile)

    # 串行
    def _handle_list_serial(self):
        res_list = []
        for files_iter in self.input_files_iter():
            res_list.append(self._processor_wrapper(files_iter))
        return res_list

    # 并行
    def _handle_list_concurrently(self):
        files_iter = self.input_files_iter()
        with Pool(self.jobs) as p:
            res_list = p.map(self._processor_wrapper, files_iter)
        return res_list

    def run(self, processor=None, saver=None):

        # 4.对列表进行批处理
        self._processor = processor

        if self.jobs > 1:
            res_list = self._handle_list_concurrently()
        else:
            res_list = self._handle_list_serial()

        if res_list is None or \
                (isinstance(res_list, list) and
                 all(map(lambda x: x is None, res_list))):
            return

        if saver:
            saver(self, res_list)
        else:
            return res_list


class MultiIOCommand:

    def __init__(self, parser):
        # 3.对对象进行解析
        self.args = parser.parse_args()
        # self.io_args = _IOWrapper(self.args)
        self._processor = None
        # self.files_list = []
        self.files_iter = None
        self._in = None
        self.multi_mode = True
        self.filepath = None

    def input_files_iter(self):
        if self.filepath and os.path.basename(self.filepath) == 'bear-parse.py' and self.args.mode == 'rasr':
            self._in = open(self.args.infile, 'rt', encoding='latin1')
        else:
            self._in = open(self.args.infile, 'rt')

        for line in self._in:
            yield line.strip()

        self._in.close()
        self._in = None

    def _processor_wrapper(self, infile):
        return self._processor(self, infile)

    # 串行
    def _handle_list_serial(self):

        res_list = []
        for files_iter in self.input_files_iter():
            res_list.append(self._processor_wrapper(files_iter))
        return res_list

    # 并行
    def _handle_list_concurrently(self):

        files_iter = self.input_files_iter()

        with Pool(self.args.jobs) as p:
            res_list = p.map(self._processor_wrapper, files_iter)
        return res_list

    def run(self, filepath=None, processor=None, saver=None):
        if filepath:
            self.filepath = filepath
        # 4.对列表进行批处理
        self._processor = processor or sys.modules['__main__']._process_input_file

        if self.args.jobs > 1:
            res_list = self._handle_list_concurrently()
        else:
            res_list = self._handle_list_serial()

        if res_list is None or \
                (isinstance(res_list, list) and
                 all(map(lambda x: x is None, res_list))):
            # if 'version' in self.args:
            #     if self.args.version == 'minis2':
            #         aec_minis2.aec_minis2_end()
            #     elif self.args.version == 'cm601':
            #         aec_cm601.aec_cm601_end()
            return

        if not saver and hasattr(sys.modules['__main__'], '_save_results'):
            saver = sys.modules['__main__']._save_results
        if saver:
            saver(self, res_list)

