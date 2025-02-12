import logging
import os
import datetime
import subprocess
import yaml

import rdflib

from modules.utils.utils import is_path_abs
from modules.tools import basic_tool


class GeoTriplesMapper(basic_tool.Tool):
    """
    Class that uses GeoTriples tool to generate mappings or transforming data into dumps.
    """

    def __init__(self):
        super().__init__()
        self.directory = os.path.join('utils', 'GeoTriples')
        self.executable = 'bin/geotriples-all'

        # optional in case db is a source of data
        self.db_type = None
        self.db_username = None
        self.db_password = None
        self.db_host = None
        self.db_port = None
        self.db_name = None

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_geotriples_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    @staticmethod
    def _change_id_col(mapping_file):
        """
        Semi-private function for adjusting reference to id column from geotriples default to column that was created
        during pre-processing phase.
        :param mapping_file: str -> full path to the mapping file.
        """
        g = rdflib.Graph()
        g2 = rdflib.Graph()
        g.parse(mapping_file, format='ttl')
        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])
        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if "template" in p and "{GeoTriplesID}" in o:
                modified_o = rdflib.Literal(o.replace("{GeoTriplesID}", "{seq}"))
                g2.add((s, p, modified_o))
            else:
                g2.add((s, p, o))
        return g2

    def _adjust_id_col(self, mapping):
        """
        Semi-private function that creates new mapping with updated id value and deletes
        the older one.
        :param mapping: str -> full path to the mapping file.
        """
        new_graph = self._change_id_col(mapping_file=mapping)
        os.remove(mapping)
        with open(mapping, 'w') as f:
            f.write(new_graph.serialize(format='ttl'))

    def generate_mappings(self, input_data, mapping_dir, base_uri, adjust_id=False):
        """
        Function that uses GeoTriples tool to create mappings based on the input file.
        :param input_data: str -> path to the input file/directory.
        :param mapping_dir: str -> directory where mappings should be saved.
        :param base_uri: str -> base URI used within the mapping.
        :param adjust_id: bool -> flag, if True default id given by geotriples will be overwritten.
        """
        self.detect_system()
        cwd = os.getcwd()
        if is_path_abs(input_data):
            input_full_path = input_data
        else:
            input_full_path = os.path.join(cwd, input_data)
        if is_path_abs(mapping_dir):
            output_dir = mapping_dir
        else:
            output_dir = os.path.join(cwd, mapping_dir)
        if os.path.isfile(input_full_path):
            input_filename = os.path.splitext(input_full_path)[0]
            output_full_path = os.path.join(output_dir, input_filename)
            if base_uri:
                with open(self.log_path, 'wb') as log:
                    p = subprocess.Popen([self.executable, 'generate_mapping', '-o', f'{output_full_path}.ttl',
                                          '-b', base_uri, input_full_path], shell=False,
                                         cwd=self.directory, stdout=log, stderr=log)
            else:
                with open(self.log_path, 'wb') as log:
                    p = subprocess.Popen([self.executable, 'generate_mapping', '-o', f'{output_full_path}.ttl',
                                          input_full_path], shell=False, cwd=self.directory, stdout=log, stderr=log)
            p.communicate()
            if adjust_id:
                self._adjust_id_col(mapping=f'{output_full_path}.ttl')
        elif os.path.isdir(input_full_path):
            for file in os.listdir(input_full_path):
                file_extension = os.path.splitext(file)[1]
                if file_extension in (".shp", ".gml", ".kml", ".geojson", ".csv"):
                    input_filename = os.path.splitext(file)[0]
                    input_with_file_path = os.path.join(input_full_path, file)
                    output_full_path = os.path.join(output_dir, input_filename)
                    if base_uri:
                        with open(self.log_path, 'wb') as log:
                            p = subprocess.Popen([self.executable, 'generate_mapping', '-o', f'{output_full_path}.ttl',
                                                  '-b', base_uri, input_with_file_path],
                                                 cwd=self.directory, shell=False, stdout=log, stderr=log)
                    else:
                        with open(self.log_path, 'wb') as log:
                            p = subprocess.Popen([self.executable, 'generate_mapping', '-o', f'{output_full_path}.ttl',
                                                  input_with_file_path], shell=False, cwd=self.directory, stdout=log,
                                                 stderr=log)
                    p.communicate()
                    if adjust_id:
                        self._adjust_id_col(mapping=f'{output_full_path}.ttl')
        else:
            print('Input not recognized. Please make sure this is valid path to either single'
                  'file or directory.')

    def generate_mappings_from_db(self, mapping_dir, base_uri):
        """
        Function that uses GeoTriples tool to create mappings based on relation database.
        :param mapping_dir: str -> directory where mappings should be saved.
        :param base_uri: str -> base URI used within the mapping.
        """
        self._load_db_config()
        jdbc_url = self._generate_jdbc_url()
        cwd = os.getcwd()
        if is_path_abs(mapping_dir):
            output_full_path = os.path.join(mapping_dir, "mapping_from_db.ttl")
        else:
            output_full_path = os.path.join(cwd, mapping_dir, "mapping_from_db.ttl")
        with open(self.log_path, 'wb') as log:
            if self.db_password:
                p = subprocess.Popen([self.executable, 'generate_mapping', '-b', base_uri, '-u', self.db_username,
                                      '-p', self.db_password, '-o', output_full_path, jdbc_url],
                                     shell=False, cwd=self.directory, stdout=log, stderr=log)
            else:
                p = subprocess.Popen([self.executable, 'generate_mapping', '-b', base_uri, '-u', self.db_username,
                                      '-o', output_full_path, jdbc_url],
                                     shell=False, cwd=self.directory, stdout=log, stderr=log)
        p.communicate()

    def _load_db_config(self):
        """
        Helper function for loading config for database usage.
        """
        with open(os.path.join("cfg", "config.yaml")) as file:
            cfg = yaml.load(file, Loader=yaml.FullLoader)
            db_cfg = cfg.get("sql_cfg")
            if not db_cfg:
                msg = "Aborting. Missing sql_cfg section in the config.yaml file. This is required" \
                      " when using database as data source."
                raise SystemExit(msg)
            self.db_type = db_cfg.get("DB_TYPE")
            self.db_username = db_cfg.get("DB_USERNAME")
            self.db_password = db_cfg.get("DB_PASSWORD")
            self.db_host = db_cfg.get("DB_HOST")
            self.db_port = db_cfg.get("DB_PORT")
            self.db_name = db_cfg.get("DB_NAME")
            required_fields = (self.db_type, self.db_username, self.db_host, self.db_name)
            if any(field is None for field in required_fields):
                self.logger.info(f"Invalid config. Value for one or more of {required_fields} "
                                 f" is missing in the config file!")
                msg = "Invalid config! Check logs for more info. Aborting..."
                raise SystemExit(msg)

    def _generate_jdbc_url(self):
        """
        Helper function for generating jdbc url based on input from the config file.
        """
        if self.db_port:
            jdbc_url = f"jdbc:{self.db_type}://{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            jdbc_url = f"jdbc:{self.db_type}://{self.db_host}/{self.db_name}"
        return jdbc_url

    def transform_shapefile(self, input_data, input_mapping, dump_filename, base_uri):
        """
        Main function that uses GeoTriples tool to create dumps based on the input shapefile.
        :param input_data: str -> path to the input data file.
        :param input_mapping: str -> path to the mapping file.
        :param base_uri: str -> base URI.
        :param dump_filename: str -> name for the dump file that will be generated.
        """
        self.detect_system()
        cwd = os.getcwd()
        if is_path_abs(input_data):
            input_data_full_path = input_data
        else:
            input_data_full_path = os.path.join(cwd, input_data)
        if is_path_abs(input_mapping):
            input_mapping_full_path = input_mapping
        else:
            input_mapping_full_path = os.path.join(cwd, input_mapping)
        if is_path_abs(dump_filename):
            output_full_path = dump_filename
        else:
            output_full_path = os.path.join(cwd, dump_filename)
        if os.path.isfile(input_data_full_path):
            if os.path.isfile(input_mapping_full_path):
                if base_uri:
                    with open(self.log_path, 'wb') as log:
                        p = subprocess.Popen([self.executable, 'dump_rdf', '-o', f'{output_full_path}', '-b', base_uri,
                                              '-sh', input_data_full_path, input_mapping_full_path],
                                             cwd=self.directory, stderr=log, stdout=log, shell=False)
                else:
                    with open(self.log_path, 'wb') as log:
                        p = subprocess.Popen([self.executable, 'dump_rdf', '-o', f'{output_full_path}', '-sh',
                                              input_data_full_path, input_mapping_full_path],
                                             cwd=self.directory, stderr=log, stdout=log, shell=False)
                p.communicate()
            else:
                self.logger.info(f"mapping file: {input_mapping_full_path} has to point to the existing file directly!")
                print(f"mapping file: {input_mapping_full_path} has to point to the existing file!")
        else:
            self.logger.info(f"input file: {input_data_full_path} has to point to the existing file directly!")
            print(f"input file: {input_data_full_path} has to point to the existing file!")

    def transform_rdf(self, input_mapping, dump_filename):
        """
        Function that uses GeoTriple tool to create dumps based on the input mapping that references csv file.
        :param input_mapping: str -> path to the mapping file.
        :param dump_filename: str -> name for the dump file that will be generated.
        :return:
        """
        self.detect_system()
        cwd = os.getcwd()
        if is_path_abs(input_mapping):
            input_mapping_full_path = input_mapping
        else:
            input_mapping_full_path = os.path.join(cwd, input_mapping)
        if is_path_abs(dump_filename):
            output_full_path = dump_filename
        else:
            output_full_path = os.path.join(cwd, dump_filename)
        if os.path.isfile(input_mapping_full_path):
            with open(self.log_path, 'wb') as log:
                p = subprocess.Popen([self.executable, 'dump_rdf', '-o', output_full_path, '-rml',
                                      input_mapping_full_path],
                                     cwd=self.directory, stderr=log, stdout=log, shell=False)
                p.communicate()

        else:
            self.logger.info(f"{input_mapping_full_path} has to point to the file directly and not to a directory!")
            print(f"{input_mapping_full_path} has to point to the file directly and not to a directory!")

    def transform_db(self, input_mapping, output_dump_path, base_uri):
        """
        Function that uses GeoTriple tool to create dumps based on the input from relational database.
        :param input_mapping: str -> path to the mapping file.
        :param output_dump_path: str -> path to the output dump.
        :param base_uri: str -> base uri.
        """
        self._load_db_config()
        jdbc_url = self._generate_jdbc_url()
        cwd = os.getcwd()
        if is_path_abs(input_mapping):
            input_mapping_full_path = input_mapping
        else:
            input_mapping_full_path = os.path.join(cwd, input_mapping)
        if is_path_abs(output_dump_path):
            output_full_path = output_dump_path
        else:
            output_full_path = os.path.join(cwd, output_dump_path)
        with open(self.log_path, 'wb') as log:
            if self.db_password:
                if base_uri:
                    p = subprocess.Popen([self.executable, 'dump_rdf', '-b', base_uri, '-o', output_full_path,
                                          '-u', self.db_username, '-p', self.db_password, '-jdbc', jdbc_url,
                                          input_mapping_full_path],
                                         shell=False, cwd=self.directory, stdout=log, stderr=log)
                else:
                    p = subprocess.Popen([self.executable, 'dump_rdf', '-o', output_full_path,
                                          '-u', self.db_username, '-p', self.db_password, '-jdbc', jdbc_url,
                                          input_mapping_full_path],
                                         shell=False, cwd=self.directory, stdout=log, stderr=log)
            else:
                if base_uri:
                    p = subprocess.Popen([self.executable, 'dump_rdf', '-b', base_uri, '-o', output_full_path,
                                          '-u', self.db_username, '-jdbc', jdbc_url, input_mapping_full_path],
                                         shell=False, cwd=self.directory, stdout=log, stderr=log)
                else:
                    p = subprocess.Popen([self.executable, 'dump_rdf', '-o', output_full_path,
                                          '-u', self.db_username, '-jdbc', jdbc_url, input_mapping_full_path],
                                         shell=False, cwd=self.directory, stdout=log, stderr=log)
        p.communicate()
