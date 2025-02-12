import logging
import os
import datetime
import subprocess
import rdflib

from modules.tools import basic_tool
from modules.utils.utils import is_path_abs, get_paths_normalized_basename, change_field_value_in_json_and_save_file


class CSV2RDF(basic_tool.Tool):
    """
    Class that uses CSV2RDF tool to generate dumps.
    """

    def __init__(self):
        super().__init__()
        self.directory = os.path.join('utils', 'csv2rdf')
        self.executable = './csv2rdf'

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_csv2rdf_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def run_csv2rdf(self, input_json, input_csv, output_dir):
        """
        Function that runs csv2rdf to generate mappings.
        :param input_json: json file
        :param input_csv: path to csv file
        :param output_dir: str
        """
        cwd = os.getcwd()
        if is_path_abs(input_csv):
            input_csv_full_path = input_csv
        else:
            input_csv_full_path = os.path.join(cwd, input_csv)
        if is_path_abs(input_json):
            input_json_full_path = input_json
        else:
            input_json_full_path = os.path.join(cwd, input_json)
        input_filename = os.path.splitext(get_paths_normalized_basename(input_json))[0]
        self._modify_path_inside_json(path_to_json=input_json_full_path, full_path_to_csv=input_csv_full_path)
        output_full_path = os.path.join(cwd, output_dir, f"{input_filename}.ttl")
        with open(self.log_path, 'wb') as log:
            p = subprocess.Popen([self.executable, '-u', input_json_full_path, '-o', output_full_path], shell=False,
                                 cwd=self.directory, stderr=log)
        p.communicate()
        ntriples_output_full_path = os.path.splitext(output_full_path)[0] + '.nt'
        self._serialize_to_ntriples(input_path=output_full_path, output_path=ntriples_output_full_path)

    @staticmethod
    def _serialize_to_ntriples(input_path, output_path):
        """
        Helper function for serializing a graph as a turtle.
        :param input_path: str
        :param output_path: str
        """
        g = rdflib.Graph()
        g.parse(input_path)
        with open(output_path, 'w') as f:
            f.write(g.serialize(format='nt'))
        os.remove(input_path)

    @staticmethod
    def _modify_path_inside_json(path_to_json, full_path_to_csv, field_name="url"):
        """
        Helper function for making correction to csv path that is reference inside json file.
        :param path_to_json: str
        :param full_path_to_csv: str
        :param field_name: str
        """
        change_field_value_in_json_and_save_file(path_to_input_json=path_to_json, field_name=field_name,
                                                 field_value=full_path_to_csv)

