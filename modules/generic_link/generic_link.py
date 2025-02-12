import os
import logging
import datetime

from modules.generic import generic
from modules.tools.silk.silk import Silk


class GenericLinking(generic.Generic):
    """
    Subclass of Generic that deals with linking tasks.
    """
    def __init__(self):
        super().__init__()
        self.config_path = None

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_generic_link'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def confirm_config(self):
        matches = []
        input_folder = os.path.join(self.results_dir, self.folder)
        for file in os.listdir(input_folder):
            if file.endswith(".xml"):
                matches.append(file)
        if len(matches) == 1:
            self.config_path = os.path.join(input_folder, matches[0])
        elif len(matches) > 1:
            msg = "Aborting... There is more than one xml file within the provided input. " \
                  "Tool is expecting one, and only one" \
                  " configuration file. Please fix it and re-run."
            self.logger.info(msg)
            self.logger.info(matches)
            raise SystemExit(msg)
        else:
            msg = "Aborting... Config file not found in the provided input. Tool is expecting" \
                  " a config file for linking process provided as an .xml file."
            self.logger.info(msg)
            raise SystemExit(msg)

    def process_linking(self):
        """
        Main function that performs linking.
        """
        linking_tool = Silk()
        linking_tool.generate_links(config_filepath=self.config_path)
