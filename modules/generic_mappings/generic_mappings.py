import os

from modules.generic import generic
from modules.general_mapping.general_mapping_shp import GeneralMappingGeneratorShp
from modules.general_mapping.general_mapping_csv import GeneralMappingGeneratorCsv
from modules.tools.geotriples.geotriples import GeoTriplesMapper
from modules.tools.yarrrml.yarrrml import YARRRML
from modules.settings import GENERATED_MAPPING_FILENAME


class GenericMappings(generic.Generic):
    """
    Subclass of Generic that deals with mapping tasks.
    """
    def __init__(self, base_uri, yarrrml_rules_file=False, from_config=False, config_path=None, input_type=None,
                 use_db=False, adjust_id_col=False):
        super().__init__()
        self.base_uri = base_uri
        self.from_config = from_config
        self.config_path = config_path
        self.use_db = use_db
        self.input_type = input_type
        self.adjust_id_col = adjust_id_col
        self.yarrrml_rules_file = yarrrml_rules_file

    def process_mapping(self):
        """
        Main function that performs mappings creation.
        """
        input_data = os.path.join(self.results_dir, self.folder)
        mapping_target = os.path.join(self.results_dir, self.mappings_dir)
        os.makedirs(mapping_target, exist_ok=True)
        if self.from_config:
            config_path = self.config_path
            if not os.path.isfile(config_path):
                raise SystemExit(f"Failure! {config_path} was not found!")
            if self.input_type == "Shapefile":
                shp_input_filename = None
                for subdir, dirs, files in os.walk(input_data):
                    for file in files:
                        if file.endswith(".shp"):
                            file_name = os.path.splitext(file)[0]
                            shp_input_filename = file_name
                            break
                if not shp_input_filename:
                    msg = "Expected at least one SHP file as an input, but none were found. Exiting..."
                    raise SystemExit(msg)
                mapper = GeneralMappingGeneratorShp(config_path=config_path,
                                                    shp_filename=shp_input_filename,
                                                    base_uri=self.base_uri)
                mapper.load_cfg()
                mapper.update_types()
                graph = mapper.generate_mapping()
                mapping_path = os.path.join(mapping_target, GENERATED_MAPPING_FILENAME)
                with open(mapping_path, 'w') as f:
                    f.write(graph.serialize(format='ttl'))
                # for subdir, dirs, files in os.walk(input_data):
                #     for file in files:
                #         if file.endswith(".shp"):
                #             file_name = os.path.splitext(file)[0]
                #             mapper = GeneralMappingGeneratorShp(config_path=config_path,
                #                                                 mapping_filename=file_name,
                #                                                 base_uri=self.base_uri)
                #             mapper.load_cfg()
                #             mapper.update_types()
                #             graph = mapper.generate_mapping()
                #             mapping_path = os.path.join(mapping_target, f"{file_name}.ttl")
                #             with open(mapping_path, 'w') as f:
                #                 f.write(graph.serialize(format='ttl'))
            elif self.input_type == "CSV":
                csv_input_file = None
                for subdir, dirs, files in os.walk(input_data):
                    for file in files:
                        if file.endswith(".csv"):
                            csv_input_file = file
                            break
                if not csv_input_file:
                    msg = "Expected at least one CSV file as an input, but none were found. Exiting..."
                    raise SystemExit(msg)
                file_abs_path = os.path.abspath(os.path.join(self.results_dir, self.folder, csv_input_file))
                mapper = GeneralMappingGeneratorCsv(config_path=config_path, file_abs_path=file_abs_path,
                                                    base_uri=self.base_uri)
                mapper.load_cfg()
                mapper.update_types(adjust_template_id=True)
                mapping_path = os.path.join(mapping_target, GENERATED_MAPPING_FILENAME)
                graph = mapper.generate_mapping(mapping_full_path=os.path.abspath(mapping_path))
                with open(mapping_path, 'w') as f:
                    f.write(graph.serialize(format='ttl'))
                # for subdir, dirs, files in os.walk(input_data):
                #     for file in files:
                #         if file.endswith(".csv"):
                #             file_name = os.path.splitext(file)[0]
                #             file_abs_path = os.path.abspath(os.path.join(self.results_dir, self.folder, file))
                #             mapper = GeneralMappingGeneratorCsv(config_path=config_path,
                #                                                 mapping_filename=file_name,
                #                                                 file_abs_path=file_abs_path,
                #                                                 base_uri=self.base_uri)
                #             mapper.load_cfg()
                #             mapper.update_types(adjust_template_id=True)
                #             mapping_path = os.path.join(mapping_target, f"{file_name}.ttl")
                #             graph = mapper.generate_mapping(mapping_full_path=os.path.abspath(mapping_path))
                #             with open(mapping_path, 'w') as f:
                #                 f.write(graph.serialize(format='ttl'))
        elif self.use_db:
            mapper = GeoTriplesMapper()
            mapper.generate_mappings_from_db(mapping_dir=mapping_target, base_uri=self.base_uri)
        elif self.yarrrml_rules_file:
            input_files = []
            if self.input_type == "CSV":
                for subdir, dirs, files in os.walk(input_data):
                    for file in files:
                        if file.endswith(".csv"):
                            file_abs_path = os.path.abspath(os.path.join(self.results_dir, self.folder, file))
                            input_files.append(file_abs_path)
            elif self.input_type == "JSON":
                for subdir, dirs, files in os.walk(input_data):
                    for file in files:
                        if file.endswith(".json"):
                            file_abs_path = os.path.abspath(os.path.join(self.results_dir, self.folder, file))
                            input_files.append(file_abs_path)
            elif self.input_type == "XML":
                for subdir, dirs, files in os.walk(input_data):
                    for file in files:
                        if file.endswith(".xml"):
                            file_abs_path = os.path.abspath(os.path.join(self.results_dir, self.folder, file))
                            input_files.append(file_abs_path)
            mapper = YARRRML(results_dir=self.results_dir)
            mapper.run_yarrrml(rules_file=self.yarrrml_rules_file, input_data_files=input_files,
                               mapping_dir=mapping_target)
        else:
            mapper = GeoTriplesMapper()
            mapper.generate_mappings(input_data=input_data, mapping_dir=mapping_target,
                                     base_uri=self.base_uri, adjust_id=self.adjust_id_col)
