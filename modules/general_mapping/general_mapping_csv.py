import os
import rdflib
import re

from modules.general_mapping.general_mapping_base import GeneralMappingGenerator
from modules.utils.utils import match_predicate_with_datatype, parse_config_value


class GeneralMappingGeneratorCsv(GeneralMappingGenerator):
    """
    Class that handles generating general mapping solution for the Generic Pipeline.
    """
    def __init__(self, config_path, file_abs_path, base_uri):
        super().__init__(config_path=config_path, base_uri=base_uri)
        # BASE ATTRS
        self.file_abs_path = file_abs_path
        # TEMPLATES ATTRS
        self.template_path = os.path.join("statics", "templates", "general_mapping", "csv")
        self.template_main_file = "main.ttl"
        self.template_secondary_file = "complex.ttl"
        self.template_main_path = os.path.join(self.template_path, self.template_main_file)
        self.template_complex_path = os.path.join(self.template_path, self.template_secondary_file)

    ###############################################################################
    #                               MAIN METHODS (CSV SPECIFIC) .                 #
    ###############################################################################

    def generate_mapping(self, mapping_full_path):
        """
        Main function that takes care of generating the whole new mapping based on the config file
        provided by the user.
        :param: mapping_full_path: str, full path to the mapping file.
        :return: Graph object -> full graph object that can be serialized.
        """
        self.logger.info("### GENERATING MAPPING... ###")
        root_graph = rdflib.Graph(base=f"file://{mapping_full_path}")

        graph = self._generate_main_section(graph=root_graph)
        graph += self._generate_all_complex_sections()
        graph = self._update_graph_with_prefixes(graph)

        return graph

    ###############################################################################
    #                               AUXILIARY METHODS (CSV SPECIFIC) .            #
    ###############################################################################

    @staticmethod
    def _distinct_between_template_column_constant(value):
        """
        Function that distinct between predicates based on given value for csv mapping.
        :param value: input value from which predicate will be derived.
        :return: URIRef for a predicate.
        """
        val = re.split("[|]", value)[0]
        if "<" and ">" in val:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#constant')
        elif "{" and "}" in val:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#template')
        elif "`" in val and "{" not in val:
            return rdflib.term.URIRef('http://semweb.mmlab.be/ns/rml#reference')
        else:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#constant')

    @staticmethod
    def _distinct_between_template_constant_in_subjectmap(val):
        """
        Function that distinct between predicates based on given value for core section of the mapping in subjectMap.
        :param value: input value from which predicate will be derived.
        :return: URIRef for a predicate.
        """
        if "{" and "}" in val:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#template')
        else:
            return rdflib.term.URIRef('http://www.w3.org/ns/r2rml#constant')

    def _load_main_properties_into_graph(self, graph, main_node, predicate_object_bnode):
        """
        Semi-private helper function that loads properties from a config file into a graph.
        :param graph: Graph object -> graph.
        """
        def _load_property(property_key, property_val, predicate_object_bnd):
            self.logger.debug(f"{property_val=}")
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

            if 'reference' in template_column_or_constant:
                graph.add((current_bnode,
                           template_column_or_constant,
                           rdflib.term.Literal(parse_config_value(property_val).strip("`"))))
            else:
                if resolved_value:
                    graph.add((current_bnode,
                               template_column_or_constant,
                               resolved_value))
                else:
                    graph.add((current_bnode,
                               template_column_or_constant,
                               rdflib.term.Literal(parse_config_value(property_val).strip("<>").replace("`", ""))))

            graph.add((current_bnode, datatype_predicate, datatype))

        # Load properties from config
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

    def _generate_main_section(self, graph):
        """
        Semi-private helper function that generates a main section for the mapping.
        :param graph: Graph object -> graph.
        :return: Graph object -> new graph object.
        """
        g = rdflib.Graph()
        g2 = graph
        g.parse(self.template_main_path, format='ttl')
        self.logger.info("Generating main section...")
        template_value = self.base_uri + "/" + self.template_id
        self.logger.debug(f"{template_value=}")
        #self.logger.debug(f"{self.mapping_filename=}")
        for s, p, o in g:
            if 'filename_main' in s:
                s1 = rdflib.term.URIRef(f"#{self.main_section_name}")
                main_node = s1
                if "r2rml#predicateObjectMap" in p:
                    predicate_object_bnode = o
                g2.add((s1, p, o))
            elif '{filename}' in o:
                #o1 = rdflib.term.Literal(f"{self.mapping_filename}")
                o1 = rdflib.term.Literal("iterator")
                g2.add((s, p, o1))
            elif '{file_path}' in o:
                o1a = rdflib.term.Literal(f"{self.file_abs_path}")
                g2.add((s, p, o1a))
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
        self.logger.debug(f"{key=}")
        self.logger.debug(f"{value=}")
        current_bnode = rdflib.term.BNode()
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

        if 'reference' in template_column_or_constant:
            graph.add((current_bnode,
                       template_column_or_constant,
                       rdflib.term.Literal(parse_config_value(value).strip("`"))))
        else:
            if resolved_value:
                graph.add((current_bnode,
                           template_column_or_constant,
                           resolved_value))
            else:
                graph.add((current_bnode,
                           template_column_or_constant,
                           rdflib.term.Literal(parse_config_value(value).strip("<>").replace("`", ""))))

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
                #o1 = rdflib.term.Literal(f"{self.mapping_filename}")
                o1 = rdflib.term.Literal("iterator")
                g2.add((s, p, o1))
            elif '{file_path}' in o:
                o1a = rdflib.term.Literal(f"{self.file_abs_path}")
                g2.add((s, p, o1a))
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
                    tu = tu.replace("`", "")
                    o3 = rdflib.term.Literal(tu)
                    self.logger.debug(f"{o3=}")
                    p3 = self._distinct_between_template_constant_in_subjectmap(val=tu)
                    g2.add((s, p3, o3))
            else:
                g2.add((s, p, o))
        return g2, predicate_object_bnode, main_node
