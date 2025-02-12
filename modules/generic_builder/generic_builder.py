import shutil
import sys
import os

from modules.generic_pipeline import generic_pipeline
from modules.utils.utils import cleaning_preexisting_dir, clean_scripts_directory, get_paths_normalized_basename
from modules.settings import CURRENTLY_SUPPORTED_FILETYPES, GEOSPATIAL_FILETYPES, OTHER_FILETYPES


def _set_proper_input_type(data_stage, **kwargs):
    """
    Helper function that sets up proper input type based on the way user provided data.
    :param data_stage: str -> single choice from: (initial_data, mappings, dumps).
    :return: str -> name of the folder containing input data.
    """
    if kwargs['url_input']:
        url = kwargs['url_input']
        input_folder = generic_pipeline.building_generic_fetch(url=url, data_stage=data_stage,
                                                               output_dir=kwargs["output"])
    else:
        input_folder = kwargs['dir_input']
    return input_folder


def _set_proper_mapping_input_type(**kwargs):
    """
    Helper function that sets up proper input type based on the way user provided data.
    :return: str -> name of the folder containing mapping input data.
    """
    if kwargs['mapping_url']:
        url = kwargs['mapping_url']
        mapping_folder = generic_pipeline.building_generic_fetch(url=url, data_stage="mappings",
                                                                 output_dir=kwargs["output"])
    else:
        mapping_folder = kwargs['mapping_input']
    return mapping_folder


def _set_proper_yarrrml_rules_type(**kwargs):
    """
    Helper function that sets up proper path to the rules file for YARRRML tool.
    """
    if kwargs['yarrrml_rules_url']:
        url = kwargs['yarrrml_rules_url']
        rules_dir = generic_pipeline.building_generic_fetch(url=url, data_stage="rules_file",
                                                            output_dir=kwargs["output"])
        rules_file = None
        for file in os.listdir(rules_dir):
            if file.endswith(".yaml") or file.endswith(".yml"):
                if rules_file:
                    msg = "Exiting... exactly one YAML file is expected to be provided using yarrrml_rules_url, " \
                          "but instead we got more than one in the package."
                    raise SystemExit(msg)
                rules_file = os.path.join(rules_dir, file)
    else:
        rules_file = kwargs['yarrrml_rules_value']
    return rules_file


def _remove_folder_containing_initial_data(input_data, **kwargs):
    """
    Helper function that removes initial data folder from final output served to the user.
    """
    input_foldername = get_paths_normalized_basename(input_data)
    output_candidate = os.path.join(kwargs["output"], input_foldername)
    if os.path.exists(output_candidate):
        shutil.rmtree(output_candidate)
    else:
        print("Folder containing initial input data not recognized properly at the end of the pipelines run. "
              "Therefore initial data folder was not deleted from final results!")


def generic_pipeline_builder(stages, **kwargs):
    """
    Function that builds generic Pipeline based on the arguments specified by the user.
    """
    print('########## Initializing the Generic Pipeline...')
    cleaning_preexisting_dir()
    updated_data_folder = None
    updated_mapping_folder = None
    input_folder = None
    for stage in reversed(stages):
        if stage == "preprocess":
            input_folder = _set_proper_input_type(data_stage="initial_data", **kwargs)
            updated_data_folder = generic_pipeline.building_generic_preprocessor(input_dir=input_folder,
                                                                                 output_dir=kwargs['output'],
                                                                                 actions=kwargs['preprocess_activity'])
        elif stage == "mapping":
            if kwargs['yarrrml_rules_value'] or kwargs['yarrrml_rules_url']:
                rules_file = _set_proper_yarrrml_rules_type(data_stage="rules_file", **kwargs)
            else:
                rules_file = False
            if updated_data_folder:
                updated_mapping_folder = generic_pipeline.building_generic_mapper(input_dir=updated_data_folder,
                                                                                  output_dir=kwargs['output'],
                                                                                  base_uri=kwargs['base_uri'],
                                                                                  from_config=kwargs['from_config'],
                                                                                  config_path=kwargs['from_config_value'],
                                                                                  input_type=kwargs['input_type'],
                                                                                  yarrrml_rules_file=rules_file,
                                                                                  adjust_id_col=True)
            else:
                input_folder = _set_proper_input_type(data_stage="initial_data", **kwargs)
                updated_data_folder = input_folder
                updated_mapping_folder = generic_pipeline.building_generic_mapper(input_dir=input_folder,
                                                                                  output_dir=kwargs['output'],
                                                                                  base_uri=kwargs['base_uri'],
                                                                                  from_config=kwargs['from_config'],
                                                                                  config_path=kwargs['from_config_value'],
                                                                                  from_db=kwargs['db_input'],
                                                                                  input_type=kwargs['input_type'],
                                                                                  yarrrml_rules_file=rules_file)
        elif stage == "transform":
            if kwargs['input_type'] in CURRENTLY_SUPPORTED_FILETYPES:
                if kwargs['sparql_query']:
                    mapper = "tarql"
                elif kwargs['input_type'] == "CSVW":
                    mapper = "csv2rdf"
                elif kwargs['input_type'] in GEOSPATIAL_FILETYPES:
                    mapper = 'geo'
                elif kwargs['input_type'] in OTHER_FILETYPES:
                    mapper = 'rml'
            else:
                print(f"Sorry, support for the {kwargs['input_type']} file type is not implemented yet!")
                print("Exiting...")
                sys.exit()
            if kwargs['from_config']:
                adjust_rml_source = True
            else:
                adjust_rml_source = False
            if updated_data_folder:
                if updated_mapping_folder:
                    updated_data_folder = generic_pipeline.building_generic_transformer(input_dir=updated_data_folder,
                                                                                        mapping_dir=updated_mapping_folder,
                                                                                        output_dir=kwargs['output'],
                                                                                        base_uri=kwargs['base_uri'],
                                                                                        mapper=mapper,
                                                                                        input_type=kwargs['input_type'],
                                                                                        adjust_rml_source=
                                                                                        adjust_rml_source)
                else:
                    mapping_folder = _set_proper_mapping_input_type(**kwargs)
                    updated_data_folder = generic_pipeline.building_generic_transformer(input_dir=updated_data_folder,
                                                                                        mapping_dir=mapping_folder,
                                                                                        output_dir=kwargs['output'],
                                                                                        base_uri=kwargs['base_uri'],
                                                                                        mapper=mapper,
                                                                                        input_type=kwargs['input_type'],
                                                                                        adjust_rml_source=True,
                                                                                        sparql_query=kwargs[
                                                                                            'sparql_query'])
            else:
                input_folder = _set_proper_input_type(data_stage="initial_data", **kwargs)
                if updated_mapping_folder:
                    updated_data_folder = generic_pipeline.building_generic_transformer(input_dir=input_folder,
                                                                                        mapping_dir=updated_mapping_folder,
                                                                                        output_dir=kwargs['output'],
                                                                                        base_uri=kwargs['base_uri'],
                                                                                        mapper=mapper,
                                                                                        input_type=kwargs['input_type'],
                                                                                        adjust_rml_source=
                                                                                        adjust_rml_source,
                                                                                        from_db=kwargs['db_input'])
                else:
                    mapping_folder = _set_proper_mapping_input_type(**kwargs)
                    updated_data_folder = generic_pipeline.building_generic_transformer(input_dir=input_folder,
                                                                                        mapping_dir=mapping_folder,
                                                                                        output_dir=kwargs['output'],
                                                                                        base_uri=kwargs['base_uri'],
                                                                                        mapper=mapper,
                                                                                        input_type=kwargs['input_type'],
                                                                                        adjust_rml_source=True,
                                                                                        from_db=kwargs['db_input'],
                                                                                        sparql_query=kwargs[
                                                                                            'sparql_query'])
        elif stage == "postprocess":
            if updated_data_folder:
                updated_data_folder = generic_pipeline.building_generic_postprocessor(input_dir=updated_data_folder,
                                                                                      output_dir=kwargs['output'],
                                                                                      to_turtle=kwargs["to_ttl"],
                                                                                      replace_expression=
                                                                                      kwargs['replace_expression'],
                                                                                      remove_line=kwargs["remove_line"],
                                                                                      target_encoding=
                                                                                      kwargs["target_encoding"],
                                                                                      source_encoding=
                                                                                      kwargs["source_encoding"])
            else:
                input_folder = _set_proper_input_type(data_stage="dumps", **kwargs)
                updated_data_folder = generic_pipeline.building_generic_postprocessor(input_dir=input_folder,
                                                                                      output_dir=kwargs['output'],
                                                                                      to_turtle=kwargs["to_ttl"],
                                                                                      replace_expression=
                                                                                      kwargs['replace_expression'],
                                                                                      remove_line=kwargs["remove_line"],
                                                                                      target_encoding=
                                                                                      kwargs["target_encoding"],
                                                                                      source_encoding=
                                                                                      kwargs["source_encoding"])
        elif stage == "load":
            if updated_data_folder:
                if kwargs['graph_per_dump']:
                    if kwargs['reload_graph']:
                        generic_pipeline.building_generic_loader(input_dir=updated_data_folder,
                                                                 graph_uri=kwargs['graph_uri'],
                                                                 output_dir=kwargs['output'],
                                                                 rg=True, gpd=True)
                    else:
                        generic_pipeline.building_generic_loader(input_dir=updated_data_folder,
                                                                 graph_uri=kwargs['graph_uri'],
                                                                 output_dir=kwargs['output'],
                                                                 rg=False, gpd=True)
                else:
                    if kwargs['reload_graph']:
                        generic_pipeline.building_generic_loader(input_dir=updated_data_folder,
                                                                 graph_uri=kwargs['graph_uri'],
                                                                 output_dir=kwargs['output'],
                                                                 rg=True, gpd=False)
                    else:
                        generic_pipeline.building_generic_loader(input_dir=updated_data_folder,
                                                                 graph_uri=kwargs['graph_uri'],
                                                                 output_dir=kwargs['output'],
                                                                 rg=False, gpd=False)
            else:
                input_folder = _set_proper_input_type(data_stage="dumps", **kwargs)
                if kwargs['graph_per_dump']:
                    if kwargs['reload_graph']:
                        generic_pipeline.building_generic_loader(input_dir=input_folder,
                                                                 graph_uri=kwargs['graph_uri'],
                                                                 output_dir=kwargs['output'],
                                                                 rg=True, gpd=True)
                    else:
                        generic_pipeline.building_generic_loader(input_dir=input_folder,
                                                                 graph_uri=kwargs['graph_uri'],
                                                                 output_dir=kwargs['output'],
                                                                 rg=False, gpd=True)
                else:
                    if kwargs['reload_graph']:
                        generic_pipeline.building_generic_loader(input_dir=input_folder,
                                                                 graph_uri=kwargs['graph_uri'],
                                                                 output_dir=kwargs['output'],
                                                                 rg=True, gpd=False)
                    else:
                        generic_pipeline.building_generic_loader(input_dir=input_folder,
                                                                 graph_uri=kwargs['graph_uri'],
                                                                 output_dir=kwargs['output'],
                                                                 rg=False, gpd=False)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        elif stage == "link":
            link_folder = _set_proper_input_type(data_stage="dumps", **kwargs)
            generic_pipeline.building_generic_link(input_dir=link_folder, output_dir=kwargs['output'])

    if input_folder:
        _remove_folder_containing_initial_data(input_data=input_folder, **kwargs)
