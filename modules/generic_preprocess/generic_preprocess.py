import logging
import datetime
import os
import shutil
import json

import pandas as pd
import xarray as xr

from modules.generic import generic
from modules.utils.utils import identify_delimiter, is_valid_zip, extract_zip_with_delete, copy_dir, adjust_crs


class GenericPreprocess(generic.Generic):
    """
    Subclass of Generic that deals with pre-processing tasks.
    """
    def __init__(self):
        super().__init__()
        self.temporary_dir = "temporary"

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_generic_preprocess'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def _set_index_column(self, df):
        """
        Semi-private function that adds a column called seq which will be treated as an index
        in the csv output. By design the Pandas indexing starts from 0 and, the desired output is
        starting from 1 though.
        :param df: Pandas DataFrame object.
        """
        try:
            df.insert(0, 'seq', range(1, 1 + len(df)))
        except ValueError:
            self.logger.info("Could not create a seq column, perhaps it already exists in the CSV file.")

    def add_sequential_column(self, chained=False):
        """
        Performs pre-processing task of adding a sequential column in the CSV file.
        :param chained: boolean -> if True, the function will expect to find input files in pre-processed folder,
        otherwise the function will act as this is the first pre-processing action.
        """
        if chained:
            target = os.path.join(self.results_dir, self.temporary_dir)
            destination = os.path.join(self.results_dir, self.preprocess_dir)
        else:
            target = os.path.join(self.results_dir, self.preprocess_dir)
            destination = os.path.join(self.results_dir, self.folder)
        os.makedirs(target, exist_ok=True)
        no_csv_provided = True  # variable that keeps track if there was at least one csv file provided.
        for subdir, dirs, files in os.walk(destination):
            for file in files:
                if file.endswith(".csv"):
                    no_csv_provided = False
                    print(f"Currently processing {file}...")
                    csv_full_path = os.path.join(subdir, file)
                    self.logger.debug(f"{csv_full_path=}")
                    delimiter = identify_delimiter(csv_full_path)
                    self.logger.debug(f"{delimiter=}")
                    df = pd.read_csv(csv_full_path, sep=delimiter)
                    self._set_index_column(df)
                    output_full_path = os.path.join(target, file)
                    self.logger.debug(f"{output_full_path=}")
                    df.to_csv(output_full_path, index=False)
                else:
                    self.logger.info(f"Sorry, only CSV files are suitable for add_seq_col!"
                                     f" Preprocessing of {file} aborted.")
        if no_csv_provided:
            msg = "No csv files were found in the directory, omitting the add_sequential_column" \
                  " step!"
            self.logger.info(msg)
            print(msg)
            if not chained:
                self.logger.debug(f"{destination=}")
                self.logger.debug(f"{target=}")
                copy_dir(from_dir=destination, to_dir=target)
            else:
                os.rmdir(target)
        else:
            self._prune_temporary_folder()

    def normalize_delimiter(self, chained=False):
        """
        Performs pre-processing task of normalizing a delimiter in the CSV file.
        :param chained: boolean -> if True, the function will expect to find input files in pre-processed folder,
        otherwise the function will act as this is the first pre-processing action.
        """
        if chained:
            target = os.path.join(self.results_dir, self.temporary_dir)
            destination = os.path.join(self.results_dir, self.preprocess_dir)
        else:
            target = os.path.join(self.results_dir, self.preprocess_dir)
            destination = os.path.join(self.results_dir, self.folder)
        os.makedirs(target, exist_ok=True)
        no_csv_provided = True  # variable that keeps track if there was at least one csv file provided.
        for subdir, dirs, files in os.walk(destination):
            for file in files:
                if file.endswith(".csv"):
                    no_csv_provided = False
                    print(f"Currently processing {file}...")
                    csv_full_path = os.path.join(subdir, file)
                    self.logger.debug(f"{csv_full_path=}")
                    delimiter = identify_delimiter(csv_full_path)
                    self.logger.debug(f"{delimiter=}")
                    df = pd.read_csv(csv_full_path, sep=delimiter)
                    output_full_path = os.path.join(target, file)
                    self.logger.debug(f"{output_full_path=}")
                    df.to_csv(output_full_path, sep=",", index=False)
                else:
                    self.logger.info(f"Sorry, only CSV files are suitable for normalize_delimiter!"
                                     f" Preprocessing of {file} aborted.")
        if no_csv_provided:
            msg = "No csv files were found in the directory, omitting the normalize_delimiter" \
                  " step!"
            self.logger.info(msg)
            print(msg)
            if not chained:
                self.logger.debug(f"{destination=}")
                self.logger.debug(f"{target=}")
                copy_dir(from_dir=destination, to_dir=target)
            else:
                os.rmdir(target)
        else:
            self._prune_temporary_folder()

    def unzip_multiple_inputs(self):
        """
        Function that iterates through data directory and unzip all archives into this directory.
        """
        target = os.path.join(self.results_dir, self.preprocess_dir)
        destination = os.path.join(self.results_dir, self.folder)
        no_zipfiles_provided = True   # variable that keeps track if there was at least one zip file provided.
        for subdir, dirs, files in os.walk(destination):
            for file in files:
                full_file_path = os.path.join(subdir, file)
                if is_valid_zip(full_file_path):
                    extract_zip_with_delete(path_to_zip=full_file_path, extract_to=target)
                    no_zipfiles_provided = False
        if no_zipfiles_provided:
            msg = "No valid zip archives were found in the directory, omitting the unzip_multiple_inputs" \
                  " step!"
            self.logger.info(msg)
            print(msg)
            copy_dir(from_dir=destination, to_dir=target)
        else:
            shutil.rmtree(destination)

    def project_crs(self, chained=False):
        """
        Function that adjusts shapefiles crs.
        """
        if chained:
            target = os.path.join(self.results_dir, self.temporary_dir)
            destination = os.path.join(self.results_dir, self.preprocess_dir)
        else:
            target = os.path.join(self.results_dir, self.preprocess_dir)
            destination = os.path.join(self.results_dir, self.folder)
        os.makedirs(target, exist_ok=True)
        no_shp_provided = True  # variable that keeps track if there was at least one csv file provided.
        for subdir, dirs, files in os.walk(destination):
            for file in files:
                if file.endswith(".shp"):
                    no_shp_provided = False
                    print(f"Currently processing {file}...")
                    shp_full_path = os.path.join(subdir, file)
                    output_full_path = os.path.join(target, file)
                    adjust_crs(input_path=shp_full_path, output_path=output_full_path, logger=self.logger)
        if no_shp_provided:
            msg = "No shp files were found in the directory, omitting the normalize_delimiter" \
                  " step!"
            self.logger.info(msg)
            print(msg)
            if not chained:
                copy_dir(from_dir=destination, to_dir=target)
            else:
                os.rmdir(target)
        else:
            self._prune_temporary_folder()

    def add_enum(self, chained=False):
        """
        Performs pre-processing task of adding enum field to JSON file.
        :param chained: boolean -> if True, the function will expect to find input files in pre-processed folder,
        otherwise the function will act as this is the first pre-processing action.
        """
        if chained:
            target = os.path.join(self.results_dir, self.temporary_dir)
            destination = os.path.join(self.results_dir, self.preprocess_dir)
        else:
            target = os.path.join(self.results_dir, self.preprocess_dir)
            destination = os.path.join(self.results_dir, self.folder)
        os.makedirs(target, exist_ok=True)
        no_json_provided = True  # variable that keeps track if there was at least one csv file provided.
        for subdir, dirs, files in os.walk(destination):
            for file in files:
                if file.endswith(".json"):
                    no_json_provided = False
                    print(f"Currently processing {file}...")
                    json_full_path = os.path.join(subdir, file)
                    with open(json_full_path, 'r') as json_file:
                        data = json.load(json_file)
                    if isinstance(data, list):
                        data = [{"id": i, **d} for i, d in enumerate(data)]
                        output_full_path = os.path.join(target, file)
                        with open(output_full_path, 'w') as output_json:
                            json.dump(data, output_json, indent=4)
                    else:
                        msg = "Exiting... Structure of provided JSON file is incompatible with add_enum task. " \
                              "It is expected to be a list of items!"
                        self.logger.info(msg)
                        raise SystemExit(msg)

                else:
                    self.logger.info(f"Sorry, only JSON files are suitable for add_enum!"
                                     f" Preprocessing of {file} aborted.")
        if no_json_provided:
            msg = "No JSON files were found in the directory, omitting the add_enum" \
                  " step!"
            self.logger.info(msg)
            print(msg)
            if not chained:
                copy_dir(from_dir=destination, to_dir=target)
            else:
                os.rmdir(target)
        else:
            self._prune_temporary_folder()

    def convert_netcdf_to_csv(self, chained=False):
        """
        Performs pre-processing task of converting netcdf into csv.
        """
        if chained:
            target = os.path.join(self.results_dir, self.temporary_dir)
            destination = os.path.join(self.results_dir, self.preprocess_dir)
        else:
            target = os.path.join(self.results_dir, self.preprocess_dir)
            destination = os.path.join(self.results_dir, self.folder)
        os.makedirs(target, exist_ok=True)
        no_netcdf_provided = True  # variable that keeps track if there was at least one csv file provided.
        for subdir, dirs, files in os.walk(destination):
            for file in files:
                if file.endswith(".nc"):
                    no_netcdf_provided = False
                    print(f"Currently processing {file}...")
                    netcdf_full_path = os.path.join(subdir, file)
                    self.logger.debug(f"{netcdf_full_path=}")
                    file_base = os.path.basename(file)
                    output_full_path = os.path.join(target, f"{os.path.splitext(file_base)[0]}.csv")
                    self.logger.debug(f"{output_full_path=}")
                    DS = xr.open_dataset(netcdf_full_path)
                    DS.to_dataframe().to_csv(output_full_path)
        if no_netcdf_provided:
            msg = "No netcdf files were found in the directory! Exiting..."
            self.logger.info(msg)
            raise SystemExit(msg)
        else:
            self._prune_temporary_folder()

    def _prune_temporary_folder(self):
        """
        Helper function for cleaning, deleting and moving files from temporary directory to the pre-processed
        directory.
        """
        temporary_dir = os.path.join(self.results_dir, self.temporary_dir)
        target_dir = os.path.join(self.results_dir, self.preprocess_dir)
        self.logger.debug(f"{temporary_dir=}")
        self.logger.debug(f"{target_dir=}")
        if os.path.isdir(temporary_dir):
            self.logger.debug(f"pruning {temporary_dir}")
            shutil.rmtree(target_dir)
            os.makedirs(target_dir, exist_ok=True)
            copy_dir(from_dir=temporary_dir, to_dir=target_dir)
            shutil.rmtree(temporary_dir)
