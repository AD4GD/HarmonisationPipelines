import os
import logging
import datetime
import re
import dateutil.parser
import shutil

from modules.lpis import lpis
from modules.utils.utils import is_path_abs, remove_duplicated_lines_from_dump, perform_standard_postprocessing


class LpisPostProcessor(lpis.Lpis):
    def __init__(self, configfile, results_dir):
        super().__init__(result_dir=results_dir)
        self.configfile = configfile
        self.layer_abbreviation = None

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_lpis_postprocess'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.propagate = False

    def _set_dumps_directory(self):
        """
        Semi-private helper function that sets up absolute path to the directory that contain dumps.
        """
        cwd = os.getcwd()
        if not is_path_abs(self.dumps_dir):
            self.dumps_dir = os.path.join(cwd, self.dumps_dir)

    def _run_general_postprocessing(self, dump):
        """
        Semi-private function that runs general post-processing logic to a dump.
        :param dump: str -> name of the dump that is being post-processed.
        """
        os.makedirs(os.path.join(self.dumps_dir, 'pp_specific'), exist_ok=True)
        input_path = os.path.join(self.dumps_dir, 'pp', dump)
        output_path = os.path.join(self.dumps_dir, 'pp_specific', dump)
        perform_standard_postprocessing(input_path=input_path, output_path=output_path, logger=self.logger)

    def _run_spain_postprocessing(self, dump):
        """
        Semi-private function that runs post-processing logic specific for LPIS Spain.
        :param dump: str -> name of the dump that is being post-processed.
        """
        os.makedirs(os.path.join(self.dumps_dir, 'pp_specific'), exist_ok=True)
        input_path = os.path.join(self.dumps_dir, 'pp', dump)
        output_path = os.path.join(self.dumps_dir, 'pp_specific', dump)
        with open(input_path, 'r') as f:
            with open(output_path, 'w') as o:
                for line in f:
                    if "<http://www.opengis.net/def/crs/EPSG/0/4258>" in line:
                        new_line = line.replace("<http://www.opengis.net/def/crs/EPSG/0/4258> ", "")
                        o.write(new_line)
                        self.logger.info(f"{line} was changed in the post-processing stage!")
                    else:
                        o.write(line)

    def _run_poland_postprocessing(self, dump):
        """
        Semi-private function that runs post-processing logic specific for LPIS Poland.
        :param dump: str -> name of the dump that is being post-processed.
        """
        os.makedirs(os.path.join(self.dumps_dir, 'pp_specific'), exist_ok=True)
        input_path = os.path.join(self.dumps_dir, 'pp', dump)
        output_path = os.path.join(self.dumps_dir, 'pp_specific', dump)
        regex_pattern = re.compile(r"\w{3}\s\w{3}\s\d{2}\s\d{2}:\d{2}:\d{2}\s\w+\s+\d{4}")
        with open(input_path, 'r') as f:
            with open(output_path, 'w') as o:
                for line in f:
                    potential_datetime = regex_pattern.findall(line)
                    if "<http://www.opengis.net/def/crs/EPSG/0/4326>" in line:
                        new_line = line.replace("<http://www.opengis.net/def/crs/EPSG/0/4326> ", "")
                        o.write(new_line)
                        self.logger.info(f"{line} was changed in the post-processing stage!")
                    elif potential_datetime:
                        if len(potential_datetime) == 1:
                            datetime_match = potential_datetime[0]
                            parsed_datetime = dateutil.parser.parse(datetime_match)
                            converted_datetime = parsed_datetime.strftime("%Y-%m-%d")
                            new_line = line.replace(datetime_match, converted_datetime)
                            o.write(new_line)
                            self.logger.info(f"{line} was changed in the post-processing stage!")
                        else:
                            self.logger.info(f"WARNING: The following line consists potentially of more than one"
                                        f" match for the datetime object!         {line}")
                            o.write(line)
                    else:
                        o.write(line)

    def _run_lithuania_lcl_postprocessing(self, dump):
        """
        Semi-private function that runs post-processing logic specific for LPIS Lithuania (LCL).
        :param dump: str -> name of the dump that is being post-processed.
        """
        os.makedirs(os.path.join(self.dumps_dir, 'pp_specific'), exist_ok=True)
        input_path = os.path.join(self.dumps_dir, 'pp', dump)
        output_path = os.path.join(self.dumps_dir, 'pp_specific', dump)
        with open(input_path, 'r') as f:
            with open(output_path, 'w') as o:
                for line in f:
                    if "<http://www.opengis.net/def/crs/EPSG/0/4326>" in line:
                        new_line = line.replace("<http://www.opengis.net/def/crs/EPSG/0/4326> ", "")
                        o.write(new_line)
                        self.logger.info(f"{line} was changed in the post-processing stage!")
                    else:
                        o.write(line)

    def _run_lithuania_efa_postprocessing(self, dump):
        """
        Semi-private function that runs post-processing logic specific for LPIS Lithuania (EFA).
        :param dump: str -> name of the dump that is being post-processed.
        """
        os.makedirs(os.path.join(self.dumps_dir, 'pp_specific'), exist_ok=True)
        input_path = os.path.join(self.dumps_dir, 'pp', dump)
        output_path = os.path.join(self.dumps_dir, 'pp_specific', dump)
        with open(input_path, 'r') as f:
            with open(output_path, 'w') as o:
                for line in f:
                    if "<http://www.opengis.net/def/crs/EPSG/0/4326>" in line:
                        new_line = line.replace("<http://www.opengis.net/def/crs/EPSG/0/4326> ", "")
                        o.write(new_line)
                        self.logger.info(f"{line} was changed in the post-processing stage!")
                    else:
                        o.write(line)

    def _run_lithuania_rpl_postprocessing(self, dump):
        """
        Semi-private function that runs post-processing logic specific for LPIS Lithuania (RPL).
        :param dump: str -> name of the dump that is being post-processed.
        """
        os.makedirs(os.path.join(self.dumps_dir, 'pp_specific'), exist_ok=True)
        input_path = os.path.join(self.dumps_dir, 'pp', dump)
        output_path = os.path.join(self.dumps_dir, 'pp_specific', dump)
        regex_pattern = re.compile(r"\w{3}\s\w{3}\s\d{2}\s\d{2}:\d{2}:\d{2}\s\w+\s+\d{4}")
        with open(input_path, 'r') as f:
            with open(output_path, 'w') as o:
                for line in f:
                    potential_datetime = regex_pattern.findall(line)
                    if "<http://www.opengis.net/def/crs/EPSG/0/4326>" in line:
                        new_line = line.replace("<http://www.opengis.net/def/crs/EPSG/0/4326> ", "")
                        o.write(new_line)
                        self.logger.info(f"{line} was changed in the post-processing stage!")
                    elif potential_datetime:
                        if len(potential_datetime) == 1:
                            datetime_match = potential_datetime[0]
                            parsed_datetime = dateutil.parser.parse(datetime_match)
                            converted_datetime = parsed_datetime.strftime("%Y-%m-%d")
                            new_line = line.replace(datetime_match, converted_datetime)
                            o.write(new_line)
                            self.logger.info(f"{line} was changed in the post-processing stage!")
                        else:
                            self.logger.info(f"WARNING: The following line consists potentially of more than one"
                                        f" match for the datetime object!         {line}")
                            o.write(line)
                    else:
                        o.write(line)

    def run_postprocessor(self):
        """
        Function that executes all the post-processing actions for the LPIS Pipeline.
        """
        print('########## Post-processing dumps...')
        self._set_dumps_directory()
        for dump in os.listdir(self.dumps_dir):
            print(f'Currently post-processing {dump}...')
            location = os.path.join(self.dumps_dir, dump)
            os.makedirs(os.path.join(self.dumps_dir, 'pp'), exist_ok=True)
            destination = os.path.join(self.dumps_dir, 'pp', dump)
            duplicates = remove_duplicated_lines_from_dump(input_path=location, output_path=destination)
            # logging all duplicated lines
            for duplicate in duplicates:
                self.logger.info(duplicate)
            self._run_general_postprocessing(dump)

    def clean_directories(self):
        """
        Function that manages redundant files and directories after the post-processing actions.
        """
        # Cleaning all the initial dumps
        for dump in os.listdir(self.dumps_dir):
            if dump.endswith(".nt"):
                os.remove(os.path.join(self.dumps_dir, dump))
        pp_folder = os.path.join(self.dumps_dir, 'pp')
        pp_specific_folder = os.path.join(self.dumps_dir, 'pp_specific')
        if os.path.isdir(pp_specific_folder):
            shutil.rmtree(pp_folder)
            for file in os.listdir(pp_specific_folder):
                shutil.move(os.path.join(pp_specific_folder, file), self.dumps_dir)
            os.rmdir(pp_specific_folder)   # deleting an empty folder all files were moved.
        else:
            self.logger.info(f"The following folder was not found but was expected: {pp_specific_folder}.")

