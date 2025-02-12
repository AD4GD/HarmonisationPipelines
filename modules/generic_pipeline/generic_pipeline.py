from modules.generic_preprocess import generic_preprocess
from modules.generic_mappings import generic_mappings
from modules.generic_transform import generic_transform
from modules.generic_postprocess import generic_postprocess
from modules.generic_loader import generic_loader
from modules.generic_web_zip import generic_web_zip
from modules.generic_link import generic_link


def building_generic_loader(input_dir, output_dir, graph_uri, rg=False, gpd=False):
    """
    Function that builds generic pipeline for loading data into Virtuoso.
    :param input_dir: str -> directory containing dumps that will be loaded into triplestore.
    :param output_dir: str -> str -> name of the directory for output files.
    :param graph_uri: str -> graph's URI.
    :param rg: boolean -> if True, the loader will clear graph before loading the data.
    :param gpd: boolean -> if True Graph's URI will be used as a base (prefix).
    """
    print('INFO: Loading data to the triplestore...')
    loader = generic_loader.GenericLoader(config='config.yaml', uri=graph_uri,
                                          remove_target_graph=rg, graph_per_dump=gpd)
    if output_dir:
        loader.results_dir = output_dir
    if input_dir:
        loader.dumps_dir = input_dir
    loader.create_main_dir_for_storing_results()
    loader.copy_folder_to_destination(data_dir=loader.dumps_dir)
    loader.run_loader()
    print('*************************************************************')
    print('Loading data into triplestore is done!')


def building_generic_mapper(input_dir, output_dir, base_uri, from_config, config_path, input_type, yarrrml_rules_file,
                            adjust_id_col=False, from_db=False):
    """
    Function that builds generic pipeline for mapping generation.
    :param input_dir: str -> name of the directory storing input files.
    :param output_dir: str -> name of the directory for output files.
    :param base_uri: str -> base URI for mapping.
    :param from_config: boolean -> if True the mapping will be generated based on the user's config input.
    :param config_path: str -> path to the config file.
    :param input_type: str -> input type.
    :param yarrrml_rules_file: str -> path to the rules file.
    :param adjust_id_col: bool -> flag, if true id reference associated with rr:template predicate will be updated.
    :param from_db: bool -> flag, if true input data comes from relation database.
    :return: str -> name of the directory containing mapping files.
    """
    print('INFO: Generating mappings...')
    if from_config:
        mapper = generic_mappings.GenericMappings(base_uri=base_uri, from_config=from_config, config_path=config_path,
                                                  input_type=input_type, use_db=from_db)
    elif yarrrml_rules_file:
        mapper = generic_mappings.GenericMappings(base_uri=base_uri, input_type=input_type,
                                                  yarrrml_rules_file=yarrrml_rules_file)
    else:
        mapper = generic_mappings.GenericMappings(base_uri=base_uri, use_db=from_db, adjust_id_col=adjust_id_col)
    if output_dir:
        mapper.results_dir = output_dir
    if input_dir:
        mapper.folder = input_dir
    mapper.create_main_dir_for_storing_results()
    if not from_db:
        mapper.copy_folder_to_destination(data_dir=mapper.folder)
    mapper.process_mapping()
    print('*************************************************************')
    print('Mappings generation is done!')
    return mapper.mappings_dir


def building_generic_transformer(input_dir, mapping_dir, output_dir, base_uri, mapper, input_type,
                                 adjust_rml_source, from_db=False, sparql_query=False):
    """
    Function that builds generic pipeline for transformation process.
    :param input_dir: str -> name of the directory storing input files.
    :param mapping_dir: str -> name for directory containing mappings.
    :param output_dir: str -> name of the directory for output files.
    :param base_uri: str -> base URI for mapping.
    :param mapper: str -> type of mapper that should be used for transformation.
    :param input_type str -> type of file that will be transformed.
    :param adjust_rml_source boolean -> if True the source in the mapping will be adjusted to existing
    absolute path.
    :param from_db: str -> flag, if true input data comes from relation database.
    :param sparql_query: bool -> flag indicating that sparql query should be used as a mapping.
    :return: str -> name of the directory containing mapping files.
    """
    print('INFO: Transforming into dumps...')
    if sparql_query or input_type == "CSVW":
        transformer = generic_transform.GenericTransform(mapper=mapper, input_type=input_type)
    else:
        if base_uri:
            transformer = generic_transform.GenericTransform(mapper=mapper, input_type=input_type, base_uri=base_uri,
                                                             adjust_rml_source=adjust_rml_source)
        else:
            transformer = generic_transform.GenericTransform(mapper=mapper, input_type=input_type,
                                                             adjust_rml_source=adjust_rml_source)
    if output_dir:
        transformer.results_dir = output_dir
    if input_dir:
        transformer.folder = input_dir
    if mapping_dir:
        transformer.mappings_dir = mapping_dir
    transformer.create_main_dir_for_storing_results()
    # checking and moving folder containing mappings.
    transformer.copy_mapping_to_destination(data_dir=transformer.mappings_dir)
    # checking and moving folder containing initial data.
    if not from_db:
        transformer.copy_folder_to_destination(data_dir=transformer.folder)
    transformer.process_transformation()
    print('*************************************************************')
    print('Transformation is done!')
    return transformer.dumps_dir


def building_generic_preprocessor(input_dir, output_dir, actions):
    """
    Function that builds generic pipeline for preprocessing tasks.
    :param input_dir: str -> name of the directory storing input files.
    :param output_dir: str -> name of the directory for output files.
    :param actions: list -> list of preprocess actions that has to be performed.
    :return: str -> name of the directory containing preprocessed files.
    """
    print('INFO: Preprocessing...')
    preprocessor = generic_preprocess.GenericPreprocess()
    if output_dir:
        preprocessor.results_dir = output_dir
    if input_dir:
        preprocessor.folder = input_dir
    preprocessor.create_main_dir_for_storing_results()
    preprocessor.copy_folder_to_destination(data_dir=preprocessor.folder)
    chained = False   # variable that tracks if there were previous pre-process actions.
    if "unzip_multiple_archives" in actions:
        preprocessor.unzip_multiple_inputs()
        chained = True
    if "convert_netcdf_to_csv" in actions:
        preprocessor.convert_netcdf_to_csv(chained=chained)
    if "add_seq_col" in actions:
        preprocessor.add_sequential_column(chained=chained)
    if "normalize_delimiter" in actions and "add_seq_col" not in actions:
        preprocessor.normalize_delimiter(chained=chained)
    if "to_crs" in actions:
        preprocessor.project_crs(chained=chained)
    if "add_enum" in actions:
        preprocessor.add_enum(chained=chained)
    print('*************************************************************')
    print('Preprocessing is done!')
    return preprocessor.preprocess_dir


def building_generic_postprocessor(input_dir, output_dir, replace_expression, target_encoding, remove_line,
                                   source_encoding=False, to_turtle=False):
    """
    Function that builds generic pipeline for post-processing tasks.
    :param input_dir: str -> name of the directory storing input files.
    :param output_dir: str -> name of the directory for output files.
    :param replace_expression: tuple -> tuple containing expression that should be replaced as a port of postprocessing.
    :param target_encoding: str -> target encoding.
    :param source_encoding: str -> source encoding, optional.
    :param to_turtle: bool -> if True the output will be converted into turtle file.
    :param remove_line: str -> string based on which line has to be removed from dump.
    :return: str -> name of the container directory that stores output.
    """
    print('INFO: Postprocessing...')
    postprocessor = generic_postprocess.GenericPostprocess()
    if output_dir:
        postprocessor.results_dir = output_dir
    if input_dir:
        postprocessor.dumps_dir = input_dir
    postprocessor.create_main_dir_for_storing_results()
    postprocessor.copy_folder_to_destination(data_dir=postprocessor.dumps_dir)
    postprocessor.run_postprocessor()
    if remove_line:
        postprocessor.remove_line_containing_specific_string(target_string=remove_line)
    if replace_expression:
        to_be_replaced, replacement = replace_expression
        postprocessor.replace_expression_postprocessing(to_be_replaced=to_be_replaced,
                                                        replacement=replacement)
    if target_encoding:
        postprocessor.adjust_encoding(target_encoding=target_encoding, source_encoding=source_encoding)
    if to_turtle:
        postprocessor.convert_to_turtle()
    print('*************************************************************')
    print('Postprocessing is done!')
    return postprocessor.postprocess_dir


def building_generic_fetch(url, data_stage, output_dir):
    """
    Function that builds generic pipeline for post-processing tasks.
    :param url: str -> URL to the input file package.
    :param data_stage: str -> single choice from: (initial_data, mappings, dumps).
    :param output_dir: str -> output directory.
    :return: str -> name of the folder that contains data.
    """
    print('INFO: Fetching data...')
    webzip = generic_web_zip.GenericWebZip(url=url)
    if output_dir:
        webzip.results_dir = output_dir
    webzip.create_main_dir_for_storing_results()
    data_dir = webzip.fetch_data(data_stage=data_stage)
    webzip.remove_zip()
    print('*************************************************************')
    print('Fetching is done!')
    return data_dir


def building_generic_link(input_dir, output_dir):
    """
    Function that builds generic pipeline for linking task.
    :param input_dir: str -> path to the input directory.
    :param output_dir: str -> path to the output directory.
    """
    print('INFO: Linking data...')
    linking_tool = generic_link.GenericLinking()
    if input_dir:
        linking_tool.folder = input_dir
    if output_dir:
        linking_tool.results_dir = output_dir
    linking_tool.create_main_dir_for_storing_results()
    linking_tool.copy_folder_to_destination(data_dir=input_dir)
    linking_tool.confirm_config()
    linking_tool.process_linking()
    print('*************************************************************')
    print('Linking is done!')
