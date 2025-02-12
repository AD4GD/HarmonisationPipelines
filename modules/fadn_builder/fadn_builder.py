import os
import sys

from modules.fadn_pipeline import fadn_pipeline
from modules.pipeline import pipeline
from modules.utils.utils import print_warning, set_folder_name_based_on_url, cleaning_preexisting_dir, \
    clean_scripts_directory
from modules.dictionaries import dictionaries


def helper_builder_all_url(pipe, **kwargs):
    """
    Helper function that provides logic for stage when value is all and input is provided as url.
    :param kwargs: key word arguments provided by parent function.
    :param pipe: Pipeline instance object.
    """
    url = kwargs['url_input']
    folder = set_folder_name_based_on_url(url)
    if folder:
        if folder not in dictionaries.illegal_dir_names:
            path = folder
        else:
            print('Please change the name of your data folder. The one you used is prohibited!')
            sys.exit()
    else:
        path = "fadn_data"
    uri = kwargs['graph_uri']
    if kwargs['graph_per_dump']:
        if kwargs['reload_graph']:
            fadn_full_pipeline_url(pipe=pipe, url=url, path=path, uri=uri, output_dir=kwargs['output'], rg=True,
                                   gpd=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        else:
            fadn_full_pipeline_url(pipe=pipe, url=url, path=path, uri=uri, output_dir=kwargs['output'], gpd=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
    else:
        if kwargs['reload_graph']:
            fadn_full_pipeline_url(pipe=pipe, url=url, path=path, uri=uri, output_dir=kwargs['output'], rg=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        else:
            fadn_full_pipeline_url(pipe=pipe, url=url, path=path, uri=uri, output_dir=kwargs['output'])
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])


def helper_builder_all_dir(pipe, **kwargs):
    """
    Helper function that provides logic for stage when value is all and input is provided as dir.
    :param kwargs: key word arguments provided by parent function.
    :param pipe: Pipeline instance object.
    """
    path = kwargs['dir_input']
    uri = kwargs['graph_uri']
    if kwargs['graph_per_dump']:
        if kwargs['reload_graph']:
            fadn_full_pipeline_dir(pipe=pipe, path=path, uri=uri, output_dir=kwargs['output'], rg=True, gpd=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        else:
            fadn_full_pipeline_dir(pipe=pipe, path=path, uri=uri, output_dir=kwargs['output'], gpd=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
    else:
        if kwargs['reload_graph']:
            fadn_full_pipeline_dir(pipe=pipe, path=path, uri=uri, output_dir=kwargs['output'], rg=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        else:
            fadn_full_pipeline_dir(pipe=pipe, path=path, uri=uri, output_dir=kwargs['output'])
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])


def helper_builder_all_none(pipe, **kwargs):
    """
    Helper function that provides logic for stage when value is all and there is no input.
    :param kwargs: key word arguments provided by parent function.
    :param pipe: Pipeline instance object.
    :returns nothing. Serves as an exit.
    """
    for folder in os.listdir():
        if folder.startswith('fadn'):
            path = folder
            uri = kwargs['graph_uri']
            if kwargs['graph_per_dump']:
                if kwargs['reload_graph']:
                    fadn_full_pipeline_dir(pipe=pipe, path=path, uri=uri, output_dir=kwargs['output'], rg=True,
                                           gpd=True)
                    if kwargs['clean']:
                        clean_scripts_directory(results_dir=kwargs['output'])
                        return
                    return
                else:
                    fadn_full_pipeline_dir(pipe=pipe, path=path, uri=uri, output_dir=kwargs['output'], gpd=True)
                    if kwargs['clean']:
                        clean_scripts_directory(results_dir=kwargs['output'])
                        return
                    return
            else:
                if kwargs['reload_graph']:
                    fadn_full_pipeline_dir(pipe=pipe, path=path, uri=uri, output_dir=kwargs['output'], rg=True)
                    if kwargs['clean']:
                        clean_scripts_directory(results_dir=kwargs['output'])
                        return
                    return
                else:
                    fadn_full_pipeline_dir(pipe=pipe, path=path, uri=uri, output_dir=kwargs['output'])
                    if kwargs['clean']:
                        clean_scripts_directory(results_dir=kwargs['output'])
                        return
                    return
    print_warning()


def helper_builder_all(pipe, **kwargs):
    """
    Helper function that provides logic when the value of the stage is all.
    :param kwargs:
    :param pipe: Pipeline instance object.
    """
    if kwargs['url_input']:
        helper_builder_all_url(pipe=pipe, **kwargs)
    elif kwargs['dir_input']:
        helper_builder_all_dir(pipe=pipe, **kwargs)
    else:
        helper_builder_all_none(pipe=pipe, **kwargs)


def helper_builder_preprocess(pipe, **kwargs):
    """
    Helper function that provides logic when the value of the stage is preprocess.
    :param kwargs:
    :param pipe: Pipeline instance object.
    :returns nothing. Serves as an exit.
    """
    if kwargs['url_input']:
        url = kwargs['url_input']
        folder = set_folder_name_based_on_url(url)
        if folder:
            if folder not in dictionaries.illegal_dir_names:
                path = folder
            else:
                print('Please change the name of your data folder. The one you used is prohibited!')
                sys.exit()
        else:
            path = "fadn_data"
        fadn_preprocess_pipeline_url(pipe=pipe, url=url, path=path, output_dir=kwargs['output'])
    elif kwargs['dir_input']:
        path = kwargs['dir_input']
        fadn_preprocess_pipeline_dir(pipe=pipe, path=path, output_dir=kwargs['output'])
    else:
        for folder in os.listdir():
            if folder.startswith('fadn'):
                path = folder
                fadn_preprocess_pipeline_dir(pipe=pipe, path=path, output_dir=kwargs['output'])
                return
        print_warning()


def helper_builder_mapping(pipe, **kwargs):
    """
    Helper function that provides logic when the value of the stage is mapping.
    :param kwargs:
    :param pipe: Pipeline instance object.
    :returns nothing. Serves as an exit.
    """
    if kwargs['url_input']:
        url = kwargs['url_input']
        folder = set_folder_name_based_on_url(url)
        if folder:
            if folder not in dictionaries.illegal_dir_names:
                path = folder
            else:
                print('Please change the name of your data folder. The one you used is prohibited!')
                sys.exit()
        else:
            path = "fadn_data"
        fadn_mapping_pipeline_url(pipe=pipe, path=path, url=url, output_dir=kwargs['output'])
    elif kwargs['dir_input']:
        path = kwargs['dir_input']
        fadn_mapping_pipeline_dir(pipe=pipe, path=path, output_dir=kwargs['output'])
        return
    else:
        for folder in os.listdir():
            if folder.startswith('fadn'):
                path = folder
                fadn_mapping_pipeline_dir(pipe=pipe, path=path, output_dir=kwargs['output'])
                return
        print_warning()


def helper_builder_transform(pipe, **kwargs):
    """
    Helper function that provides logic when the value of the stage is transform.
    :param kwargs:
    :param pipe: Pipeline instance object.
    :returns nothing. Serves as an exit.
    """
    if kwargs['url_input']:
        url = kwargs['url_input']
        folder = set_folder_name_based_on_url(url)
        if folder:
            if folder not in dictionaries.illegal_dir_names:
                path = folder
            else:
                print('Please change the name of your data folder. The one you used is prohibited!')
                sys.exit()
        else:
            path = "fadn_data"
        fadn_transformer_pipeline_url(pipe=pipe, path=path, url=url, output_dir=kwargs['output'])
    elif kwargs['dir_input']:
        path = kwargs['dir_input']
        fadn_transformer_pipeline_dir(pipe=pipe, path=path, output_dir=kwargs['output'])
    else:
        for folder in os.listdir():
            if folder.startswith('fadn'):
                path = folder
                fadn_transformer_pipeline_dir(pipe=pipe, path=path, output_dir=kwargs['output'])
                return
        print_warning()


def helper_builder_postprocess(pipe, **kwargs):
    """
    Helper function that provides logic when the value of the stage is postprocess.
    :param kwargs:
    :param pipe: Pipeline instance object.
    :returns nothing. Serves as an exit.
    """
    if kwargs['url_input']:
        url = kwargs['url_input']
        folder = set_folder_name_based_on_url(url)
        if folder:
            if folder not in dictionaries.illegal_dir_names:
                path = folder
            else:
                print('Please change the name of your data folder. The one you used is prohibited!')
                sys.exit()
        else:
            path = "fadn_data"
        fadn_postprocess_pipeline_url(pipe=pipe, path=path, url=url, output_dir=kwargs['output'])
    elif kwargs['dir_input']:
        path = kwargs['dir_input']
        fadn_postprocess_pipeline_dir(pipe=pipe, path=path, output_dir=kwargs['output'])
    else:
        for folder in os.listdir():
            if folder.startswith('fadn'):
                path = folder
                fadn_postprocess_pipeline_dir(pipe=pipe, path=path, output_dir=kwargs['output'])
                return
        print_warning()


def helper_builder_fetch(pipe, **kwargs):
    """
    Helper function that provides logic when the value of the stage is fetch.
    :param kwargs:
    :param pipe: Pipeline instance object.
    """
    url = kwargs['url_input']
    folder = set_folder_name_based_on_url(url)
    if folder:
        if folder in dictionaries.illegal_dir_names:
            print('Please change the name of your data folder. The one you used is prohibited!')
            sys.exit()
    fadn_fetch_data_pipeline(pipe=pipe, url=url, output_dir=kwargs['output'])


def fadn_pipeline_builder(**kwargs):
    """
    Function that builds FADN Pipeline based on the arguments specified by the user.
    """
    print('########## Initializing the FADN Pipeline...')
    pipe = pipeline.Pipeline()
    cleaning_preexisting_dir()
    if kwargs['stage'] == 'all':
        helper_builder_all(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'preprocess':
        helper_builder_preprocess(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'mapping':
        helper_builder_mapping(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'transform':
        helper_builder_transform(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'postprocess':
        helper_builder_postprocess(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'fetch':
        helper_builder_fetch(pipe=pipe, **kwargs)


def fadn_full_pipeline_url(pipe, url, path, uri, output_dir, rg=False, gpd=False):
    """
    Helper function that runs the full instance of the FADN Pipeline with user's URL input.
    :param pipe: Pipeline object.
    :param url: str -> url to the file containing data.
    :param path: str -> main folder containing data.
    :param uri: str -> graph's URI.
    :param output_dir: str -> name for the output directory.
    :param rg: boolean -> stands for reload graph. If true the graph will be reloaded.
    :param gpd: boolean -> stands for graph per dump. If true uri argument will be used as a prefix for constructing
    graph's URI.
    """
    fadn_pipeline.building_webzip(pipe=pipe, url=url, output_dir=output_dir)
    fadn_pipeline.building_csv(pipe=pipe, path=path, url=url, output_dir=output_dir)
    fadn_pipeline.building_mappings(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_transformer(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_postprocessor(pipe=pipe, output_dir=output_dir)
    fadn_pipeline.building_loader(pipe=pipe, configfile='config.yaml', uri=uri, output_dir=output_dir,
                                  remove_target_graph=rg, graph_per_dump=gpd)
    print('INFO: Running the whole Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_full_pipeline_dir(pipe, path, uri, output_dir, rg=False, gpd=False):
    """
    Helper function that runs the full instance of the FADN Pipeline with user's directory input.
    :param pipe: Pipeline object.
    :param path: str -> main folder containing data.
    :param uri: str -> graph's URI.
    :param output_dir: str -> name for the output directory.
    :param rg: stands for reload graph. If true the graph will be reloaded.
    :param gpd: stands for graph per dump. If true uri argument will be used as a prefix for constructing
    graph's URI.
    """
    fadn_pipeline.building_csv(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_mappings(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_transformer(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_postprocessor(pipe=pipe, output_dir=output_dir)
    fadn_pipeline.building_loader(pipe=pipe, configfile='config.yaml', uri=uri, output_dir=output_dir,
                                  remove_target_graph=rg, graph_per_dump=gpd)
    print('INFO: Running the whole Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_preprocess_pipeline_url(pipe, url, path, output_dir):
    """
    Helper function that runs the preprocess stage of the FADN Pipeline with user's URL input.
    :param pipe: Pipeline object.
    :param url: str -> url to the file containing data.
    :param path: str -> main folder containing data.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_webzip(pipe=pipe, url=url, output_dir=output_dir)
    fadn_pipeline.building_csv(pipe=pipe, path=path, url=url, output_dir=output_dir)
    print('INFO: Running the pre-processing stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_preprocess_pipeline_dir(pipe, path, output_dir):
    """
    Helper function that runs the preprocess stage of the FADN Pipeline with user's directory input.
    :param pipe: Pipeline object.
    :param path: str -> main folder containing data.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_csv(pipe=pipe, path=path, output_dir=output_dir)
    print('INFO: Running the pre-processing stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_mapping_pipeline_url(pipe, path, url, output_dir):
    """
    Helper function that runs the mapping stage of the FADN Pipeline with URL input.
    :param pipe: Pipeline object.
    :param path: str -> main folder containing data.
    :param url: str -> data URL.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_webzip(pipe=pipe, url=url, output_dir=output_dir)
    fadn_pipeline.building_csv(pipe=pipe, path=path, url=url, output_dir=output_dir)
    fadn_pipeline.building_mappings(pipe=pipe, path=path, output_dir=output_dir)
    print('INFO: Running the mapping stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_mapping_pipeline_dir(pipe, path, output_dir):
    """
    Helper function that runs the mapping stage of the FADN Pipeline with DIR input.
    :param pipe: Pipeline object.
    :param path: str -> main folder containing data.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_csv(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_mappings(pipe=pipe, path=path, output_dir=output_dir)
    print('INFO: Running the mapping stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_transformer_pipeline_url(pipe, path, url, output_dir):
    """
    Helper function that runs the transforming stage of the FADN Pipeline.
    :param pipe: Pipeline object.
    :param path: str -> main folder containing data.
    :param url: str -> data URL.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_webzip(pipe=pipe, url=url, output_dir=output_dir)
    fadn_pipeline.building_csv(pipe=pipe, path=path, url=url, output_dir=output_dir)
    fadn_pipeline.building_mappings(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_transformer(pipe=pipe, path=path, output_dir=output_dir)
    print('INFO: Running the transformer stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_transformer_pipeline_dir(pipe, path, output_dir):
    """
    Helper function that runs the transforming stage of the FADN Pipeline.
    :param pipe: Pipeline object.
    :param path: str -> main folder containing data.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_csv(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_mappings(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_transformer(pipe=pipe, path=path, output_dir=output_dir)
    print('INFO: Running the transformer stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_postprocess_pipeline_url(pipe, url, path, output_dir):
    """
    Helper function that runs the post-processing stage of the FADN Pipeline.
    :param pipe: Pipeline object.
    :param path: str -> main folder containing data.
    :param url: str -> data URL.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_webzip(pipe=pipe, url=url, output_dir=output_dir)
    fadn_pipeline.building_csv(pipe=pipe, path=path, url=url, output_dir=output_dir)
    fadn_pipeline.building_mappings(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_transformer(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_postprocessor(pipe=pipe, output_dir=output_dir)
    print('INFO: Running the transformer stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_postprocess_pipeline_dir(pipe, path, output_dir):
    """
    Helper function that runs the post-processing stage of the FADN Pipeline.
    :param pipe: Pipeline object.
    :param path: str -> main folder containing data.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_csv(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_mappings(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_transformer(pipe=pipe, path=path, output_dir=output_dir)
    fadn_pipeline.building_postprocessor(pipe=pipe, output_dir=output_dir)
    print('INFO: Running the transformer stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def fadn_fetch_data_pipeline(pipe, url, output_dir):
    """
    Helper function that runs fetching data from web stage of the FADN Pipeline.
    :param pipe: Pipeline object.
    :param url: str -> url to the file containing data.
    :param output_dir: str -> name for the output directory.
    """
    fadn_pipeline.building_webzip(pipe=pipe, url=url, output_dir=output_dir)
    print('INFO: Running the fetching data from the web stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')
