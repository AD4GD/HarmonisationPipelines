import logging
import datetime
import os
import sys

import rdflib

from modules.generic import generic
from modules.tools.geotriples.geotriples import GeoTriplesMapper
from modules.tools.rml_mapper.rml_mapper import RmlMapper
from modules.tools.tarql.tarql import Tarql
from modules.tools.csv2rdf.csv2rdf import CSV2RDF
from modules.utils.utils import get_paths_normalized_basename


class GenericTransform(generic.Generic):
    """
    Subclass of Generic that deals with transformation tasks.
    """
    def __init__(self, mapper, input_type, base_uri=None, adjust_rml_source=False):
        super().__init__()
        self.mapper = mapper
        self.base_uri = base_uri
        self.input_type = input_type
        self.adjust_source = adjust_rml_source
        self.list_of_input_files = []
        self.list_of_input_mappings = []

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_generic_transform'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def _create_output_path(self, mapping, transformer):
        """
        Semi-private helper function that creates directory and output name for dumps in the FADN
        transformation process.
        :param mapping: str -> mapping filename.
        :param transformer: object -> transformer instance.
        :return: str -> full path and name of the output that should be produced by mapper tool.
        """
        dumps_directory = os.path.join(transformer.directory, self.dumps_dir)
        os.makedirs(dumps_directory, exist_ok=True)  # creates directory only if it doesn't already exist.
        mapping_name = os.path.splitext(mapping)[0]
        output_filename = f'{mapping_name}.nt'
        output_full_path = os.path.join(dumps_directory, output_filename)
        return output_full_path

    @staticmethod
    def _change_the_tablename(mapping_file, tablename_value):
        """
        Semi-private function that performs a change to the tablename in the mapping.
        :param mapping_file: str -> full path to the mapping file.
        :param tablename_value: str -> value that tablename should be replaced with.
        :return: rdflib Graph Object -> new graph with adjusted tablename.
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
            if "tableName" in p:
                modified_o = rdflib.term.Literal('`' + tablename_value + '`')
                g2.add((s, p, modified_o))
            else:
                g2.add((s, p, o))
        return g2

    def _adjust_the_tablename(self, tablename_value):
        """
        Semi-private function that creates new mapping with updated tableName value and deletes
        the older one.
        :param tablename_value: str -> value that tablename should be replaced with.
        """
        mapping = self.list_of_input_mappings[0]  # this function is evoked only if one mapping exists.
        new_graph = self._change_the_tablename(mapping_file=mapping, tablename_value=tablename_value)
        os.remove(mapping)
        with open(mapping, 'w') as f:
            f.write(new_graph.serialize(format='ttl'))

    def _change_the_rml_source(self, mapping_file, data_dir):
        """
        Semi-private function that performs path change in the rml source field in the mapping.
        :param mapping_file: str -> full path to the mapping file.
        :param data_dir: str -> path to the directory that stores input file.
        :return rdflib Graph Object -> new graph with adjusted source.
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
        filename = None
        for s, p, o in g:
            if "rml#source" in p:
                filename = get_paths_normalized_basename(o)
                data_path = os.path.abspath(os.path.join(data_dir, filename))
                # checking if the path to the file really exist
                if not os.path.isfile(data_path):
                    print("Incorrect data filename in the mapping file.")
                    print("Exiting...")
                    self.logger.info(f"It looks like filename include in the source of {mapping_file} does not exist!")
                    sys.exit()
                modified_o = rdflib.term.Literal(data_path)
                g2.add((s, p, modified_o))
            else:
                g2.add((s, p, o))
        return g2

    def _adjust_mappings_rml_source(self):
        """
        Semi-private function that validates the input path included in the mapping and changes it into the valid one
        if necessary.
        """
        for mapping in self.list_of_input_mappings:
            data_dir = os.path.join(self.results_dir, self.folder)
            new_graph = self._change_the_rml_source(mapping_file=mapping, data_dir=data_dir)
            os.remove(mapping)
            with open(mapping, 'w') as f:
                f.write(new_graph.serialize(format='ttl'))

    @staticmethod
    def _change_the_source(mapping_file, data_file):
        """
        Semi-private helper function that adjusts the source in single mapping for multiple data inputs.
        :param mapping_file: str -> full path to the mapping file.
        :param data_file: str -> full path to the input file.
        :return: rdflib Graph Object -> new graph with adjusted source.
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
            if "rml#source" in p:
                data_path = os.path.abspath(data_file)
                modified_o = rdflib.term.Literal(data_path)
                g2.add((s, p, modified_o))
            else:
                g2.add((s, p, o))
        return g2

    def _adjust_rml_source_for_single_mapping(self, data_file):
        """
        Semi-private function that adjusts rml source in single mapping for multiple input files.
        :param data_file: str -> full path to the input file.
        """
        mapping = self.list_of_input_mappings[0]  # this function is evoked only if one mapping exists.
        new_graph = self._change_the_source(mapping_file=mapping, data_file=data_file)
        os.remove(mapping)
        with open(mapping, 'w') as f:
            f.write(new_graph.serialize(format='ttl'))

    def _create_list_of_input_files(self):
        """
        Semi-private function that creates list of input files.
        """
        input_type_mapper = {
            "Shapefile": ".shp",
            "CSV": ".csv",
            "JSON": ".json",
            "CSVW": ".csv",
            "XML": ".xml",
        }
        input_extension = input_type_mapper.get(self.input_type)
        data_dir = os.path.join(self.results_dir, self.folder)
        for subdir, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith(input_extension):
                    full_file_path = os.path.join(subdir, file)
                    self.list_of_input_files.append(full_file_path)

    def _create_list_of_input_mappings(self, CSVW_mapping=False):
        """
        Semi-private function that creates list of input_mappings.
        :return:
        """
        mapping_dir = os.path.join(self.results_dir, self.mappings_dir)
        for subdir, dirs, files in os.walk(mapping_dir):
            for file in files:
                if CSVW_mapping:
                    if file.endswith(".json"):
                        full_mapping_path = os.path.join(subdir, file)
                        self.list_of_input_mappings.append(full_mapping_path)
                else:
                    if file.endswith(".ttl"):
                        full_mapping_path = os.path.join(subdir, file)
                        self.list_of_input_mappings.append(full_mapping_path)

    def _detect_input_sparql_query(self):
        """
        Semi-private function that sets an input mapping to the sparql query.
        """
        mapping_dir = os.path.join(self.results_dir, self.mappings_dir)
        for subdir, dirs, files in os.walk(mapping_dir):
            for file in files:
                full_mapping_path = os.path.join(subdir, file)
                self.list_of_input_mappings.append(full_mapping_path)

    def _is_single_mapping(self):
        """
        Semi-private function that checks if single or multiple mappings were provided.
        :return: boolean -> True if single, False otherwise.
        """
        no_of_mappings = len(self.list_of_input_mappings)
        if no_of_mappings == 0:
            self.logger.debug("No mappings were found in the directory!")
            sys.exit(0)
        elif no_of_mappings == 1:
            return True
        else:
            return False

    def _rml_transformation(self, adjust_rml_source, single_mapping):
        """
        Semi-private function that iterates through data folder and creates transformation for data file.
        :param adjust_rml_source: boolean -> if True source will be adjusted.
        :param single_mapping: boolean -> if True all input files will be processed with the same mapping.
        """
        print('########## Initializing transformer...')
        transformer = RmlMapper()
        if single_mapping:
            input_mapping = self.list_of_input_mappings[0]   # only one mapping exists if this block fires.
            for input_file in self.list_of_input_files:
                full_filename = get_paths_normalized_basename(input_file)
                data_filename = os.path.splitext(full_filename)[0]
                if adjust_rml_source:
                    self._adjust_rml_source_for_single_mapping(data_file=input_file)
                output_dump_full_path = os.path.join(self.results_dir, self.dumps_dir, f"{data_filename}.nt")
                transformer.generate_dumps(input_data=input_mapping, dump_path=output_dump_full_path)
        else:
            if adjust_rml_source:
                self._adjust_mappings_rml_source()
            for mapping_file in self.list_of_input_mappings:
                full_mapping_name = get_paths_normalized_basename(mapping_file)
                mapping_filename = os.path.splitext(full_mapping_name)[0]
                output_dump_full_path = os.path.join(self.results_dir, self.dumps_dir, f"{mapping_filename}.nt")
                transformer.generate_dumps(input_data=mapping_file, dump_path=output_dump_full_path)

    def _geo_transformation_shapefiles(self, single_mapping):
        """
        Semi-private function that iterates through data folder and creates transformation for shapefile(s) input data.
        :param single_mapping: boolean -> if True all input files will be processed with the same mapping.
        """
        print('########## Initializing transformer...')
        transformer = GeoTriplesMapper()
        if single_mapping:
            input_mapping = self.list_of_input_mappings[0]   # only one mapping exists if this block fires.
            for input_file in self.list_of_input_files:
                full_filename = get_paths_normalized_basename(input_file)
                data_filename = os.path.splitext(full_filename)[0]
                self._adjust_the_tablename(tablename_value=data_filename)
                output_dump_full_path = os.path.join(self.results_dir, self.dumps_dir, f"{data_filename}.nt")
                transformer.transform_shapefile(input_data=input_file, input_mapping=input_mapping,
                                                dump_filename=output_dump_full_path, base_uri=self.base_uri)

        else:
            for input_file in self.list_of_input_files:
                full_filename = get_paths_normalized_basename(input_file)
                data_filename = os.path.splitext(full_filename)[0]
                input_mapping_full_path = os.path.join(self.results_dir, self.mappings_dir, f"{data_filename}.ttl")
                output_dump_full_path = os.path.join(self.results_dir, self.dumps_dir, f"{data_filename}.nt")
                transformer.transform_shapefile(input_data=input_file, input_mapping=input_mapping_full_path,
                                                dump_filename=output_dump_full_path, base_uri=self.base_uri)

    def _geo_transformation(self, adjust_rml_source, single_mapping):
        """
        Semi-private function that iterates through mapping folder and creates transformation.
        :param adjust_rml_source: boolean -> if True source will be adjusted.
        :param single_mapping: boolean -> if True all input files will be processed with the same mapping.
        """
        print('########## Initializing transformer...')
        transformer = GeoTriplesMapper()
        if single_mapping:
            input_mapping = self.list_of_input_mappings[0]   # only one mapping exists if this block fires.
            for input_file in self.list_of_input_files:
                full_filename = get_paths_normalized_basename(input_file)
                data_filename = os.path.splitext(full_filename)[0]
                self._adjust_rml_source_for_single_mapping(data_file=input_file)
                output_dump_full_path = os.path.join(self.results_dir, self.dumps_dir, f"{data_filename}.nt")
                transformer.transform_rdf(input_mapping=input_mapping, dump_filename=output_dump_full_path)
        else:
            if adjust_rml_source:
                self._adjust_mappings_rml_source()
            for mapping_file in self.list_of_input_mappings:
                full_mapping_name = get_paths_normalized_basename(mapping_file)
                mapping_filename = os.path.splitext(full_mapping_name)[0]
                output_dump_full_path = os.path.join(self.results_dir, self.dumps_dir, f"{mapping_filename}.nt")
                transformer.transform_rdf(input_mapping=mapping_file, dump_filename=output_dump_full_path)

    def _db_geo_transformation(self):
        """
        Semi-private helper function for initializing transformation using geotriples with input data
        coming from relation database.
        """
        print('########## Initializing transformer...')
        transformer = GeoTriplesMapper()
        input_mapping = self.list_of_input_mappings[0]   # only one mapping exists if this block fires.
        output_full_path = os.path.join(self.results_dir, self.dumps_dir, "dump_from_db.nt")
        transformer.transform_db(input_mapping=input_mapping, output_dump_path=output_full_path, base_uri=self.base_uri)

    def process_transformation(self):
        """
        Main function that performs transformations.
        """
        target_folder = os.path.join(self.results_dir, self.dumps_dir)
        os.makedirs(target_folder, exist_ok=True)
        self._create_list_of_input_files()
        if self.mapper == 'tarql':
            self._detect_input_sparql_query()
        else:
            if self.input_type == "CSVW":
                self._create_list_of_input_mappings(CSVW_mapping=True)
            else:
                self._create_list_of_input_mappings()
        is_mapping_single = self._is_single_mapping()
        if self.mapper == 'rml':
            if is_mapping_single:
                self._rml_transformation(adjust_rml_source=self.adjust_source, single_mapping=True)
            else:
                self._rml_transformation(adjust_rml_source=self.adjust_source, single_mapping=False)
        elif self.mapper == 'geo':
            if self.input_type == 'Shapefile':
                if is_mapping_single:
                    self._geo_transformation_shapefiles(single_mapping=True)
                else:
                    self._geo_transformation_shapefiles(single_mapping=False)
            elif self.input_type in ['CSV', 'JSON']:
                if is_mapping_single:
                    self._geo_transformation(adjust_rml_source=self.adjust_source,
                                             single_mapping=True)
                else:
                    self._geo_transformation(adjust_rml_source=self.adjust_source,
                                             single_mapping=False)
            elif self.input_type == 'DB':
                if is_mapping_single:
                    self._db_geo_transformation()
                else:
                    msg = "Only a single mapping file is supported when input data coming from" \
                          " relation database!"
                    raise SystemExit(msg)
        elif self.mapper == 'tarql':
            if is_mapping_single:
                transformer = Tarql()
                single_mapping = self.list_of_input_mappings[0]
                for input_file in self.list_of_input_files:
                    transformer.generate_ntriples(input_csv=input_file, input_mapping=single_mapping,
                                                  output_dir=target_folder)
            else:
                msg = "An error occurred. More than one file was found in the directory that should contain" \
                      " a single SPARQL query. Please check and make it unambiguous which file should be treated" \
                      " as SPARQL query!"
                raise SystemExit(msg)
        elif self.mapper == "csv2rdf":
            transformer = CSV2RDF()
            if is_mapping_single:
                single_mapping = self.list_of_input_mappings[0]
                if len(self.list_of_input_files) > 1:
                    msg = "Multiple CSV files provided via input. CSVW transformation currently do not support" \
                          "single mapping to multiple inputs case. Please limit your input to one CSV file."
                    sys.exit(msg)
                single_input_csv = self.list_of_input_files[0]
                transformer.run_csv2rdf(input_json=single_mapping, input_csv=single_input_csv, output_dir=target_folder)
            else:
                msg = "CSVW transformation currently do not support multiple mappings (json files). Please provide " \
                      "a single CSV + JSON pair."
                sys.exit(msg)

        else:
            self.logger.info("Mapper not recognized! Transformation aborted.")


