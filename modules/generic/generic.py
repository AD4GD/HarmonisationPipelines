import os
from distutils.dir_util import copy_tree

from modules.utils.utils import get_paths_normalized_basename


class Generic(object):
    """
    Parent class for every single stage in the Generic Pipeline.
    """
    def __init__(self):
        self.results_dir = 'results'
        self.folder = 'generic_data'
        self.preprocess_dir = 'preprocessed_data'
        self.postprocess_dir = 'postprocessed_data'
        self.mappings_dir = 'mappings'
        self.dumps_dir = 'dumps'

    def create_main_dir_for_storing_results(self):
        """
        Function that creates directory that stores all the results.
        """
        os.makedirs(self.results_dir, exist_ok=True)   # creates directory where all results will be stored.

    def copy_folder_to_destination(self, data_dir):
        """
        Function that copies directory containing input data to container directory storing data.
        :param data_dir: str -> name of the folder containing data.
        """
        if os.path.isabs(data_dir):
            self.folder = get_paths_normalized_basename(data_dir)
            new_folder = os.path.join(self.results_dir, self.folder)
            os.makedirs(new_folder, exist_ok=True)
            copy_tree(data_dir, new_folder)
        else:
            if not os.path.isdir(os.path.join(self.results_dir, data_dir)):
                new_folder = os.path.join(self.results_dir, data_dir)
                os.makedirs(new_folder, exist_ok=True)
                copy_tree(data_dir, new_folder)

    def copy_mapping_to_destination(self, data_dir):
        """
        Function that copies directory containing mappings to container directory storing data.
        :param data_dir: str -> name of the folder containing data.
        """
        if os.path.isabs(data_dir):
            self.mappings_dir = get_paths_normalized_basename(data_dir)
            new_folder = os.path.join(self.results_dir, self.mappings_dir)
            os.makedirs(new_folder, exist_ok=True)
            copy_tree(data_dir, new_folder)
        else:
            if not os.path.isdir(os.path.join(self.results_dir, data_dir)):
                new_folder = os.path.join(self.results_dir, data_dir)
                os.makedirs(new_folder, exist_ok=True)
                copy_tree(data_dir, new_folder)
