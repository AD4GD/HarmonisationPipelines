import logging
import datetime
import os

from modules.fadn import fadn
from modules.tools.vto_loader.vto_loader import VtoLoader


class FadnLoader(fadn.Fadn):
    """
    Subclass of Fadn that deals with tasks of loading data into Virtuoso.
    """
    def __init__(self, config, uri, results_dir, remove_target_graph=False, graph_per_dump=False):
        super().__init__(results_dir=results_dir)
        self.config = config
        self.uri = uri
        self.remove_target_graph = remove_target_graph
        self.graph_per_dump = graph_per_dump
        self.dumps_dir = os.path.join(self.results_dir, 'output', 'dumps')

    def run_vto_loader(self):
        """
        Main function that instantiates the vto_loader tool with pipeline-specific settings.
        """
        print('########## Loading dumps into triplestore...')
        loader = VtoLoader(configfile=self.config, uri=self.uri,
                           remove_target_graph=self.remove_target_graph, graph_per_dump=self.graph_per_dump)
        loader.fadn_naming_convention = True   # setting up pattern for recognizing suffix for graph_uri.
        loader.detect_system()
        loader.load_config()
        loader.vto_loader(data_directory=self.dumps_dir)
