import logging
import datetime
import os

from modules.generic import generic
from modules.tools.vto_loader.vto_loader import VtoLoader


class GenericLoader(generic.Generic):
    """
    Subclass of Generic that deals with tasks of loading data into Virtuoso.
    """
    def __init__(self, config, uri, remove_target_graph=False, graph_per_dump=False):
        super().__init__()
        self.config = config
        self.uri = uri
        self.remove_target_graph = remove_target_graph
        self.graph_per_dump = graph_per_dump

    def run_loader(self):
        """
        Main function that instantiates the loader tool with pipeline-specific settings.
        """
        print('########## Loading dumps into triplestore...')
        loader = VtoLoader(configfile=self.config, uri=self.uri,
                           remove_target_graph=self.remove_target_graph, graph_per_dump=self.graph_per_dump)
        loader.detect_system()
        loader.load_config()
        loader.vto_loader(data_directory=os.path.join(self.results_dir, self.dumps_dir))
