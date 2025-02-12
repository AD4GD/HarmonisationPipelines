import os
import shutil
import logging
import datetime

from modules.fadn import fadn
from modules.utils.utils import is_path_abs, get_paths_normalized_basename


class FadnPostProcessor(fadn.Fadn):
    """
    Subclass of Fadn that performs post-processing tasks on the freshly created dumps.
    """
    def __init__(self, results_dir, handling_duplicates):
        """
        :param handling_duplicates: boolean -> If true the duplicates will be removed.
        """
        super().__init__(results_dir=results_dir)
        self.directory = os.path.join(self.results_dir, 'output', 'dumps')
        self.pp_duplicates = handling_duplicates
        self.dumps_directory = None

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_fadn_postprocessing_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def _set_dumps_directory(self):
        """
        Semi-private helper function that sets up absolute path to the directory that contain dumps.
        """
        cwd = os.getcwd()
        if is_path_abs(self.directory):
            self.dumps_directory = self.directory
        else:
            self.dumps_directory = os.path.join(cwd, self.directory)

    def run_postprocessor(self):
        """
        Function that executes all the post-processing actions on all dumps.
        """
        print('########## Post-processing dumps...')
        self._set_dumps_directory()
        for dump in os.listdir(self.dumps_directory):
            print(f'Currently post-processing {dump}...')
            location = os.path.join(self.dumps_directory, dump)
            os.makedirs(os.path.join(self.dumps_directory, 'pp'), exist_ok=True)
            destination = os.path.join(self.dumps_directory, 'pp', dump)
            list_of_bnodes = self._remove_empty_triples(location, destination)
            if self.pp_duplicates:
                os.makedirs(os.path.join(self.dumps_directory, 'pp_without_duplicates'), exist_ok=True)
                new_destination = os.path.join(self.dumps_directory, 'pp_without_duplicates', dump)
                self._remove_duplicates(destination, new_destination, list_of_bnodes)

    def _remove_duplicates(self, path, output_path, list_of_bnodes):
        """
        Private function that checks for duplicates and redundant triples and removes them from
        .nt file while storing potential information about duplicated lines in the log files.
        :param path: str -> path to the file that has to be processed.
        :param output_path: str -> path to the file to write into.
        :param list_of_bnodes: list -> list of blank nodes that are indicating that line should be removed.
        """
        unique_lines = set()
        with open(path, 'r') as f:
            with open(output_path, 'w') as o:
                for line in f:
                    if line not in unique_lines:
                        if not any(word in line for word in list_of_bnodes):
                            o.write(line)
                            unique_lines.add(line)
                    else:
                        filename = get_paths_normalized_basename(path)
                        self.logger.info(f'Duplicated line in file {filename}: {line}')

    def _remove_empty_triples(self, path, output_path):
        """
        Private function that checks for empty triples and removes them from .nt file while storing
        potential information about number of lines that were removed in the log files.
        :param path: str -> path to the file that has to be processed.
        :param output_path: str -> path to the file to write into.
        :returns list -> list of blank nodes.
        """
        empty_lines_counter = 0
        bnodes_to_be_removed = []   # list which stores all blank nodes that are indicating of redundant line.
        with open(path, 'r') as f:
            with open(output_path, 'w') as o:
                for line in f:
                    if '""^^' not in line:
                        if '<>' not in line:
                            o.write(line)
                        else:
                            words = line.split()
                            if words[0].startswith('_:'):
                                bnodes_to_be_removed.append(words[0])
                    else:
                        empty_lines_counter += 1
        filename = get_paths_normalized_basename(path)
        self.logger.info(f'The number of deleted empty lines in file {filename}: {empty_lines_counter}')
        self.logger.info(f'The list of blank nodes that are indicating lines that should be later removed:'
                         f'{*bnodes_to_be_removed,} in the file: {filename}')
        return bnodes_to_be_removed

    def clean_directories(self):
        """
        Function that manages redundant files and directories after the post-processing actions.
        """
        # Cleaning all the initial dumps
        for dump in os.listdir(self.dumps_directory):
            if dump.endswith(".nt"):
                os.remove(os.path.join(self.dumps_directory, dump))

        # Checking if 'pp_without_duplicates' directory exists
        pp_no_duplicates_folder = os.path.join(self.dumps_directory, 'pp_without_duplicates')
        pp_folder = os.path.join(self.dumps_directory, 'pp')
        if os.path.isdir(pp_no_duplicates_folder):
            shutil.rmtree(os.path.join(self.dumps_directory, 'pp'))
            for file in os.listdir(pp_no_duplicates_folder):
                shutil.move(os.path.join(pp_no_duplicates_folder, file), self.dumps_directory)
            os.rmdir(pp_no_duplicates_folder)   # deleting an empty folder all files were moved.
        else:
            for file in os.listdir(pp_folder):
                shutil.move(os.path.join(pp_folder, file), self.dumps_directory)
            os.rmdir(pp_folder)   # deleting an empty folder all files were moved.
