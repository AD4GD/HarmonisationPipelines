import os
import rdflib
import re

from modules.general_mapping.general_mapping_base import GeneralMappingGenerator
from modules.utils.utils import match_predicate_with_datatype, parse_config_value


class GeneralMappingGeneratorShp(GeneralMappingGenerator):
    """
    Class that handles generating general mapping solution for the Generic Pipeline.
    """
    def __init__(self, config_path, shp_filename, base_uri):
        super().__init__(config_path=config_path, base_uri=base_uri)
        # BASE ATTRS
        self.filename = shp_filename
        # TEMPLATE ATTRS
        self.template_path = os.path.join("statics", "templates", "general_mapping", "shp")
        self.template_geo_file = "geometry.ttl"
        self.template_main_file = "main.ttl"
        self.template_secondary_file = "complex.ttl"
        self.template_main_path = os.path.join(self.template_path, self.template_main_file)
        self.template_complex_path = os.path.join(self.template_path, self.template_secondary_file)
        self.template_geo_path = os.path.join(self.template_path, self.template_geo_file)
        # AUXILIARY ATTRS
        self.geometry_key = "hasGeometry"

    ###############################################################################
    #                               MAIN METHODS (SHP SPECIFIC) .                 #
    ###############################################################################

    def generate_mapping(self):
        """
        Main function that takes care of generating the whole new mapping based on the config file
        provided by the user.
        :return: Graph object -> full graph object that can be serialized.
        """
        self.logger.info("### GENERATING MAPPING... ###")
        root_graph = rdflib.Graph()

        graph = self._generate_geometry_section(graph=root_graph)
        graph += self._generate_main_section()
        graph += self._generate_all_complex_sections()
        graph = self._update_graph_with_prefixes(graph)

        return graph

    ###############################################################################
    #                               AUXILIARY METHODS (SHP SPECIFIC) .            #
    ###############################################################################

    def _search_for_geometry(self):
        """
        Semi-private helper function that looks up geometry value from a config file. In case
        the value is missing function generates custom geometry value.
        :return: str -> geometry.
        """
        if self.geometry_key in self.main_type:
            return self.main_type[self.geometry_key]
        else:
            return self.base_uri + "/" + self.template_id + "/geo"

    @staticmethod
    def _distinct_between_template_column_constant(value):
        """
        Function that distinct between predicates based on given value.
        :param value: input value from which predicate will be derived.
        :return: URIRef for a predicate.
        """
        val = re.split("[|]", value)[0]
        if "<" and ">" in val:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#constant')
        elif "{" and "}" in val:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#template')
        elif "`" in val and "{" not in val:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#column')
        else:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#template')

    @staticmethod
    def _distinct_between_template_constant_in_subjectmap(val):
        """
        Function that distinct between predicates based on given value for core section of the mapping in subjectMap.
        :param value: input value from which predicate will be derived.
        :return: URIRef for a predicate.
        """
        # currently, no distinction here for shapefiles, but it might change in the future
        return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#template')

    def _load_main_properties_into_graph(self, graph, main_node, predicate_object_bnode):
        """
        Semi-private helper function that loads properties from a config file into a graph.
        :param graph: Graph object -> graph.
        """
        def _load_property(property_key, property_val, predicate_object_bnd):
            self.logger.debug(f"{property_val}=")
            datatype_predicate, datatype = match_predicate_with_datatype(value=property_val)
            if not datatype:
                datatype = self._resolve_datatype(value=property_val)
            self.logger.debug(f"{datatype_predicate=}")
            self.logger.debug(f"{datatype=}")
            predicate = self._parse_predicate(value=property_key)
            self.logger.debug(f"{predicate=}")
            template_column_or_constant = self._distinct_between_template_column_constant(value=property_val)
            self.logger.debug(f"{template_column_or_constant=}")
            resolved_value = self._resolve_value_if_needed(value=property_val)
            self.logger.debug(f"{resolved_value=}")
            current_bnode = rdflib.term.BNode()
            self.logger.debug(f"{current_bnode=}")
            self.logger.debug(f"{predicate_object_bnd=}")
            if not predicate_object_bnd:
                predicate_object_bnd = self._assign_object_bnode(graph=graph, main_node=main_node)

            graph.add((predicate_object_bnd,
                       rdflib.term.URIRef('http://www.w3.org/ns/r2rml#objectMap'),
                       current_bnode))
            graph.add((predicate_object_bnd,
                       rdflib.term.URIRef('http://www.w3.org/ns/r2rml#predicate'),
                       predicate))

            if resolved_value:
                graph.add((current_bnode,
                           template_column_or_constant,
                           resolved_value))
            else:
                graph.add((current_bnode,
                           template_column_or_constant,
                           rdflib.term.Literal(parse_config_value(property_val).strip("<>"))))
            graph.add((current_bnode, datatype_predicate, datatype))

        # First, add property associated with hasGeometry, that is not present in the config.
        self.logger.info("Loading geometry property into graph...")
        geometry_value = self._search_for_geometry()
        self.logger.debug(f"{geometry_value=}")
        bnode = rdflib.term.BNode()
        datatype_predicate, datatype = match_predicate_with_datatype(value=geometry_value)
        if not datatype:
            datatype = self._resolve_datatype(value=geometry_value)
        self.logger.debug(f"{datatype_predicate=}")
        self.logger.debug(f"{datatype=}")
        template_column_or_constant = self._distinct_between_template_column_constant(value=geometry_value)
        self.logger.debug(f"{template_column_or_constant}")
        predicate = self._parse_predicate(value=self.geometry_key)
        self.logger.debug(f"{predicate=}")
        if not predicate_object_bnode:
            predicate_object_bnode = self._assign_object_bnode(graph=graph, main_node=main_node)

        graph.add((predicate_object_bnode,
                   rdflib.term.URIRef('http://www.w3.org/ns/r2rml#objectMap'),
                   bnode))
        graph.add((predicate_object_bnode,
                   rdflib.term.URIRef('http://www.w3.org/ns/r2rml#predicate'),
                   predicate))
        predicate_object_bnode = None
        if 'constant' in template_column_or_constant:
            graph.add((bnode,
                       template_column_or_constant,
                       rdflib.term.URIRef(geometry_value.strip("<>"))))
        else:
            graph.add((bnode,
                       template_column_or_constant,
                       rdflib.term.Literal(geometry_value)))
        if datatype:
            graph.add((bnode, datatype_predicate, datatype))

        # Then, load rest of properties
        for key, value in self.main_type.items():
            self.logger.info("Loading properties from config into graph...")
            if key not in self.config_keywords:
                self.logger.debug(f"{key=}")
                self.logger.debug(f"{value=}")
                if isinstance(value, list):
                    # logic for handling a list of properties associated with the main type
                    for single_val in value:
                        _load_property(property_key=key, property_val=single_val,
                                       predicate_object_bnd=predicate_object_bnode)
                        # resetting bnode to avoid all properties under same objectMap
                        predicate_object_bnode = None
                else:
                    _load_property(property_key=key, property_val=value, predicate_object_bnd=predicate_object_bnode)
                    # resetting bnode to avoid all properties under same objectMap
                    predicate_object_bnode = None

    def _generate_geometry_section(self, graph):
        """
        Semi-private helper function that generates a geometry section for the mapping.
        :param graph: Graph object -> graph.
        :param template_geo: str -> path to the Turtle file containing mapping template.
        :return: Graph object -> updated graph.
        """
        g = rdflib.Graph()
        g2 = graph
        g.parse(self.template_geo_path, format='ttl')
        template_value = self._search_for_geometry()
        self.logger.info("Generating geometry section...")
        self.logger.debug(f"{template_value=}")
        #self.logger.debug(f"{self.mapping_filename=}")
        for s, p, o in g:
            if 'filename_geometry' in s:
                #s1 = rdflib.term.URIRef(f"#{self.mapping_filename}_geometry")
                s1 = rdflib.term.URIRef(f"geometry")
                g2.add((s1, p, o))
            elif '{filename}' in o:
                o1 = rdflib.term.Literal(f"`{self.filename}`")
                g2.add((s, p, o1))
            elif '{template}' in o:
                o2 = rdflib.term.Literal(template_value)
                g2.add((s, p, o2))
            else:
                g2.add((s, p, o))
        return g2

    def _generate_main_section(self):
        """
        Semi-private helper function that generates a main section for the mapping.
        :return: Graph object -> new graph object.
        """
        g = rdflib.Graph()
        g2 = rdflib.Graph()
        g.parse(self.template_main_path, format='ttl')
        self.logger.info("Generating main section...")
        template_value = self.base_uri + "/" + self.template_id
        self.logger.debug(f"{template_value=}")
        #self.logger.debug(f"{self.filename=}")
        for s, p, o in g:
            if 'filename_main' in s:
                s1 = rdflib.term.URIRef(f"#{self.main_section_name}")
                main_node = s1
                if "r2rml#predicateObjectMap" in p:
                    predicate_object_bnode = o
                g2.add((s1, p, o))
            elif '{filename}' in o:
                o1 = rdflib.term.Literal(f"`{self.filename}`")
                g2.add((s, p, o1))
            elif '{template}' in o:
                o2 = rdflib.term.Literal(template_value)
                p2 = self._distinct_between_template_constant_in_subjectmap(val=template_value)
                g2.add((s, p2, o2))
            elif "r2rml#class" in p:
                # type can be now provided more than once, that's why we need to iterate
                if isinstance(self.type, str):
                    self.type = [self.type]
                    self.logger.debug(f"{self.type=}")
                for tp in self.type:
                    o3 = self._parse_predicate(tp)
                    self.logger.debug(f"{o3=}")
                    g2.add((s, p, o3))
            else:
                g2.add((s, p, o))
        self._load_main_properties_into_graph(graph=g2, main_node=main_node,
                                              predicate_object_bnode=predicate_object_bnode)
        return g2

    def _load_complex_property(self, graph, key, value, predicate_object_bnode, main_node):
        """
        Semi-private function for generating triples for single property in the complex section.
        :param graph: Graph object -> graph.
        :param key: str -> key
        :param value: str -> value
        :param predicate_object_bnode: node -> predicate_object_bnode
        :param main_node: node -> main_node.
        """
        self.logger.info("Loading complex property into graph...")
        current_bnode = rdflib.term.BNode()
        self.logger.debug(f"{key=}")
        self.logger.debug(f"{value=}")
        template_column_or_constant = self._distinct_between_template_column_constant(value=value)
        self.logger.debug(f"{template_column_or_constant=}")
        datatype_predicate, datatype = match_predicate_with_datatype(value=value)
        if not datatype:
            datatype = self._resolve_datatype(value=value)
        self.logger.debug(f"{datatype_predicate=}")
        self.logger.debug(f"{datatype=}")
        resolved_value = self._resolve_value_if_needed(value=value)
        self.logger.debug(f"{resolved_value=}")

        self.logger.debug(f"{main_node=}")
        if not predicate_object_bnode:
            predicate_object_bnode = self._assign_object_bnode(graph=graph, main_node=main_node)

        graph.add((predicate_object_bnode,
                   rdflib.term.URIRef('http://www.w3.org/ns/r2rml#objectMap'),
                   current_bnode))

        if resolved_value:
            graph.add((current_bnode,
                       template_column_or_constant,
                       resolved_value))
        else:
            graph.add((current_bnode,
                       template_column_or_constant,
                       rdflib.term.Literal(parse_config_value(value).strip("<>"))))

        graph.add((current_bnode, datatype_predicate, datatype))
        graph.add((predicate_object_bnode,
                   rdflib.term.URIRef('http://www.w3.org/ns/r2rml#predicate'),
                   self._parse_predicate(key)))

    def _generate_core_of_complex_section(self, complex_type, subject_node_name, template_uri):
        """
        Semi-private function for generating core section for set of complex properties.
        :param complex_type: str/list -> type/types for the complex property.
        :param subject_node_name: str -> full name for subject node.
        :param template_uri: str -> template uri.
        :return: tuple consisting of graph object, predicate_object_bnode node and main node.
        """
        g = rdflib.Graph()
        g2 = rdflib.Graph()
        g.parse(self.template_complex_path, format='ttl')
        self.logger.info("Generating complex section...")
        self.logger.debug(f"{complex_type=}")
        #self.logger.debug(f"{self.mapping_filename=}")
        predicate_object_bnode = None
        for s, p, o in g:
            if 'filename_secondary' in s:
                s1 = rdflib.term.URIRef(f"#{subject_node_name}")
                main_node = s1
                if 'r2rml#predicateObjectMap' in p:
                    predicate_object_bnode = o
                g2.add((s1, p, o))
            elif '{filename}' in o:
                o1 = rdflib.term.Literal(f"{self.filename}")
                g2.add((s, p, o1))
            elif '{type}' in o:
                if isinstance(complex_type, str):
                    complex_type = [complex_type]
                for ctp in complex_type:
                    o2 = self._parse_predicate(ctp)
                    self.logger.debug(f"{o2=}")
                    g2.add((s, p, o2))
            elif '{template}' in o:
                if isinstance(template_uri, str):
                    template_uri = [template_uri]
                for tu in template_uri:
                    o3 = rdflib.term.Literal(tu)
                    self.logger.debug(f"{o3=}")
                    p3 = self._distinct_between_template_constant_in_subjectmap(val=tu)
                    g2.add((s, p3, o3))
            else:
                g2.add((s, p, o))
        return g2, predicate_object_bnode, main_node
