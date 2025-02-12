import subprocess
import os
import logging
import datetime

from modules.tools import basic_tool
from modules.utils.utils import is_path_abs


class Silk(basic_tool.Tool):
    """
    Class that uses Silk tool to generate links.
    """

    def __init__(self):
        super().__init__()
        self.directory = os.path.join('utils', 'silk')
        self.executable = 'silk-tools/silk-singlemachine/target/scala-2.12/Silk SingleMachine-assembly-3.1.0-SNAPSHOT.jar'

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_silk_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def generate_links(self, config_filepath):
        """
        Function for generating links using silk tool.
        """
        self.detect_system()
        cwd = os.getcwd()
        if is_path_abs(config_filepath):
            config = config_filepath
        else:
            config = os.path.join(cwd, config_filepath)
        with open(self.log_path, 'wb') as log:
            p = subprocess.Popen(['java', f'-DconfigFile={config}', '-jar', self.executable], shell=False,
                                 cwd=self.directory, stdout=log, stderr=log)
        p.communicate()
