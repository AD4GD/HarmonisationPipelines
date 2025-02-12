import os
import logging
import datetime
import subprocess

from modules.tools import basic_tool
from modules.utils.utils import is_path_abs, get_paths_normalized_basename


class RmlMapper(basic_tool.Tool):
    """
    RmlMapper class inherits from the basic mapper and handles all the tasks connected to the RmlMapper tool.
    """
    def __init__(self):
        """
        Class that uses Rmlmapper tool to transform data.
        """
        super().__init__()
        self.directory = os.path.join('utils', 'rmlmapper', 'target')
        # executable suitable for container image
        self.executable = 'rmlmapper-7.0.0-r373-all.jar'
        self.java_exec = "/usr/lib/jvm/java-17-openjdk-amd64/bin/java"

        # local executable just for testing on local machine
        # self.executable = 'rmlmapper-6.3.0-r369-all.jar'
        # self.java_exec = "java"


        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_rmlmapper_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def generate_dumps(self, input_data, dump_path):
        """
        Function that generates dumps based on mappings and data using RMLmapper tool.
        :param input_data: str -> single mapping file or directory containing multiple mapping files.
        :param dump_path: str -> filename or directory for the output data.
        """
        cwd = os.getcwd()
        if is_path_abs(input_data):
            input_full_path = input_data
        else:
            input_full_path = os.path.join(cwd, input_data)
        if is_path_abs(dump_path):
            dumps_full_path = dump_path
        else:
            dumps_full_path = os.path.join(cwd, dump_path)
        if os.path.isfile(input_full_path):
            if input_full_path.endswith('.ttl'):
                print(f'Creating output using {get_paths_normalized_basename(input_full_path)}...')
                with open(self.log_path, 'wb') as log:
                    p = subprocess.Popen([self.java_exec, '-Xmx2048m', '-jar', self.executable, '-m', f'"{input_full_path}"',
                                          '-o', f'"{dumps_full_path}"', '-v'], cwd=self.directory,
                                         stderr=log, stdout=log)
                p.communicate()
            else:
                print('Invalid mapping type!!! Expected .ttl files!')
        elif os.path.isdir(input_full_path):
            for file in os.listdir(input_full_path):
                if file.endswith('.ttl'):
                    print(f'Creating output using {file}...')
                    filename = os.path.splitext(file)[0]
                    full_filepath = os.path.join(input_full_path, file)
                    full_dump_path = os.path.join(dumps_full_path, filename)
                    with open(self.log_path, 'wb') as log:
                        p = subprocess.Popen([self.java_exec, '-Xmx2048m', '-jar', self.executable, '-m', f'"{full_filepath}"',
                                              '-o', f'"{full_dump_path}.nt"', '-v'], cwd=self.directory,
                                             stderr=log, stdout=log)
                    p.communicate()
                else:
                    print('Invalid mapping type!!! Expected .ttl files!')
