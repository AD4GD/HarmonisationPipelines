import os
from urllib import request
import zipfile
import sys
import shutil

from modules.progress_bar import progress_bar
from modules.generic import generic
from modules.utils.utils import get_paths_normalized_basename


class GenericWebZip(generic.Generic):
    """
    Subclass of Generic class that deals with data provided as the zip package through the url.
    """
    def __init__(self, url):
        """
        :param url: str -> url to the zip file.
        """
        super().__init__()
        self.url = url

    def fetch_data(self, data_stage):
        """
        Function that downloads the data from the url and extracts the main content.
        :param: data_stage: str -> single choice from: (initial_data, mappings, dumps, rules_file).
        :return destination folder.
        """
        if data_stage == "initial_data" or data_stage == "netcdf_transform":
            # destination = self.folder
            destination = os.path.join(self.results_dir, self.folder)
        elif data_stage == "mappings":
            # destination = self.mappings_dir
            destination = os.path.join(self.results_dir, self.mappings_dir)
        elif data_stage == "dumps":
            # destination = self.dumps_dir
            destination = os.path.join(self.results_dir, self.dumps_dir)
        elif data_stage == "rules_file":
            destination = self.results_dir
        else:
            print("Data stage input not recognized. Quiting...")
            sys.exit()
        if os.path.exists(destination) and data_stage != "rules_file":
            shutil.rmtree(destination)
        os.makedirs(destination, exist_ok=True)
        filename = 'data.zip'
        filepath = os.path.join('temp', filename)
        request.urlretrieve(self.url, filepath, progress_bar.MyProgressBar())
        zip_file = None
        for dir_path, dir_names, filenames in os.walk('temp'):
            for filename in [f for f in filenames if f.endswith(".zip")]:
                zip_file = os.path.join(dir_path, filename)
        if zip_file:
            with zipfile.ZipFile(zip_file, 'r') as zip_target:
                zip_target.extractall(path=destination)
            if data_stage == "rules_file":
                return destination
            else:
                return get_paths_normalized_basename(destination)
        else:
            print('WARNING: failed to unpack files! System did not find any suitable ZIP file.'
                  ' Please make sure that the URL you provided points to a ZIP file!')
            sys.exit()

    @staticmethod
    def remove_zip():
        """
        Function that removes zip file after the data is extracted.
        """
        target_dir = 'temp'
        for file in os.listdir(target_dir):
            if file.endswith(".zip"):
                os.remove(os.path.join(target_dir, file))
