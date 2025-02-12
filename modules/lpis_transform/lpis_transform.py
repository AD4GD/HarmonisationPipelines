import os
import logging
import datetime
import sys

from modules.lpis import lpis
from modules.tools.geotriples.geotriples import GeoTriplesMapper
from modules.utils.utils import get_paths_normalized_basename


class LpisTransform(lpis.Lpis):
    def __init__(self, results_dir):
        super().__init__(result_dir=results_dir)

        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        current_date = datetime.datetime.now()
        self.log_path = os.path.join('logs',
                                     f'pipeline_lpis_transform'
                                     f'{current_date.year}-{current_date.month}-{current_date.day}.log')
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    def run_transformer(self):
        """
        Function that runs GeoTriples transformer for each shapefile in the data directory.
        """
        print('########## Initializing transformer...')
        self.create_list_of_input_files()
        transformer = GeoTriplesMapper()
        if not self.list_of_input_files:
            self.logger.info(f'No shapefiles were found in the data directory: {self.destination_path}')
            print('Invalid input data! ShapeFiles were not found in the data directory!')
            sys.exit()
        for input_file in self.list_of_input_files:
            base_filename = get_paths_normalized_basename(input_file)
            filename = os.path.splitext(base_filename)[0]
            mapping_path = os.path.join(self.mappings_dir, f'LPIS_mapping_{filename}.ttl')
            if not os.path.isfile(mapping_path):
                self.logger.info(f'System was unable to find corresponding mapping for {base_filename}. '
                            f'Please check naming convention of your mapping files!')
                print(f'Corresponding mapping for {base_filename} was not found. Skipping...')
            else:
                input_file_path = os.path.join(input_file)
                os.makedirs(self.dumps_dir, exist_ok=True)
                output_file_path = os.path.join(self.dumps_dir, filename + '_dump.nt')
                transformer.transform_shapefile(input_data=input_file_path, input_mapping=mapping_path,
                                                base_uri=None, dump_filename=output_file_path)
