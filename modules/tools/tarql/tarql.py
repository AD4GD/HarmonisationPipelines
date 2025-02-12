import os
import logging
import datetime
import subprocess
from collections import defaultdict
import rdflib
from rdflib.collection import Collection
from rdflib.term import BNode, URIRef

from modules.tools import basic_tool
from modules.utils.utils import is_path_abs, get_paths_normalized_basename


class Tarql(basic_tool.Tool):
    """
    Class that uses Tarql tool to generate dumps.
    """

    def __init__(self):
        super().__init__()
        self.directory = os.path.join('utils', 'tarql', 'target', 'appassembler')
        self.executable = 'bin/tarql'

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_tarql_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def generate_ntriples(self, input_csv, input_mapping, output_dir):
        """
        Function that uses tarql tool to generate ntriples.
        :param input_csv: str -> path to the input csv.
        :param input_mapping: str -> path to the input mapping.
        :param output_dir: str -> directory that stores output.
        """
        cwd = os.getcwd()
        if is_path_abs(input_csv):
            input_csv_full_path = input_csv
        else:
            input_csv_full_path = os.path.join(cwd, input_csv)
        if is_path_abs(input_mapping):
            input_mapping_full_path = input_mapping
        else:
            input_mapping_full_path = os.path.join(cwd, input_mapping)
        input_filename = os.path.splitext(get_paths_normalized_basename(input_csv))[0]
        output_full_path = os.path.join(output_dir, f"{input_filename}.ttl")
        with open(self.log_path, 'wb') as log:
            with open(output_full_path, 'wb') as output_target:
                p = subprocess.Popen([self.executable, input_mapping_full_path,
                                      input_csv_full_path], shell=False,
                                     cwd=self.directory, stdout=output_target, stderr=log)
        p.communicate()
        ntriples_output_full_path = os.path.splitext(output_full_path)[0] + '.nt'
        self._oneof_postprocessor(input_path=output_full_path)
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
    def _oneof_postprocessor(input_path):
        """
        Helper function for postprocessing oneOf predicate in order to generate collection.
        :param input_path: str
        """
        input_rdf = input_path

        g = rdflib.Graph()
        g2 = rdflib.Graph()
        g.parse(input_rdf, format="turtle")

        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        concepts = defaultdict(list)

        for s, p, o in g:
            if p == URIRef("http://www.w3.org/2002/07/owl#oneOf"):
                if not type(o) == BNode:
                    concepts[s].append(o)
                else:
                    g2.add((s, p, o))
            else:
                g2.add((s, p, o))

        for concept in concepts:
            bn = BNode()
            g2.add((concept, URIRef("http://www.w3.org/2002/07/owl#oneOf"), bn))
            Collection(g2, bn, concepts[concept])

        g2.serialize(destination=input_path, format="turtle")
