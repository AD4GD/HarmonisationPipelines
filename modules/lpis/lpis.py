import os
from distutils.dir_util import copy_tree


class Lpis(object):
    """
    Parent class for every single stage in the LPIS Pipeline.
    """
    def __init__(self, result_dir='results'):
        self.results_dir = result_dir
        self.mappings_dir = os.path.join(self.results_dir, 'mappings')
        self.dumps_dir = os.path.join(self.results_dir, 'output', 'dumps')
        self.destination_path = None
        self.folder = 'lpis_data'
        self.list_of_input_files = []

    def create_list_of_input_files(self):
        """
        Function that creates list of input files based on the amount of shapefiles that were found in the
        data directory.
        """
        for subdir, dirs, files in os.walk(self.destination_path):
            for file in files:
                if file.endswith(".shp"):
                    full_file_path = os.path.join(subdir, file)
                    self.list_of_input_files.append(full_file_path)

    def create_main_dir_for_storing_results(self):
        """
        Function that creates directory that stores all of the results.
        """
        os.makedirs(self.results_dir, exist_ok=True)   # creates directory where all results will be stored.

    def set_destination_path(self):
        """
        Function that sets up full path to the destination data folder.
        """
        self.destination_path = os.path.join(self.results_dir, self.folder)

    def copy_folder_to_destination(self):
        """
        Function that moves directory containing input data to container directory "results".
        """
        if not os.path.isdir(self.destination_path):
            if not os.path.isdir(os.path.join(self.results_dir, self.folder)):
                new_folder = os.path.join(self.results_dir, self.folder)
                os.makedirs(new_folder)
                copy_tree(self.folder, new_folder)
