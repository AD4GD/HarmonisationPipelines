import re
import datetime
import os
from distutils.dir_util import copy_tree

import pandas as pd


class Fadn(object):
    """
    Parent class for every single stage in the FADN Pipeline.
    """
    def __init__(self, results_dir='results'):
        self.folder = None
        self.date = None
        self.year = None
        self.month = None
        self.day = None
        self.results_dir = results_dir
        self.destination_path = None

    def set_date(self):
        """
        Function that sets up date based on the information provided in the folder name.
        """
        reg = re.compile(r"\d{8}")   # using regex to parse date from string.
        matches = reg.findall(self.folder)
        if matches:
            string_date = matches[-1]   # grabbing the date as string.
            date = pd.to_datetime(string_date)  # converting string into datetime object.
        else:
            date = datetime.datetime.now()   # if date was not found in the folder name we will use current date.
        self.date = date
        self.year = date.year
        self.month = date.month
        self.day = date.day

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

