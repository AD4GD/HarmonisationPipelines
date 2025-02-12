import os
import logging
import datetime

import rdflib

from modules.fadn import fadn
from modules.dictionaries import dictionaries


class FadnMapping(fadn.Fadn):
    """
    Subclass of Fadn that deals with creation of mappings for FADN data.
    """
    def __init__(self, results_dir):
        super().__init__(results_dir=results_dir)
        self.directory = os.path.join('statics', 'templates', 'mappings')
        self.main_dictionary = dictionaries.mapping_dictionary

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_fadn_mappings_'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    # PIPELINE OPERATIONS

    def create_mapping(self):
        """
        The main function that executes mapping creation for each package present in the data.
        """
        print('########## Creating mappings for all packages...')
        self.set_date()   # setting proper data based on the filename.
        packages = os.listdir(self.destination_path)
        os.mkdir(os.path.join(self.results_dir, 'mappings'))   # creating folder where mappings will be stored.
        for package in packages:
            print(f'Creating mapping for {package} package...')
            root_graph = self._dataset_mapping(package_name=package)
            org_graph = self._organisation_mapping(package_name=package)
            ds_graph = self._datastructure_mapping(package_name=package)
            dim_graph = self._dimensions_mapping(package_name=package)
            measures_graph = self._measures_mapping(package_name=package)
            obs_graph = self._observations_mapping(package_name=package)
            sk_graph = self._slicekey_mapping(package_name=package)
            slices_graph = self._slices_mapping(package_name=package)
            root_graph += org_graph
            root_graph += ds_graph
            root_graph += dim_graph
            root_graph += measures_graph
            root_graph += obs_graph
            root_graph += sk_graph
            root_graph += slices_graph
            if 'ANC3' in package:
                anc3_graph = self._anc3_mapping(package_name=package)
                root_graph += anc3_graph
            if 'SIZ6' in package:
                siz6_graph = self._siz6_mapping(package_name=package)
                root_graph += siz6_graph
            if 'SIZC' in package:
                sizc_graph = self._sizc_mapping(package_name=package)
                root_graph += sizc_graph
            if 'TF_GEN1' in package:
                gen1_graph = self._tf_gen1_mapping(package_name=package)
                root_graph += gen1_graph
            if 'TF_PRIN2' in package:
                prin2_graph = self._tf_prin2_mapping(package_name=package)
                root_graph += prin2_graph
            if 'TF_SUBP4' in package:
                subp4_graph = self._tf_subp4_mapping(package_name=package)
                root_graph += subp4_graph
            if 'TF8' in package:
                tf8_graph = self._tf8_mapping(package_name=package)
                root_graph += tf8_graph
            if 'TF14' in package:
                tf14_graph = self._tf14_mapping(package_name=package)
                root_graph += tf14_graph
            self.save_graph(graph=root_graph, package_name=package)

    # HELPER FUNCTIONS

    def save_graph(self, graph, package_name):
        """
        Helper function that saves Graph object into Turtle file with appropriate naming based on the
        package name.
        :param graph: Graph object.
        :param package_name: str -> name of the package.
        """
        specifics = package_name.lower().split('.')
        filename = f'mapping-'
        if len(specifics) == 2:
            filename += f'{specifics[0]}-{specifics[1]}-{self.year}.ttl'
        elif len(specifics) == 3:
            filename += f'{specifics[0]}-{specifics[1]}-{specifics[2]}-{self.year}.ttl'
        elif len(specifics) == 4:
            filename += f'{specifics[0]}-{specifics[1]}-{specifics[2]}-{specifics[3]}-{self.year}.ttl'
        elif len(specifics) == 5:
            filename += f'{specifics[0]}-{specifics[1]}-{specifics[2]}-{specifics[3]}-{specifics[4]}-{self.year}.ttl'
        else:
            self.logger.info(f'Number of specifics for package: {package_name} is invalid!')

        file_path = os.path.join(self.results_dir, 'mappings', filename)
        with open(file_path, 'w') as f:
            #f.write(graph.serialize(format='ttl').decode('utf-8'))
            # above line commented due to the change in rdflib!
            f.write(graph.serialize(format='ttl'))

    # MAPPINGS

    def _dataset_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing
        all the triples for the dataset part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for dataset_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'dataset_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.dataset')   # setting up target namespace.
        aux_ns = rdflib.Namespace(f'#{package_name}.slices')   # setting up auxiliary namespace used in dataset part.
        target_csv = f'{package_name.lower()}.dataset_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            elif 'r2rml#parentTriplesMap' in p:
                o2 = rdflib.term.URIRef(aux_ns)
                g2.add((s, p, o2))
            else:
                g2.add((s, p, o))
        return g2

    def _organisation_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples
        for the organisation part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'organisation_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.organisation')   # setting up target namespace.
        target_csv = f'{package_name.lower()}.organisation_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _datastructure_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples
        for the datastructure part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'datastructure_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.datastructure')   # setting up target namespace.
        aux_ns = rdflib.Namespace(f'#{package_name}.measures')  # setting up auxiliary namespace.
        target_csv = f'{package_name.lower()}.datastructure_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            elif 'measures_ns' in o:
                o2 = rdflib.term.URIRef(aux_ns)
                g2.add((s, p, o2))
            else:
                g2.add((s, p, o))
        return g2

    def _dimensions_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the dimensions part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'dimensions_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.dimensions')   # setting up target namespace.
        target_csv = f'{package_name.lower()}.dimensions_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _measures_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for the
        measures part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'measures_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.measures')   # setting up target namespace.
        target_csv = f'{package_name.lower()}.measures_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _observations_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples
        for the observations part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'observations_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.observations-fixed-codes')   # setting up target namespace.
        aux_ns = rdflib.Namespace(f'#{package_name}.dataset')  # setting up auxiliary namespace.
        target_csv = f'{package_name}_preprocessed_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # specifics of a what the package contains.
        specifics = package_name.lower().split('.')
        specifics_up = package_name.split('.')
        cr = ''   # variable that will store information if the package aligns with country or region.
        if 'country' in specifics[1]:
            cr += 'Country'
        elif 'region' in specifics[1]:
            cr += 'Region'
        else:
            self.logger.info(f'Observations mapping issue for. Could not find neither refRegion nor refCountry!')

        # additional variables that are necessary for this particular mapping.
        iterator = f'{package_name}.observations-fixed-codes'
        cr_ns = rdflib.Namespace(f'#ref{cr}')
        a_var = f'http://w3id.org/foodie/fadn/{package_name.lower().replace(".", "-")}#{{{specifics_up[0]}}}'
        b_var = f'{{{specifics_up[0]}}} {{{specifics_up[1]}}}'
        c_var = f'http://nuts.geovocab.org/id/{{{specifics_up[1]}CODE}}'
        if len(specifics) == 2:
            a_var += f'-{{{specifics_up[1]}CODE}}'
        elif len(specifics) == 3:
            a_var += f'_{{{specifics_up[2]}CODE}}-{{{specifics_up[1]}CODE}}'
            b_var += f' {{{specifics_up[2]}}}'
        elif len(specifics) == 4:
            a_var += f'_{{{specifics_up[2]}CODE}}_{{{specifics_up[3]}CODE}}-{{{specifics_up[1]}CODE}}'
            b_var += f' {{{specifics_up[2]}}} {{{specifics_up[3]}}}'
        elif len(specifics) == 5:
            a_var += f'_{{{specifics_up[2]}CODE}}_{{{specifics_up[3]}CODE}}_{{{specifics_up[4]}CODE}}-' \
                     f'{{{specifics_up[1]}CODE}}'
            b_var += f' {{{specifics_up[2]}}} {{{specifics_up[3]}}} {{{specifics_up[4]}}}'

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            elif 'rml#iterator' in p:
                o2 = rdflib.term.Literal(iterator)
                g2.add((s, p, o2))
            elif 'dataset_ns' in o:
                o3 = rdflib.term.URIRef(aux_ns)
                g2.add((s, p, o3))
            elif 'a_temp' in o:
                o4 = rdflib.term.Literal(a_var)
                g2.add((s, p, o4))
            elif 'b_temp' in o:
                o5 = rdflib.term.Literal(b_var)
                g2.add((s, p, o5))
            elif 'c_temp' in o:
                o6 = rdflib.term.Literal(c_var)
                g2.add((s, p, o6))
            elif 'refGEO' in o and 'r2rml#constant' in p:
                o7 = rdflib.term.URIRef(cr_ns)
                g2.add((s, p, o7))
            else:
                g2.add((s, p, o))
        return g2

    def _slicekey_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the slicekey part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'slicekey_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.slicekey')   # setting up target namespace.
        target_csv = f'{package_name.lower()}.slicekey_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _slices_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the slices part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # 1st part - Creating a vanilla slices mapping.

        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'slices_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.slices')   # setting up target namespace.
        # setting up auxiliary namespaces.
        aux_ns = rdflib.Namespace(f'#{package_name}.slicekey')
        aux2_ns = rdflib.Namespace(f'#{package_name}.observations-fixed-codes')
        target_csv = f'{package_name.lower()}.slices_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # specifics of a what the package contains.
        specifics = package_name.lower().split('.')
        specifics_up = package_name.split('.')

        # additional variables that are necessary for this particular mapping.
        a_var = f'http://w3id.org/foodie/fadn/{package_name.lower().replace(".", "-")}#{{{specifics_up[0]}}}'
        b_var = f'slice with {{{specifics_up[0]}}}'
        if len(specifics) == 3:
            a_var += f'_{{{specifics_up[2]}CODE}}'
            b_var += f' and {{{specifics_up[2]}}}'
        elif len(specifics) == 4:
            a_var += f'_{{{specifics_up[2]}CODE}}_{{{specifics_up[3]}CODE}}'
            b_var += f', {{{specifics_up[2]}}} and {{{specifics_up[3]}}}'
        elif len(specifics) == 5:
            a_var += f'_{{{specifics_up[2]}CODE}}_{{{specifics_up[3]}CODE}}_{{{specifics_up[4]}CODE}}'
            b_var += f', {{{specifics_up[2]}}}, {{{specifics_up[3]}}} and {{{specifics_up[4]}}}'

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            elif 'a_temp' in o:
                o2 = rdflib.term.Literal(a_var)
                g2.add((s, p, o2))
            elif 'b_temp' in o:
                o3 = rdflib.term.Literal(b_var)
                g2.add((s, p, o3))
            elif 'slicekey_ns' in o:
                o4 = rdflib.term.URIRef(aux_ns)
                g2.add((s, p, o4))
            elif 'observations_ns' in o:
                o5 = rdflib.term.URIRef(aux2_ns)
                g2.add((s, p, o5))
            else:
                g2.add((s, p, o))

        # If there is no additions based on the package name function is returning existing Graph.
        if len(specifics) == 2:
            return g2
        else:
            # 2nd part - Adding package specifics to the slices mapping.

            # Instantiating namespaces that will be used in new Nodes.
            pom = rdflib.Namespace('http://www.w3.org/ns/r2rml#predicateObjectMap')
            pm = rdflib.Namespace('http://www.w3.org/ns/r2rml#predicateMap')
            om = rdflib.Namespace('http://www.w3.org/ns/r2rml#objectMap')
            constant = rdflib.Namespace('http://www.w3.org/ns/r2rml#constant')
            ptm = rdflib.Namespace('http://www.w3.org/ns/r2rml#parentTriplesMap')
            jc = rdflib.Namespace('http://www.w3.org/ns/r2rml#joinCondition')
            child = rdflib.Namespace('http://www.w3.org/ns/r2rml#child')
            parent = rdflib.Namespace('http://www.w3.org/ns/r2rml#parent')

            # Finding certain nodes in Graph in order to extend a set of triples.
            anode_x = ''
            anode_y = ''
            for s, p, o in g2:
                if 'child' in p and 'YEAR' in o:
                    anode_x += s
            for s, p, o in g2:
                if anode_x in o and 'joinCondition' in p:
                    anode_y += s
            if anode_x == '' or anode_y == '':
                self.logger.debug(f'Nodes required for extending triple were not found for package {package_name}!')
            else:
                if len(specifics) == 3:
                    # Instantiating BNodes that will be used in extending existing Graph.
                    anode = rdflib.term.BNode('bNode#1')
                    anode2 = rdflib.term.BNode('bNode#2')
                    anode3 = rdflib.term.BNode('bNode#3')
                    anode4 = rdflib.term.BNode('bNode#4')
                    enode = rdflib.term.BNode('bNode#101')
                    # Instantiating namespaces specific to the package.
                    specific_ref = rdflib.Namespace(f'#ref{specifics[2].capitalize()}')
                    # Creating additional namespace/namespaces based on package specifics.
                    ns_appendix = self.main_dictionary[specifics_up[2]]
                    spec_ns = f'#{package_name}.{ns_appendix}'
                    # Extending Graph with #1 set of triples
                    g2.add((rdflib.URIRef(target_ns), rdflib.URIRef(pom), anode))
                    g2.add((anode, rdflib.URIRef(pm), anode2))
                    g2.add((anode, rdflib.URIRef(om), anode3))
                    g2.add((anode2, rdflib.URIRef(constant), rdflib.URIRef(specific_ref)))
                    g2.add((anode3, rdflib.URIRef(ptm), rdflib.URIRef(spec_ns)))
                    g2.add((anode3, rdflib.URIRef(jc), anode4))
                    g2.add((anode4, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[2]}')))
                    g2.add((anode4, rdflib.URIRef(parent), rdflib.Literal('label')))
                    # Extending set of triples with new nodes.
                    g2.add((rdflib.BNode(anode_y), rdflib.URIRef(jc), enode))
                    g2.add((enode, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[2]}')))
                    g2.add((enode, rdflib.URIRef(parent), rdflib.Literal(f'{specifics_up[2]}')))
                elif len(specifics) == 4:
                    # Instantiating BNodes that will be used in extending existing Graph.
                    anode = rdflib.term.BNode('bNode#1')
                    anode2 = rdflib.term.BNode('bNode#2')
                    anode3 = rdflib.term.BNode('bNode#3')
                    anode4 = rdflib.term.BNode('bNode#4')
                    anode5 = rdflib.term.BNode('bNode#5')
                    anode6 = rdflib.term.BNode('bNode#6')
                    anode7 = rdflib.term.BNode('bNode#7')
                    anode8 = rdflib.term.BNode('bNode#8')
                    enode = rdflib.term.BNode('bNode#101')
                    enode2 = rdflib.term.BNode('bNode#102')
                    # Instantiating namespaces specific to the package.
                    specific_ref = rdflib.Namespace(f'#ref{specifics[2].capitalize()}')
                    specific_ref_2 = rdflib.Namespace(f'#ref{specifics[3].capitalize()}')
                    # Creating additional namespace/namespaces based on package specifics.
                    ns_appendix = self.main_dictionary[specifics_up[2]]
                    ns_appendix2 = self.main_dictionary[specifics_up[3]]
                    spec_ns = f'#{package_name}.{ns_appendix}'
                    spec_ns2 = f'#{package_name}.{ns_appendix2}'
                    # extending Graph with #1 set of triples
                    g2.add((rdflib.URIRef(target_ns), rdflib.URIRef(pom), anode))
                    g2.add((anode, rdflib.URIRef(pm), anode2))
                    g2.add((anode, rdflib.URIRef(om), anode3))
                    g2.add((anode2, rdflib.URIRef(constant), rdflib.URIRef(specific_ref)))
                    g2.add((anode3, rdflib.URIRef(ptm), rdflib.URIRef(spec_ns)))
                    g2.add((anode3, rdflib.URIRef(jc), anode4))
                    g2.add((anode4, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[2]}')))
                    g2.add((anode4, rdflib.URIRef(parent), rdflib.Literal('label')))
                    # extending Graph with #2 set of triples
                    g2.add((rdflib.URIRef(target_ns), rdflib.URIRef(pom), anode5))
                    g2.add((anode5, rdflib.URIRef(pm), anode6))
                    g2.add((anode5, rdflib.URIRef(om), anode7))
                    g2.add((anode6, rdflib.URIRef(constant), rdflib.URIRef(specific_ref_2)))
                    g2.add((anode7, rdflib.URIRef(ptm), rdflib.URIRef(spec_ns2)))
                    g2.add((anode7, rdflib.URIRef(jc), anode8))
                    g2.add((anode8, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[3]}')))
                    g2.add((anode8, rdflib.URIRef(parent), rdflib.Literal('label')))
                    # Extending set of triples with new nodes.
                    g2.add((rdflib.BNode(anode_y), rdflib.URIRef(jc), enode))
                    g2.add((enode, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[2]}')))
                    g2.add((enode, rdflib.URIRef(parent), rdflib.Literal(f'{specifics_up[2]}')))
                    g2.add((rdflib.BNode(anode_y), rdflib.URIRef(jc), enode2))
                    g2.add((enode2, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[3]}')))
                    g2.add((enode2, rdflib.URIRef(parent), rdflib.Literal(f'{specifics_up[3]}')))
                elif len(specifics) == 5:
                    # Instantiating BNodes that will be used in extending existing Graph.
                    anode = rdflib.term.BNode('bNode#1')
                    anode2 = rdflib.term.BNode('bNode#2')
                    anode3 = rdflib.term.BNode('bNode#3')
                    anode4 = rdflib.term.BNode('bNode#4')
                    anode5 = rdflib.term.BNode('bNode#5')
                    anode6 = rdflib.term.BNode('bNode#6')
                    anode7 = rdflib.term.BNode('bNode#7')
                    anode8 = rdflib.term.BNode('bNode#8')
                    anode9 = rdflib.term.BNode('bNode#9')
                    anode10 = rdflib.term.BNode('bNode#10')
                    anode11 = rdflib.term.BNode('bNode#11')
                    anode12 = rdflib.term.BNode('bNode#12')
                    enode = rdflib.term.BNode('bNode#101')
                    enode2 = rdflib.term.BNode('bNode#102')
                    enode3 = rdflib.term.BNode('bNode#103')
                    # Instantiating namespaces specific to the package.
                    specific_ref = rdflib.Namespace(f'#ref{specifics[2].capitalize()}')
                    specific_ref_2 = rdflib.Namespace(f'#ref{specifics[3].capitalize()}')
                    specific_ref_3 = rdflib.Namespace(f'#ref{specifics[4].capitalize()}')
                    # Creating additional namespace/namespaces based on package specifics.
                    ns_appendix = self.main_dictionary[specifics_up[2]]
                    ns_appendix2 = self.main_dictionary[specifics_up[3]]
                    ns_appendix3 = self.main_dictionary[specifics_up[4]]
                    spec_ns = f'#{package_name}.{ns_appendix}'
                    spec_ns2 = f'#{package_name}.{ns_appendix2}'
                    spec_ns3 = f'#{package_name}.{ns_appendix3}'
                    # extending Graph with #1 set of triples
                    g2.add((rdflib.URIRef(target_ns), rdflib.URIRef(pom), anode))
                    g2.add((anode, rdflib.URIRef(pm), anode2))
                    g2.add((anode, rdflib.URIRef(om), anode3))
                    g2.add((anode2, rdflib.URIRef(constant), rdflib.URIRef(specific_ref)))
                    g2.add((anode3, rdflib.URIRef(ptm), rdflib.URIRef(spec_ns)))
                    g2.add((anode3, rdflib.URIRef(jc), anode4))
                    g2.add((anode4, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[2]}')))
                    g2.add((anode4, rdflib.URIRef(parent), rdflib.Literal('label')))
                    # extending Graph with #2 set of triples
                    g2.add((rdflib.URIRef(target_ns), rdflib.URIRef(pom), anode5))
                    g2.add((anode5, rdflib.URIRef(pm), anode6))
                    g2.add((anode5, rdflib.URIRef(om), anode7))
                    g2.add((anode6, rdflib.URIRef(constant), rdflib.URIRef(specific_ref_2)))
                    g2.add((anode7, rdflib.URIRef(ptm), rdflib.URIRef(spec_ns2)))
                    g2.add((anode7, rdflib.URIRef(jc), anode8))
                    g2.add((anode8, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[3]}')))
                    g2.add((anode8, rdflib.URIRef(parent), rdflib.Literal('label')))
                    # extending Graph with #3 set of triples
                    g2.add((rdflib.URIRef(target_ns), rdflib.URIRef(pom), anode9))
                    g2.add((anode9, rdflib.URIRef(pm), anode10))
                    g2.add((anode9, rdflib.URIRef(om), anode11))
                    g2.add((anode10, rdflib.URIRef(constant), rdflib.URIRef(specific_ref_3)))
                    g2.add((anode11, rdflib.URIRef(ptm), rdflib.URIRef(spec_ns3)))
                    g2.add((anode11, rdflib.URIRef(jc), anode12))
                    g2.add((anode12, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[4]}')))
                    g2.add((anode12, rdflib.URIRef(parent), rdflib.Literal('label')))
                    # Extending set of triples with new nodes.
                    g2.add((rdflib.BNode(anode_y), rdflib.URIRef(jc), enode))
                    g2.add((enode, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[2]}')))
                    g2.add((enode, rdflib.URIRef(parent), rdflib.Literal(f'{specifics_up[2]}')))
                    g2.add((rdflib.BNode(anode_y), rdflib.URIRef(jc), enode2))
                    g2.add((enode2, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[3]}')))
                    g2.add((enode2, rdflib.URIRef(parent), rdflib.Literal(f'{specifics_up[3]}')))
                    g2.add((rdflib.BNode(anode_y), rdflib.URIRef(jc), enode3))
                    g2.add((enode3, rdflib.URIRef(child), rdflib.Literal(f'{specifics_up[4]}')))
                    g2.add((enode3, rdflib.URIRef(parent), rdflib.Literal(f'{specifics_up[4]}')))

                return g2

    def _anc3_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the anc3 part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'anc3_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.anc3Values')   # setting up target namespace.
        target_csv = f'{package_name.lower()}.anc3Values_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _siz6_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the siz6 part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'siz6_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.siz6Values')   # setting up target namespace.
        target_csv = f'{package_name.lower()}.siz6Values_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _sizc_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the sizc part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()   # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'sizc_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.sizcValues')   # setting up target namespace.
        target_csv = f'{package_name.lower()}.sizcValues_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _tf_gen1_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the tf_gen1 part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()  # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'tf_gen1_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.gen1Values')  # setting up target namespace.
        target_csv = f'{package_name.lower()}.gen1Values_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _tf_prin2_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the tf_prin2 part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()  # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'tf_prin2_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.prin2Values')  # setting up target namespace.
        target_csv = f'{package_name.lower()}.prin2Values_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _tf_subp4_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the tf_subp4 part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()  # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'tf_subp4_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.subp4Values')  # setting up target namespace.
        target_csv = f'{package_name.lower()}.subp4Values_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _tf8_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the tf8 part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()  # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'tf8_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.tf8Values')  # setting up target namespace.
        target_csv = f'{package_name.lower()}.tf8Values_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2

    def _tf14_mapping(self, package_name):
        """
        Semi-private function that will create a graph containing all the triples for
        the tf14 part in a given package.
        :param package_name: str -> name of the package.
        :return: Graph object.
        """
        # initializing graph instances for organisation_template and the output graph that we will populate
        # with package specifics.
        g = rdflib.Graph()  # g is used to denote graph as per convention presented in rdflib documentation.
        g2 = rdflib.Graph(base=rdflib.Namespace('http://w3id.org/foodie/fadn#'))
        template_path = os.path.join(self.directory, 'tf14_template.ttl')
        g.parse(template_path, format='ttl')
        target_ns = rdflib.Namespace(f'#{package_name}.tf14Values')  # setting up target namespace.
        target_csv = f'{package_name.lower()}.tf14Values_{self.year}.csv'
        # directory to the csv file that will be used as a source in the mapping.
        source = os.path.join(self.destination_path, package_name, 'auxiliary_csv', target_csv)

        # creating a copy of all prefixes that were present in the template.
        for ns in g.namespaces():
            g2.namespace_manager.bind(ns[0], ns[1])

        # s, p, o is the convention that was used by creators of Rdflib and it stands for
        # subject, predicate, object. We are iterating through all triples to make necessary modifications
        # to the template that was loaded.
        for s, p, o in g:
            if 'module_ns' in s:
                s1 = rdflib.term.URIRef(target_ns)
                g2.add((s1, p, o))
            elif 'rml#source' in p:
                o1 = rdflib.term.Literal(source)
                g2.add((s, p, o1))
            else:
                g2.add((s, p, o))
        return g2
