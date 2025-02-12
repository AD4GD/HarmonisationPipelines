import os
from urllib import request
import zipfile
import sys

from modules.progress_bar import progress_bar
from modules.lpis import lpis


class LpisWebZip(lpis.Lpis):
    """
    Subclass of Lpis class that deals with data provided as the zip package through the url.
    """
    def __init__(self, url, result_dir):
        """
        :param url: str -> url to the zip file.
        """
        super().__init__(result_dir=result_dir)
        self.url = url

    def fetch_data(self):
        """
        Function that downloads the data from the url and extracts the main content.
        """
        print('########## Fetching data...')
        os.makedirs(self.destination_path, exist_ok=True)
        filename = 'data.zip'
        filepath = os.path.join('temp', filename)
        request.urlretrieve(self.url, filepath, progress_bar.MyProgressBar())
        zip_file = None
        for dir_path, dir_names, filenames in os.walk('temp'):
            for filename in [f for f in filenames if f.endswith(".zip")]:
                zip_file = os.path.join(dir_path, filename)
        if zip_file:
            with zipfile.ZipFile(zip_file, 'r') as zip_target:
                zip_target.extractall(path=self.destination_path)
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
