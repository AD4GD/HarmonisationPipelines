import os
import subprocess
import shutil

from modules.fadn import fadn
from modules.tools.rml_mapper.rml_mapper import RmlMapper


class FadnTransform(fadn.Fadn):
    """
    Subclass of Fadn that creates data dumps using mapping tool.
    """
    def __init__(self, results_dir, rml_duplicates):
        super().__init__(results_dir=results_dir)
        self.rml_duplicates = rml_duplicates
        self.alt_results_path = None

    def move_content(self):
        """
        Function that moves content to the mapper directory.
        """
        print('########## Creating directories for the transforming tool...')
        if self.rml_duplicates:
            mapper = RmlMapper(handle_duplicates=True)
        else:
            mapper = RmlMapper(handle_duplicates=False)
        preexisting_mapping_folder = os.path.join(mapper.directory, 'mappings')
        preexisting_dumps_folder = os.path.join(mapper.directory, 'output')
        mappings_folder = os.path.join(mapper.directory, self.folder, 'mappings')
        main_folder = os.path.join(mapper.directory, self.folder)
        # removes data directory in case it already exists in the mapper directory.
        if os.path.isdir(main_folder):
            shutil.rmtree(main_folder)
        # removes mapping directory in case it already exists in the mapper directory.
        if os.path.isdir(preexisting_mapping_folder):
            shutil.rmtree(preexisting_mapping_folder)
        # removes dumps directory in case it already exists in the mapper directory.
        if os.path.isdir(preexisting_dumps_folder):
            shutil.rmtree(preexisting_dumps_folder)
        # sets up alternative path in for mv function to work properly in case self.results contains subdirectories.
        self.alt_results_path = self.results_dir.split("/")[0]   # captures only base folder name to copy
        if mapper.windows:
            subprocess.run(args=['move', self.alt_results_path, mapper.directory], check=True, shell=True)
        else:
            subprocess.run(f"mv {self.alt_results_path} {mapper.directory}", check=True, shell=True)

    def _create_output_path(self, mapping, mapper):
        """
        Semi-private helper function that creates directory and output name for dumps in the FADN
        transformation process.
        :param mapping: str -> mapping filename.
        :param mapper: object -> mapper instance.
        :return: str -> full path and name of the output that should be produced by mapper tool.
        """
        dumps_directory = os.path.join(mapper.directory, self.results_dir, 'output', 'dumps')
        os.makedirs(dumps_directory, exist_ok=True)  # creates directory only if it doesn't already exist.
        mapping_name = os.path.splitext(mapping)[0].replace('mapping-', '')
        output_filename = f'fadn-{mapping_name}-{self.folder}.nt'
        output_full_path = os.path.join(dumps_directory, output_filename)
        return output_full_path

    def run_transformer(self):
        """
        Function that runs rmlmapper_action for each package in the directory.
        """
        print('########## Initializing transformer...')
        self.set_date()   # setting proper data based on the filename.
        if self.rml_duplicates:
            mapper = RmlMapper(handle_duplicates=True)
        else:
            mapper = RmlMapper(handle_duplicates=False)
        data_folder = os.path.join(mapper.directory, self.results_dir, 'mappings')
        mapper.detect_system()
        for mapping in os.listdir(data_folder):
            dump_path = self._create_output_path(mapping=mapping, mapper=mapper)
            mapper.generate_dumps(input_data=os.path.join(data_folder, mapping),
                                  dump_path=dump_path)
        transformed_data_dir = os.path.join(mapper.directory, self.alt_results_path)
        if os.path.isdir(transformed_data_dir):
            shutil.move(transformed_data_dir, os.getcwd())
