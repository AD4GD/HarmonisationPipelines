import os
from urllib import request
import zipfile
import shutil
import logging
import datetime

from modules.progress_bar import progress_bar
from modules.fadn import fadn
from modules.utils.utils import url_extract_filename, set_folder_name_based_on_url


class WebZip(fadn.Fadn):
    """
    Subclass of Fadn that deals with data provided in the zip package through the url.
    """
    def __init__(self, results_dir, url):
        """
        :param url: str -> url to the zip file.
        """
        super().__init__(results_dir=results_dir)
        self.url = url
        self.filename = url_extract_filename(self.url)
        self.folder = None

    def set_folder_name(self):
        """
        Function that sets self.folder to the appropriate value based on the URL.
        """
        folder = set_folder_name_based_on_url(self.url)
        if folder:
            self.folder = folder
        else:
            self.folder = "fadn_data"   # fixed folder name in case it could not be derived from URL.

    def fetch_data(self, keep=False):
        """
        Function that downloads the data from the url and extracts the main content.
        :params keep: boolean -> if true the main zip file will not be deleted at the end of the
        process.
        """
        print('########## Fetching data...')
        os.makedirs(self.destination_path, exist_ok=True)
        file_path = os.path.join(self.destination_path, self.filename)
        request.urlretrieve(self.url, file_path, progress_bar.MyProgressBar())
        with zipfile.ZipFile(file_path, 'r') as zip_target:
            zip_target.extractall(self.destination_path)
        if not keep:
            os.remove(file_path)

    def unpack_all_packages(self, keep=False):
        """
        Function that unpacks all files inside main file.
        :params keep: boolean -> if true the auxiliary zip files will not be deleted at the end
        of the process.
        """
        print('########## Unpacking ZIP files...')
        for file in os.listdir(self.destination_path):
            if file.endswith(".zip"):
                file_name = os.path.join(self.destination_path, file)
                zip_ref = zipfile.ZipFile(file_name)
                zip_ref.extractall(self.destination_path)
                zip_ref.close()
                if not keep:
                    os.remove(file_name)
