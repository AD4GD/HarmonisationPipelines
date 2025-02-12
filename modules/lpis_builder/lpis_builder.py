import os

from modules.lpis_pipeline import lpis_pipeline
from modules.pipeline import pipeline
from modules.utils.utils import load_config_from_path, cleaning_preexisting_dir, clean_scripts_directory, print_warning


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


def helper_builder_all_url(pipe, **kwargs):
    """
    Helper function that provides logic for handling full LPIS Pipeline using URL input.
    :param pipe: Pipeline instance.
    :param kwargs: key word arguments provided by parent function.
    """
    config_path = os.path.join('cfg', 'config.yaml')
    configfile = load_config_from_path(path=config_path, country=kwargs['country'])
    graph_uri = kwargs['graph_uri']
    url = kwargs['url_input']
    if kwargs['graph_per_dump']:
        if kwargs['reload_graph']:
            lpis_full_pipeline_url(pipe=pipe, url=url, output_dir=kwargs['output'], country_config=configfile,
                                   graph_uri=graph_uri, gpd=True, rg=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        else:
            lpis_full_pipeline_url(pipe=pipe, url=url, output_dir=kwargs['output'],
                                   country_config=configfile, graph_uri=graph_uri, gpd=True, rg=False)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
    else:
        if kwargs['reload_graph']:
            lpis_full_pipeline_url(pipe=pipe, url=url, output_dir=kwargs['output'],
                                   country_config=configfile, graph_uri=graph_uri, gpd=False, rg=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        else:
            lpis_full_pipeline_url(pipe=pipe, url=url, output_dir=kwargs['output'],
                                   country_config=configfile, graph_uri=graph_uri, gpd=False, rg=False)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])


def helper_builder_all_dir(pipe, **kwargs):
    """
    Helper function that provides logic for handling full LPIS Pipeline using DIR input.
    :param pipe: Pipeline instance.
    :param kwargs: key word arguments provided by parent function.
    """
    config_path = os.path.join('cfg', 'config.yaml')
    configfile = load_config_from_path(path=config_path, country=kwargs['country'])
    graph_uri = kwargs['graph_uri']
    dir_input = kwargs['dir_input']
    if kwargs['graph_per_dump']:
        if kwargs['reload_graph']:
            lpis_full_pipeline_dir(pipe=pipe, data_dir=dir_input, output_dir=kwargs['output'],
                                   country_config=configfile, graph_uri=graph_uri, gpd=True, rg=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        else:
            lpis_full_pipeline_dir(pipe=pipe, data_dir=dir_input, output_dir=kwargs['output'],
                                   country_config=configfile, graph_uri=graph_uri, gpd=True, rg=False)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
    else:
        if kwargs['reload_graph']:
            lpis_full_pipeline_dir(pipe=pipe, data_dir=dir_input, output_dir=kwargs['output'],
                                   country_config=configfile, graph_uri=graph_uri, gpd=False, rg=True)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])
        else:
            lpis_full_pipeline_dir(pipe=pipe, data_dir=dir_input, output_dir=kwargs['output'],
                                   country_config=configfile, graph_uri=graph_uri, gpd=False, rg=False)
            if kwargs['clean']:
                clean_scripts_directory(results_dir=kwargs['output'])


def helper_builder_all_none(pipe, **kwargs):
    """
    Helper function that provides logic for handling full LPIS Pipeline in absence of specified input.
    :param pipe: Pipeline instance.
    :param kwargs: key word arguments provided by parent function.
    :returns nothing. Serves as an exit.
    """
    config_path = os.path.join('cfg', 'config.yaml')
    configfile = load_config_from_path(path=config_path, country=kwargs['country'])
    graph_uri = kwargs['graph_uri']
    for folder in os.listdir():
        if folder.startswith('lpis'):
            dir_input = folder
            if kwargs['graph_per_dump']:
                if kwargs['reload_graph']:
                    lpis_full_pipeline_dir(pipe=pipe, data_dir=dir_input, output_dir=kwargs['output'],
                                           country_config=configfile, graph_uri=graph_uri, gpd=True, rg=True)
                    if kwargs['clean']:
                        clean_scripts_directory(results_dir=kwargs['output'])
                        return
                    return
                else:
                    lpis_full_pipeline_dir(pipe=pipe, data_dir=dir_input, output_dir=kwargs['output'],
                                           country_config=configfile, graph_uri=graph_uri, gpd=True, rg=False)
                    if kwargs['clean']:
                        clean_scripts_directory(results_dir=kwargs['output'])
                        return
                    return
            else:
                if kwargs['reload_graph']:
                    lpis_full_pipeline_dir(pipe=pipe, data_dir=dir_input, output_dir=kwargs['output'],
                                           country_config=configfile, graph_uri=graph_uri, gpd=False, rg=True)
                    if kwargs['clean']:
                        clean_scripts_directory(results_dir=kwargs['output'])
                        return
                    return
                else:
                    lpis_full_pipeline_dir(pipe=pipe, data_dir=dir_input, output_dir=kwargs['output'],
                                           country_config=configfile, graph_uri=graph_uri, gpd=False, rg=False)
                    if kwargs['clean']:
                        clean_scripts_directory(results_dir=kwargs['output'])
                        return
                    return
    print_warning()


def helper_builder_fetch(pipe, **kwargs):
    """
    Helper function that provided logic for handling fetch stage of the LPIS Pipeline.
    :param pipe: Pipeline instance.
    :param kwargs: key word arguments provided by parent function.
    """
    url = kwargs['url_input']
    lpis_fetch_pipeline_url(pipe=pipe, url=url, output_dir=kwargs['output'])


def helper_builder_mapping(pipe, **kwargs):
    """
    Helper function that provided logic for handling mapping stage of the LPIS Pipeline.
    :param pipe: Pipeline instance.
    :param kwargs: key word arguments provided by parent function.
    :returns nothing. Serves as an exit.
    """
    config_path = os.path.join('cfg', 'config.yaml')
    configfile = load_config_from_path(path=config_path, country=kwargs['country'])
    if kwargs['url_input']:
        url = kwargs['url_input']
        lpis_mapping_pipeline_url(pipe=pipe, url=url, country_config=configfile, output_dir=kwargs['output'])
    elif kwargs['dir_input']:
        dir_input = kwargs['dir_input']
        lpis_mapping_pipeline_dir(pipe=pipe, country_config=configfile, data_dir=dir_input, output_dir=kwargs['output'])
    else:
        for folder in os.listdir():
            if folder.startswith('lpis'):
                dir_input = folder
                lpis_mapping_pipeline_dir(pipe=pipe, country_config=configfile, data_dir=dir_input,
                                          output_dir=kwargs['output'])
                return
        print_warning()


def helper_builder_transform(pipe, **kwargs):
    """
    Helper function that provided logic for handling transforming stage of the LPIS Pipeline.
    :param pipe: Pipeline instance.
    :param kwargs: key word arguments provided by parent function.
    :returns nothing. Serves as an exit.
    """
    config_path = os.path.join('cfg', 'config.yaml')
    configfile = load_config_from_path(path=config_path, country=kwargs['country'])
    if kwargs['url_input']:
        url = kwargs['url_input']
        lpis_transformer_pipeline_url(pipe=pipe, url=url, country_config=configfile, output_dir=kwargs['output'])
    elif kwargs['dir_input']:
        dir_input = kwargs['dir_input']
        lpis_transformer_pipeline_dir(pipe=pipe, country_config=configfile, data_dir=dir_input,
                                      output_dir=kwargs['output'])
    else:
        for folder in os.listdir():
            if folder.startswith('lpis'):
                dir_input = folder
                lpis_transformer_pipeline_dir(pipe=pipe, country_config=configfile, data_dir=dir_input,
                                              output_dir=kwargs['output'])
                return
        print_warning()


def helper_builder_postprocess(pipe, **kwargs):
    """
    Helper function that provided logic for handling post-processing stage of the LPIS Pipeline.
    :param pipe: Pipeline instance.
    :param kwargs: key word arguments provided by parent function.
    :returns nothing. Serves as an exit.
    """
    config_path = os.path.join('cfg', 'config.yaml')
    configfile = load_config_from_path(path=config_path, country=kwargs['country'])
    if kwargs['url_input']:
        url = kwargs['url_input']
        lpis_postprocess_pipeline_url(pipe=pipe, url=url, country_config=configfile, output_dir=kwargs['output'])
    elif kwargs['dir_input']:
        dir_input = kwargs['dir_input']
        lpis_postprocess_pipeline_dir(pipe=pipe, country_config=configfile, data_dir=dir_input,
                                      output_dir=kwargs['output'])
    else:
        for folder in os.listdir():
            if folder.startswith('lpis'):
                dir_input = folder
                lpis_postprocess_pipeline_dir(pipe=pipe, country_config=configfile, data_dir=dir_input,
                                              output_dir=kwargs['output'])
                return
        print_warning()


def lpis_pipeline_builder(**kwargs):
    """
    Function that builds LPIS Pipeline based on the arguments specified by the user.
    """
    print('########## Initializing the LPIS Pipeline...')
    pipe = pipeline.Pipeline()
    cleaning_preexisting_dir()
    if kwargs['stage'] == 'all':
        helper_builder_all(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'mapping':
        helper_builder_mapping(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'transform':
        helper_builder_transform(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'postprocess':
        helper_builder_postprocess(pipe=pipe, **kwargs)
    elif kwargs['stage'] == 'fetch':
        helper_builder_fetch(pipe=pipe, **kwargs)


def lpis_full_pipeline_url(pipe, url, output_dir, country_config, graph_uri, gpd=False, rg=False):
    """
    Helper function that runs full LPIS Pipeline based on the url input.
    :param pipe: Pipeline object.
    :param url: str -> URL to the file containing data.
    :param output_dir: str -> name for the output directory.
    :param country_config: str -> config file for specific country.
    :param graph_uri: str -> graph's URI.
    :param gpd: boolean -> stands for reload graph. If true the graph will be reloaded.
    :param rg: boolean -> stands for graph per dump. If true graph_uri argument will be used as a prefix for
    constructing graph's URI.
    """
    lpis_pipeline.building_lpis_fetch(pipe=pipe, url=url, output_dir=output_dir)
    lpis_pipeline.building_lpis_mappings(pipe=pipe, configfile=country_config, output_dir=output_dir)
    lpis_pipeline.building_lpis_transform(pipe=pipe, output_dir=output_dir)
    lpis_pipeline.building_lpis_postprocess(pipe=pipe, configfile=country_config, output_dir=output_dir)
    lpis_pipeline.building_lpis_loader(pipe=pipe, configfile='config.yaml', uri=graph_uri,
                                       remove_target_graph=rg, graph_per_dump=gpd, output_dir=output_dir)
    print('INFO: Running the whole Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def lpis_full_pipeline_dir(pipe, output_dir, country_config, graph_uri, gpd=False, rg=False, data_dir=None):
    """
    Helper function that runs full LPIS Pipeline based on the dir input.
    :param pipe: Pipeline object.
    :param output_dir: str -> name for the output directory.
    :param country_config: str -> config file for specific country.
    :param graph_uri: str -> graph's URI.
    :param gpd: boolean -> stands for reload graph. If true the graph will be reloaded.
    :param rg: boolean -> stands for graph per dump. If true graph_uri argument will be used as a prefix for
    constructing graph's URI.
    :param data_dir: str -> folder containing data.
    """
    lpis_pipeline.building_lpis_mappings(pipe=pipe, configfile=country_config, data_dir=data_dir, output_dir=output_dir)
    lpis_pipeline.building_lpis_transform(pipe=pipe, data_dir=data_dir, output_dir=output_dir)
    lpis_pipeline.building_lpis_postprocess(pipe=pipe, configfile=country_config, output_dir=output_dir)
    lpis_pipeline.building_lpis_loader(pipe=pipe, configfile='config.yaml', uri=graph_uri, output_dir=output_dir,
                                       remove_target_graph=rg, graph_per_dump=gpd)
    print('INFO: Running the whole Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def lpis_mapping_pipeline_dir(pipe, output_dir, country_config, data_dir=None):
    """
    Helper function that runs mapping stage of the LPIS Pipeline based on the DIR input.
    :param pipe: Pipeline object.
    :param output_dir: str -> name for the output directory.
    :param country_config: str -> config filename.
    :param data_dir: str -> folder containing data.
    """
    lpis_pipeline.building_lpis_mappings(pipe=pipe, configfile=country_config, data_dir=data_dir, output_dir=output_dir)
    print('INFO: Running mapping stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def lpis_mapping_pipeline_url(pipe, output_dir, url, country_config):
    """
    Helper function that runs mapping stage of the LPIS Pipeline based on the URL input.
    :param pipe: Pipeline object.
    :param output_dir: str -> name for the output directory.
    :param url: str -> URL to the file containing data.
    :param country_config: str -> config file for specific country.
    """
    lpis_pipeline.building_lpis_fetch(pipe=pipe, url=url, output_dir=output_dir)
    lpis_pipeline.building_lpis_mappings(pipe=pipe, configfile=country_config, output_dir=output_dir)
    print('INFO: Running mapping stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def lpis_transformer_pipeline_url(pipe, output_dir, country_config, url):
    """
    Helper function that runs transforming stage of the LPIS Pipeline based on URL input.
    :param pipe: Pipeline object.
    :param output_dir: str -> name for the output directory.
    :param country_config: str -> config file for specific country.
    :param url: str -> URL to the file containing data.
    """
    lpis_pipeline.building_lpis_fetch(pipe=pipe, url=url, output_dir=output_dir)
    lpis_pipeline.building_lpis_mappings(pipe=pipe, configfile=country_config, output_dir=output_dir)
    lpis_pipeline.building_lpis_transform(pipe=pipe, output_dir=output_dir)
    print('INFO: Running transforming stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def lpis_transformer_pipeline_dir(pipe, output_dir, country_config, data_dir=None):
    """
    Helper function that runs transforming stage of the LPIS Pipeline based on DIR input.
    :param pipe: Pipeline object.
    :param output_dir: str -> name for the output directory.
    :param country_config: str -> config file for specific country.
    :param data_dir: str -> data directory.
    """
    lpis_pipeline.building_lpis_mappings(pipe=pipe, configfile=country_config, data_dir=data_dir, output_dir=output_dir)
    lpis_pipeline.building_lpis_transform(pipe=pipe, data_dir=data_dir, output_dir=output_dir)
    print('INFO: Running transforming stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def lpis_postprocess_pipeline_url(pipe, output_dir, country_config, url):
    """
    Helper function that runs transforming stage of the LPIS Pipeline based on URL input.
    :param pipe: Pipeline object.
    :param output_dir: str -> name for the output directory.
    :param country_config: str -> config file for specific country.
    :param url: URL to the file containing data.
    """
    lpis_pipeline.building_lpis_fetch(pipe=pipe, url=url, output_dir=output_dir)
    lpis_pipeline.building_lpis_mappings(pipe=pipe, configfile=country_config, output_dir=output_dir)
    lpis_pipeline.building_lpis_transform(pipe=pipe, output_dir=output_dir)
    lpis_pipeline.building_lpis_postprocess(pipe=pipe, configfile=country_config, output_dir=output_dir)
    print('INFO: Running transforming stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def lpis_postprocess_pipeline_dir(pipe, output_dir, country_config, data_dir=None):
    """
    Helper function that runs transforming stage of the LPIS Pipeline based on DIR input.
    :param pipe: Pipeline object.
    :param output_dir: str -> name for the output directory.
    :param country_config: str -> config file for specific country.
    :param data_dir: str -> data directory.
    """
    lpis_pipeline.building_lpis_mappings(pipe=pipe, configfile=country_config, data_dir=data_dir, output_dir=output_dir)
    lpis_pipeline.building_lpis_transform(pipe=pipe, data_dir=data_dir, output_dir=output_dir)
    lpis_pipeline.building_lpis_postprocess(pipe=pipe, configfile=country_config, output_dir=output_dir)
    print('INFO: Running post-processing stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')


def lpis_fetch_pipeline_url(pipe, output_dir, url):
    """
    Helper function that runs fetching stage of the LPIS Pipeline.
    :param pipe: Pipeline object.
    :param output_dir: str -> name for the output directory.
    :param url: str -> URL to the file containing data.
    """
    lpis_pipeline.building_lpis_fetch(pipe=pipe, url=url, output_dir=output_dir)
    print('INFO: Running fetching stage of the Pipeline!')
    pipe.run_pipeline()
    print('*************************************************************')
    print('Done!')
