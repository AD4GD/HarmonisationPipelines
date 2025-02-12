import os
import logging
import datetime
import subprocess

from modules.tools import basic_tool
from modules.utils.utils import is_path_abs


class RdfConvert(basic_tool.Tool):
    """
    Class that uses rdfconvert tool to generate serialize things in different rdf formats.
    """

    def __init__(self):
        super().__init__()
        self.directory = os.path.join('utils', 'rdfconvert')
        self.executable = 'bin/rdfconvert.sh'

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_rdfconvert_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def serialize_to_ttl(self, input_path, output_path):
        """
        Function for converting nt dump into ttl format.
        :param: input_path -> str
        :param: output_path -> str
        """
        self.logger.debug(f"{input_path=}")
        self.logger.debug(f"{output_path=}")
        cwd = os.getcwd()
        if is_path_abs(input_path):
            input_full_path = input_path
        else:
            input_full_path = os.path.join(cwd, input_path)
        if is_path_abs(output_path):
            output_full_path = output_path
        else:
            output_full_path = os.path.join(cwd, output_path)
        self.logger.debug(f"{input_full_path=}")
        self.logger.debug(f"{output_full_path=}")
        with open(self.log_path, 'wb') as log:
            p = subprocess.Popen([self.executable, '-o', '"Turtle"', input_full_path, output_full_path], shell=False,
                                 cwd=self.directory, stderr=log)
        p.communicate()
