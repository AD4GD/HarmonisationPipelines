import yaml
import os
import rdflib
import logging
import datetime
import sys
import re
import copy

from modules.utils.utils import generate_missing_uri, open_context_url, validate_uriref, is_key_enum_entry, is_it_enum
from modules.dictionaries.dictionaries import default_namespaces
from modules.general_mapping.general_mapping_settings import CONFIG_PROPERTIES_DEPTH, CONFIG_SPECIAL_KEYWORDS


class GeneralMappingGenerator(object):
    """
    Class that handles generating general mapping solution for the Generic Pipeline.
    """
    def __init__(self, config_path, base_uri):
        """
        :param config_path: str -> path to the config file.
        :param mapping_filename: str -> name for the mapping file that will be generated.
        :param base_uri: str -> base URI.
        """
        # BASE ATTRS
        self.config = config_path
        #self.mapping_filename = mapping_filename
        self.base_uri = base_uri
        # CONFIG ATTRS
        self.context = None
        self.context_type = None
        self.context_dict = {}
        self.default_namespace = "https://w3id.org/dpi/default-context/"
        self.template_id = None
        self.main_section = None
        self.main_type = {}
        self.complex_type = {}
        self.type = None
        self.valid_config = True
        self.main_section_name = "main"
        self.config_keywords = CONFIG_SPECIAL_KEYWORDS

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_general_mapping'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    ###############################################################################
    #                               MAIN METHODS .                                #
    ###############################################################################

    def load_cfg(self):
        """
        Function that loads config file in order to set an array of attributes.
        """
        self.logger.info("### LOADING CFG... ###")
        with open(self.config) as file:
            cfg = yaml.load(file, Loader=yaml.FullLoader)
            self.context = cfg['cfg'].get('CONTEXT')
            self.logger.debug(f"{self.context=}")
            self._recognize_context_type()
            self.logger.debug(f"{self.context_type=}")
            self.logger.debug(f"{self.context_dict=}")

            self.template_id = cfg['cfg'].get('TEMPLATE_ID')
            self.logger.debug(f"{self.template_id=}")
            self.main_section = cfg['cfg'].get('MAIN TYPE')
            self.logger.debug(f"{self.main_type=}")
            self.type = self.main_section.get("@type")
            self.logger.debug(f"{self.type=}")
            required_fields = (self.template_id, self.main_section)
            if any(field is None for field in required_fields):
                self.logger.error("Invalid config! Template_id or main section are missing!")
                self.valid_config = False
        if not self.valid_config:
            msg = "Invalid config for mapping generation. Aborting. Please inspect logs to get" \
                  " more details!"
            raise SystemExit(msg)

    def update_types(self, adjust_template_id=False):
        """
        Function that updates two dictionaries: main_type and complex_type with values that
        were parsed from the config file.
        :param: adjust_template_id: bool -> True only for CSV input type, False otherwise.
        """
        self.logger.info("### UPDATING TYPES... ###")
        if adjust_template_id:
            self.logger.info("Adjusting template_id...")
            self._adjust_template_id()
        self.logger.debug(f"{self.main_section=}")
        # adjusting dictionary in case there is enumerator so that in can be processed
        adjusted_dict = self.rename_enum_keys(dct=self.main_section)
        self.logger.debug(f"{adjusted_dict=}")
        self.main_type = adjusted_dict
        for key, value in self.main_type.items():
            if isinstance(value, str):
                self.logger.debug("SIMPLE ONE; key value pair")
                self.logger.debug(f"{key=}")
                self.logger.debug(f"{value=}")
                self.main_type.update({key: value})
            elif isinstance(value, dict):
                self.logger.debug("COMPLEX ONE; key value pair")
                self.logger.debug(f"{key=}")
                self.logger.debug(f"{value=}")
                # filling missing uri values recursively
                self.fill_missing_uris(value, prev_key=key, template_id=self.template_id)
                updated_value = self.main_type.get(key)
                self.logger.debug(f"{updated_value=}")
                self.main_type.update({key: updated_value.get("uri")})
                self.logger.debug(f"{self.main_type=}")
                self.complex_type.update({key: updated_value})
                self.logger.debug(f"{self.complex_type=}")

    ###############################################################################
    #                               AUXILIARY METHODS .                           #
    ###############################################################################

    @staticmethod
    def rename_enum_keys(dct):
        """
        Function that renames and re-adjusts input dictionary in cases where user's input was an enumerator.
        :param: dct: -> dictionary
        """
        new_dct = copy.deepcopy(dct)
        new_dct_final = copy.deepcopy(dct)

        def stripper(data):
            new_data = {}
            for k, v in data.items():
                if isinstance(v, dict):
                    v = stripper(v)
                if v not in (u'', {}):
                    new_data[k] = v
            return new_data

        def add_keys_nested_dict(d, keys, value):
            if len(keys) == 1:
                d.setdefault(keys[0], value)
            else:
                key = keys[0]
                if key not in d:
                    d[key] = {}
                add_keys_nested_dict(d[key], keys[1:], value)

        def del_by_path(d, keys):
            for k in keys[:-1]:
                d = d[k]
            return d.pop(keys[-1])

        def recurse(dct_rec, parent):
            for k, v in dct_rec.items():
                if is_it_enum(k):
                    # add fixed iterator
                    new_key = f"{parent[-1]}_{k.split('@')[-1]}"
                    use_path = []
                    for x in parent[:-1]:
                        use_path.append(x)
                    use_path.append(new_key)
                    add_keys_nested_dict(new_dct_final, use_path, v)
                    # remove iterator
                    old_iterator = list()
                    old_iterator.append(k)
                    use_path = parent + old_iterator
                    del_by_path(new_dct_final, use_path)
                if isinstance(v, dict):
                    parent.append(k)
                    recurse(v, parent)
                    if len(parent) != 0:
                        parent.pop()

        recurse(new_dct, [])
        new_dct_final = stripper(new_dct_final)
        return new_dct_final

    def fill_missing_uris(self, dct, prev_key, template_id):
        """
        Function that fills URI values across input dictionary in every case where URI was not provided.
        :param: dct: -> dictionary, input
        :param: prev_key -> str, previous key name
        :param: template_id -> str, template id
        """
        for key, value in dct.items():
            if key == "uri":
                if value is None:
                    dct["uri"] = generate_missing_uri(base_uri=self.base_uri, template_id=template_id, key=prev_key)
            elif isinstance(value, dict):
                self.fill_missing_uris(value, prev_key=key, template_id=template_id + "/" + prev_key)

    def _adjust_template_id(self):
        """
        Semi-private function that gets rid of illegal characters provided in config that are not suitable for csv
        transformation.
        """
        self.template_id = self.template_id.replace("`", "")

    def _recognize_context_type(self):
        """
        Semi-private helper function that sets up proper context information based on what was provided in the config
        file.
        """
        if not self.context:
            e = "Config file error! CONTEXT was not provided or missing!"
            self.logger.critical(e)
            raise SystemExit(e)
        if isinstance(self.context, str):
            self.context = [self.context]
            self.context_type = "SIMPLE"
        elif isinstance(self.context, list):
            self.context_type = "SIMPLE"
            self.logger.debug(f"initial context: {self.context=}")
            for context_url in self.context:
                self.logger.debug(f"{context_url=}")
                if not isinstance(context_url, str):
                    self.context_type = "COMPLEX"
                    self.context_dict.update(context_url)
            self.context[:] = [context_elem for context_elem in self.context if isinstance(context_elem, str)]
            self.logger.debug(f"updated context: {self.context=}")
        else:
            e = f"Config file error! CONTEXT type not recognized, expected single value, or list of values, got " \
                f"{type(self.context)} instead!"
            raise SystemExit(e)

    def _recognize_type(self):
        """
        Semi-private helper function that recognizes if there is only one type or multiple types and sets attributes
        accordingly
        """
        if not self.type:
            self.valid_config = False
            e = "Invalid config file! @type is missing in the MAIN TYPE section."
            self.logger.error(e)
            raise SystemExit(e)
        if isinstance(self.type, str):
            self.type = [self.type]
            self.logger.debug(f"{self.type=}")
        elif isinstance(self.type, list):
            return
        else:
            e = f"Config file error! @type not recognized, expected single value, or list of values, got " \
                f"{type(self.context)} instead!"
            raise SystemExit(e)

    def _match_value_with_namespace(self, value):
        """
        Semi-private function that matches value with appropriate namespace coming from context.
        """
        if self.context_type == "SIMPLE":
            return self._extract_ns_from_context(value=value)
        elif self.context_type == "COMPLEX":
            # first check if uri is provided in the custom dictionary from yaml
            uri = self.context_dict.get(value)
            if uri:
                return dict({"uri": uri})
            else:
                return self._extract_ns_from_context(value=value)
        else:
            e = "Unrecognized CONTEXT type. Check logs for more info!"
            self.logger.info(e)
            self.logger.debug(f"CONTEXT_TYPE IS SET TO: {self.context_type}")
            raise SystemExit(e)

    def _extract_ns_from_context(self, value):
        """
        Semi-private function for extracting namespace from simple or complex context type.
        """
        vocab = None
        for context_url in self.context:
            self.logger.debug(f"{context_url=}")
            context_json = open_context_url(context_url)
            ns_dict = context_json.get("@context").get(value)
            if ns_dict:
                try:
                    uri = ns_dict.get("@id")
                    return dict({"uri": uri})
                except AttributeError:
                    if ns_dict == "@type":
                        return dict({"uri": default_namespaces.get("rdf").strip("<>") + "type"})
                    else:
                        msg = "Unexpected error parsing json-ld context file provided in the config. Check logs for " \
                              "more details!"
                        raise SystemExit(msg)
            # namespace was not found in json, save vocab default value for further usage
            else:
                if not vocab:
                    vocab = context_json.get("@context").get("@vocab")
        return dict({"vocab": vocab})

    def _update_graph_with_prefixes(self, graph):
        """
        Semi-private helper function that updates a Graph object with prefixes coming
        from a config file.
        :param graph: Graph object -> graph.
        :return: Graph object -> updated graph.
        """
        self.logger.info("Updating prefixes")
        for key, value in default_namespaces.items():
            self.logger.debug(f"{key=}")
            self.logger.debug(f"{value=}")
            graph.namespace_manager.bind(key, value.strip("<>"))
        return graph

    def _parse_predicate(self, value):
        """
        Semi-private helper function that parses a given value in order to create legit URIRef
        for the predicate.
        :param value: str -> value that will be parsed.
        :return: URIRef object -> uri.
        """
        # adjusting key in case it was detected as name associated with enum
        if is_key_enum_entry(value):
            value = value.split("_")[0]
        # case when type is used as a special keyword
        if value == "@type":
            namespace = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
            # change value to regular word to apply for legal URI
            value = "type"
            uri = rdflib.term.URIRef(namespace + value)
        else:
            uri = self._match_value_with_namespace(value).get("uri")
            if uri:
                uri = rdflib.term.URIRef(uri)
            else:
                namespace = rdflib.Namespace(self._match_value_with_namespace(value).get("vocab"))
                if not namespace:
                    # if there was no vocab value in the CONTEXT we use default namespace
                    namespace = self.default_namespace
                uri = rdflib.term.URIRef(namespace + value)
        return uri

    @staticmethod
    def _assign_object_bnode(graph, main_node):
        """
        Semi-private helper function that assigns object bnode and creates an associated triple in the graph.
        :param graph: Graph object -> graph.
        :param main_node: node object that will be used as a predicate to generate triple.
        """
        predicate_object_bnode = rdflib.term.BNode()
        graph.add((main_node,
                   rdflib.term.URIRef('http://www.w3.org/ns/r2rml#predicateObjectMap'),
                   predicate_object_bnode))
        return predicate_object_bnode

    def _resolve_value_if_needed(self, value):
        """
        Semi-private helper function that resolves value if there is no datatype associated with it, and it is not
        already an url.
        """
        if value.startswith("http"):
            # resolving is not needed
            return False
        val = re.split("[|]", value)
        if len(val) > 1:
            # resolving is not needed
            return False
        else:
            # validation for value provided by the user, if it can't be serialized properly we throw an error
            if validate_uriref(uri_candid=value):
                return self._parse_predicate(value=value)

    def _resolve_datatype(self, value):
        """
        Semi-private function for resolving datatype if it is not a standard one.
        """
        val = re.split("[|]", value)[-1].strip("<>")
        if validate_uriref(uri_candid=val):
            uri = self._match_value_with_namespace(val).get("uri")
            if uri:
                uri = rdflib.term.URIRef(uri)
            else:
                namespace_candid = self._match_value_with_namespace(value).get("vocab")
                if namespace_candid:
                    namespace = rdflib.Namespace(namespace_candid)
                else:
                    # if there was no vocab value in the CONTEXT we use default namespace
                    namespace = self.default_namespace
                uri = rdflib.term.URIRef(namespace + val)
            return uri

    def _generate_all_complex_sections(self):
        """
        Semi-private helper function that generates all complex sections needed for the mapping
        based on the config.
        :return: Graph object -> new graph object.
        """
        g = rdflib.Graph()
        self.logger.info("Generating all complex sections...")
        for key, value in self.complex_type.items():
            self.logger.debug(f"{key=}")
            self.logger.debug(f"{value=}")
            complex_type = self.complex_type[key].get("@type")
            self.logger.debug(f"{complex_type=}")
            template_uri = self.complex_type[key].get("uri")
            self.logger.debug(f"{template_uri=}")
            if complex_type:
                complex_dict = self.complex_type[key]
                adjusted_key = "_" + key
                self._generate_complex_sections_iteratively(complex_dict=complex_dict,
                                                            template_uri=template_uri, key=adjusted_key,
                                                            graph=g)
            else:
                self.logger.info(f"Config error. Type was not specified for the complex type: {key}!")
                return
        return g

    def _generate_complex_sections_iteratively(self, complex_dict, template_uri, graph, key,
                                               depth=CONFIG_PROPERTIES_DEPTH):
        """
        Semi-private function for iteratively generating all sections and properties for the complex part of the config.
        :param complex_dict: dict -> dictionary containing information about complex properties.
        :param template_uri: str -> uri that will be used as template.
        :param graph: Graph object -> graph.
        :param key: str -> key
        :param depth: int -> max depth that recursion will go before throwing an error.
        :returns: Graph object -> result graph.
        """
        def recurse(g, dct, uri, level, p_key):
            self.logger.debug("~~~~~ CORE LEVEL OF RECURSION ~~~~~~")
            self.logger.debug(f"{p_key=}")
            self.logger.debug(f"{dct=}")
            complex_type = dct.get("@type")
            if not complex_type:
                self.logger.info(f"Config error. Type was not specified for the complex type: {dct.keys()}!")
                return
            self.logger.debug(f"{self.template_id=}")
            #subject_node_name = f"{self.mapping_filename}_{self.main_section_name}{p_key}"
            subject_node_name = f"{self.main_section_name}{p_key}"
            self.logger.debug(f"{subject_node_name=}")
            g2, predicate_object_bnode, main_node = self._generate_core_of_complex_section(complex_type=complex_type,
                                                                                           subject_node_name=
                                                                                           subject_node_name,
                                                                                           template_uri=uri)
            g += g2
            for key, value in dct.items():
                if key not in self.config_keywords:
                    self.logger.debug("~~~~~ ITEMS LEVEL OF RECURSION ~~~~~~")
                    self.logger.info(f"Generating complex section for {key} property...")
                    self.logger.debug(f"{key=}")
                    self.logger.debug(f"{value=}")
                    if isinstance(value, dict):
                        self.logger.debug(f"{value=}")
                        uri = value.get("uri")
                        self.logger.debug(f"{uri=}")
                        self.logger.debug(f"{g=}")
                        self.logger.debug(f"{predicate_object_bnode=}")
                        self._load_complex_property(graph=g, key=key, value=uri,
                                                    predicate_object_bnode=predicate_object_bnode,
                                                    main_node=main_node)
                        # erasing the predicate_object_bnode
                        predicate_object_bnode = None
                        level = level - 1
                        self.logger.debug(f"{level=}")
                        updated_key = p_key + "_" + key
                        self.logger.debug(updated_key)
                        if level > 0:
                            recurse(g=g, dct=value, uri=uri, level=level, p_key=updated_key)
                        else:
                            msg = f"Complex attributes from config reached maximum deepness = {depth}"
                            sys.exit(msg)
                    else:
                        self.logger.debug(f"{g=}")
                        if isinstance(value, str):
                            value = [value]
                        for val in value:
                            self.logger.debug(f"{val=}")
                            self._load_complex_property(graph=g, key=key, value=val,
                                                        predicate_object_bnode=predicate_object_bnode,
                                                        main_node=main_node)
                            # erasing the predicate_object_bnode
                            predicate_object_bnode = None
            self.logger.debug(f"{level=}")

        self.logger.info("recursion starts...")
        self.logger.debug(f"{complex_dict=}")
        recurse(g=graph, dct=complex_dict, uri=template_uri, level=depth, p_key=key)
        self.logger.debug("final graph...")
        self.logger.debug(f"{graph=}")
        return graph
