import os
import logging
import datetime
import sys

import rdflib
import yaml

from modules.lpis import lpis
from modules.utils.utils import generate_current_date, get_paths_normalized_basename


class LpisMappings(lpis.Lpis):
    def __init__(self, configfile, results_dir):
        super().__init__(result_dir=results_dir)
        self.configfile = configfile
        self.directory = os.path.join('statics', 'templates', 'mappings')

        # attributes from a config file
        self.base_uri = None
        self.label = None
        self.iacs_id = None
        self.valid_from = None
        self.short_id = None
        self.specific_land_use = None
        self.parent_adm2 = None
        self.parent_adm3 = None
        self.municipality_id = None
        self.area = None
        self.perimeter = None
        self.template_id = None
        self.layer_abbreviation = None

        self.identifier_scheme = None
        self.validated_config = True

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_lpis_mappings'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def load_from_config(self):
        """
        Function that loads all the information regarding specific template from a config file into
        attributes.
        """
        path = os.path.join('cfg', 'LPIS', self.configfile)
        with open(path) as file:
            mapping_cfg = yaml.load(file, Loader=yaml.FullLoader)
            self.base_uri = mapping_cfg['cfg'].get('BASE_URI')
            self.label = mapping_cfg['cfg'].get('LABEL')
            self.iacs_id = mapping_cfg['cfg'].get('IACS_ID')
            self.valid_from = mapping_cfg['cfg'].get('VALID_FROM')
            self.short_id = mapping_cfg['cfg'].get('SHORT_ID')
            self.specific_land_use = mapping_cfg['cfg'].get('SPECIFIC_LAND_USE')
            self.parent_adm2 = mapping_cfg['cfg'].get('PARENT_ADM2')
            self.parent_adm3 = mapping_cfg['cfg'].get('PARENT_ADM3')
            self.municipality_id = mapping_cfg['cfg'].get('MUNICIPALITY_ID')
            self.area = mapping_cfg['cfg'].get('AREA')
            self.perimeter = mapping_cfg['cfg'].get('PERIMETER')
            self.template_id = mapping_cfg['cfg'].get('TEMPLATE_ID')
            self.layer_abbreviation = mapping_cfg['cfg'].get('LAYER_ABBREVIATION')

            # adjusting base_uri and identifier_scheme based on layer_abbreviation occurrence.
            if self.layer_abbreviation:
                self.identifier_scheme = self.base_uri
                self.base_uri += self.layer_abbreviation + '/'
            else:
                self.identifier_scheme = self.base_uri

            required_fields = (self.base_uri, self.label, self.iacs_id, self.template_id)
            if any(field is None for field in required_fields):
                self.logger.info(f"Required parameter from a LPIS config file is missing. Please check "
                            f"following fields: BASE_URI, LABEL, IACSID, TEMPLATE_ID in {self.configfile}.")
                self.validated_config = False

    def create_mapping(self):
        """
        Main function that creates a new mapping file based on the information provided in the config file.
        """
        print('########## Generating mappings...')
        if not self.validated_config:
            print("Invalid config. Some required parameters are missing. Please check log file for more info!")
            sys.exit()
        for input_file in self.list_of_input_files:
            base_filename = get_paths_normalized_basename(input_file)
            filename = os.path.splitext(base_filename)[0]
            root_graph = self._geometry_mapping(filename=filename)
            if self.area:
                parcel_area_graph = self._parcel_area_mapping(filename=filename)
                root_graph += parcel_area_graph
            if self.perimeter:
                perimeter_graph = self._parcel_perimeter_mapping(filename=filename)
                root_graph += perimeter_graph
            parcel_graph = self._parcel_mapping(filename=filename)
            root_graph += parcel_graph

            mapping_path = os.path.join(self.mappings_dir)
            os.makedirs(mapping_path, exist_ok=True)
            file_path = os.path.join(mapping_path, f'LPIS_mapping_{filename}.ttl')
            with open(file_path, 'w') as f:
                #f.write(root_graph.serialize(format='ttl').decode('utf-8'))
                # above line commented due to the change in rdflib!
                f.write(root_graph.serialize(format='ttl'))

    def _geometry_mapping(self, filename):
        """
        Semi-private helper function that generates a geometry part of the mapping.
        :param filename: str -> input data that mapping is being generated for.
        :return: Graph instance -> Geometry part of the graph.
        """
        g = rdflib.Graph()
        g2 = rdflib.Graph()
        template_path = os.path.join(self.directory, 'lpis_geometry.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{filename}_geometry')
        template = self.base_uri + f"Parcel/Geometry/{self.template_id}"
        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])
        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'filename_geometry' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif '{filename}' in o:
                o1 = rdflib.term.Literal(f"`{filename}`")
                g2.add((s, p, o1))
            elif '{template}' in o:
                o2 = rdflib.term.Literal(template)
                g2.add((s, p, o2))
            else:
                g2.add((s, p, o))
        return g2

    def _parcel_area_mapping(self, filename):
        """
        Semi-private helper function that generates an area part of the mapping.
        :param filename: str -> input data that mapping is being generated for.
        :return: Graph instance -> Area part of the graph.
        """
        g = rdflib.Graph()
        g2 = rdflib.Graph()
        template_path = os.path.join(self.directory, 'lpis_parcel_area.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{filename}_parcel_area')
        template = self.base_uri + f"Parcel/Area/{self.template_id}"
        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])
        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'filename_parcel_area' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif '{filename}' in o:
                o1 = rdflib.term.Literal(f"`{filename}`")
                g2.add((s, p, o1))
            elif '{temp_area}' in o:
                o2 = rdflib.term.Literal(template)
                g2.add((s, p, o2))
            elif '{surface}' in o:
                o3 = rdflib.term.Literal(f"{self.area}")
                g2.add((s, p, o3))
            else:
                g2.add((s, p, o))
        return g2

    def _parcel_perimeter_mapping(self, filename):
        """
        Semi-private helper function that generates a perimeter part of the mapping.
        :param filename: str -> input data that mapping is being generated for.
        :return: Graph instance -> Perimeter part of the graph.
        """
        g = rdflib.Graph()
        g2 = rdflib.Graph()
        template_path = os.path.join(self.directory, 'lpis_parcel_perimeter.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{filename}_parcel_perimeter')
        template = self.base_uri + f"Parcel/Perimeter/{self.template_id}"
        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])
        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'filename_parcel_perimeter' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif '{filename}' in o:
                o1 = rdflib.term.Literal(f"`{filename}`")
                g2.add((s, p, o1))
            elif '{temp_parcel_perimeter}' in o:
                o2 = rdflib.term.Literal(template)
                g2.add((s, p, o2))
            elif '{column_perim}' in o:
                o3 = rdflib.term.Literal(f"{self.perimeter}")
                g2.add((s, p, o3))
            else:
                g2.add((s, p, o))
        return g2

    @staticmethod
    def _parcel_remove_redundant_triples_set(g, identifier):
        """
        Semi-private helper function that removes all triples associated with certain identifier from given
        graph.
        :param g: Graph instance -> input graph.
        :param identifier: str -> identifier.
        :return: Graph instance -> truncated graph.
        """
        new_g = rdflib.Graph()
        bnode_x = ""
        bnode_y = ""
        for ns in g.namespaces():
            new_g.namespace_manager.bind(ns[0], ns[1])

        for s, p, o in g:
            if identifier in o:
                bnode_x += s

        for s, p, o in g:
            if bnode_x in o:
                bnode_y += s

        for s, p, o in g:
            if bnode_y in s:
                continue
            if bnode_y in o:
                continue
            if bnode_x in s:
                continue
            if bnode_x in o:
                continue
            new_g.add((s, p, o))
        return new_g

    @staticmethod
    def _distinct_between_template_and_column(attribute):
        """
        Semi-private helper function that makes distinction between predicates. It assigns either template
        or column to given attribute.
        :param attribute: str -> attribute's value.
        :return: URIRef object -> appropriate predicate.
        """
        if all([x in attribute for x in ['{', '}']]):
            p = rdflib.term.URIRef("http://www.w3.org/ns/r2rml#template")
        else:
            p = rdflib.term.URIRef("http://www.w3.org/ns/r2rml#column")
        return p

    @staticmethod
    def _distinct_between_string_and_date(attribute):
        if all([x in attribute for x in ['{', '}']]):
            o = rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')
        else:
            o = rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#date')
        return o

    def _parcel_mapping(self, filename):
        """
        Semi-private helper function that generates a parcel part of the mapping.
        :param filename: str -> input data that mapping is being generated for.
        :return: Graph instance -> Parcel part of the graph.
        """
        g = rdflib.Graph()
        g2 = rdflib.Graph()
        template_path = os.path.join(self.directory, 'lpis_parcel.ttl')
        g.parse(template_path, format='ttl')
        # creating a copy of all prefixes that were present in the template.
        g_truncated = g
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])
        if not self.short_id:
            g_truncated = self._parcel_remove_redundant_triples_set(g_truncated, identifier="{shortid_var}")
        if not self.specific_land_use:
            g_truncated = self._parcel_remove_redundant_triples_set(g_truncated, identifier="{landuse_var}")
        if not self.parent_adm2:
            g_truncated = self._parcel_remove_redundant_triples_set(g_truncated, identifier="{parentadm2_var}")
        if not self.parent_adm3:
            g_truncated = self._parcel_remove_redundant_triples_set(g_truncated, identifier="{parameteradm3_var}")
        if not self.municipality_id:
            g_truncated = self._parcel_remove_redundant_triples_set(g_truncated, identifier="{municipalityid_var}")
        if not self.area:
            g_truncated = self._parcel_remove_redundant_triples_set(g_truncated, identifier="{temp_area}")
        if not self.perimeter:
            g_truncated = self._parcel_remove_redundant_triples_set(g_truncated, identifier="{temp_observed_perimeter}")
        if not self.valid_from:
            g_truncated = self._parcel_remove_redundant_triples_set(g_truncated, identifier='{datefrom_var}')

        target_ns = rdflib.Namespace(f'#{filename}_parcel')
        template = self.base_uri + f"Parcel/{self.template_id}"
        template_geometry = self.base_uri + f"Parcel/Geometry/{self.template_id}"
        template_area = self.base_uri + f"Parcel/Area/{self.template_id}"
        template_perimeter = self.base_uri + f"Parcel/Perimeter/{self.template_id}"
        if self.parent_adm2:
            template_parent_adm2 = self.base_uri + self.parent_adm2
        if self.parent_adm3:
            template_parent_adm3 = self.base_uri + self.parent_adm3

        curr_date = generate_current_date()
        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g_truncated:
            if 'filename_parcel' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif '{filename}' in o:
                o1 = rdflib.term.Literal(f"`{filename}`")
                g2.add((s, p, o1))
            elif '{temp_parcel}' in o:
                o2 = rdflib.term.Literal(template)
                g2.add((s, p, o2))
            elif '{IACSID_var}' in o:
                o3 = rdflib.term.Literal(self.iacs_id)
                p1 = self._distinct_between_template_and_column(self.iacs_id)
                g2.add((s, p1, o3))
            elif 'base_namespace' in o:
                o4 = rdflib.term.URIRef(self.identifier_scheme)
                g2.add((s, p, o4))
            elif '{datefrom_var}' in o:
                o5 = rdflib.term.Literal(self.valid_from)
                g2.add((s, p, o5))
            elif '{now_var}' in o:
                o6 = rdflib.term.Literal(str(curr_date))
                g2.add((s, p, o6))
            elif '{shortid_var}' in o:
                o7 = rdflib.term.Literal(self.short_id)
                g2.add((s, p, o7))
            elif '{temp_geometry}' in o:
                o8 = rdflib.term.Literal(template_geometry)
                g2.add((s, p, o8))
            elif '{temp_area}' in o:
                o9 = rdflib.term.Literal(template_area)
                g2.add((s, p, o9))
            elif '{temp_observed_perimeter}' in o:
                o10 = rdflib.term.Literal(template_perimeter)
                g2.add((s, p, o10))
            elif '{landuse_var}' in o:
                o11 = rdflib.term.Literal(self.specific_land_use)
                g2.add((s, p, o11))
            elif '{parentadm2_var}' in o:
                o12 = rdflib.term.Literal(template_parent_adm2)
                g2.add((s, p, o12))
            elif '{parameteradm3_var}' in o:
                o13 = rdflib.term.Literal(template_parent_adm3)
                g2.add((s, p, o13))
            elif '{municipalityid_var}' in o:
                o14 = rdflib.term.Literal(self.municipality_id)
                p2 = self._distinct_between_template_and_column(self.municipality_id)
                g2.add((s, p2, o14))
            elif '{label_var}' in o:
                o15 = rdflib.term.Literal(self.label)
                g2.add((s, p, o15))
            elif 'string_or_date' in o:
                o16 = self._distinct_between_string_and_date(self.valid_from)
                g2.add((s, p, o16))
            else:
                g2.add((s, p, o))
        return g2
